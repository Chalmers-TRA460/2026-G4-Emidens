from __future__ import annotations

from enum import Enum
from itertools import chain
from typing import cast

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field

from .base import AgentCapability, AgentRequest, AgentResponse, Citation, TraceStep

MAX_ITERATIONS = 2
ESCALATE_CONFIDENCE_THRESHOLD = 0.6
_ORCHESTRATOR_AGENT = "orchestrator"

_EXPERTS_TEXT = "\n".join(
    f"- {cap.value}: {cap.description}" for cap in AgentCapability
)

ROUTING_PROMPT = """\
You are a clinical query router. Given a clinical question, select the minimum set of expert agents needed to answer it accurately.

Available experts:
{experts}

Query: {query}
Clinical context: {context}
Constraints: {constraints}

Prefer fewer experts unless multiple domains are clearly required. Explain your routing decision.
"""

EVALUATE_PROMPT = """\
You are a clinical quality evaluator. Review the following expert responses to a clinical query.

Original query: {query}

Expert responses:
{responses}

Decide whether the responses are sufficient to produce a complete, safe clinical answer, or whether specific experts need to be re-prompted due to critical gaps, low confidence, or contradictions.

Only re-prompt if genuinely necessary — unnecessary iterations add latency in a time-critical setting.
"""

SYNTHESIS_PROMPT = """\
You are a clinical synthesizer. Merge the following expert responses into a single coherent answer.

Original query: {query}

Expert responses:
{responses}

Rules:
- Attribute every claim to its source citations
- If experts contradict each other, flag it explicitly in the answer
- Set escalate=True if any expert escalated or if overall confidence is below {threshold}
- Include all citations from all experts
- Be concise — this answer goes directly to a clinician under time pressure
"""


class EvaluationAction(str, Enum):
    SYNTHESIZE = "synthesize"
    RE_PROMPT  = "re_prompt"


class RoutingDecision(BaseModel):
    experts:   list[AgentCapability] = Field(min_length=1)
    reasoning: str


class EvaluationDecision(BaseModel):
    action:         EvaluationAction
    re_prompt_caps: list[AgentCapability] = Field(default_factory=list)
    reasoning:      str


class _SynthesisOutput(BaseModel):
    answer:          str
    citations:       list[Citation]
    confidence:      float
    reasoning_trace: list[str]
    escalate:        bool = False


def _format_responses(responses: list[AgentResponse]) -> str:
    return "\n\n".join(
        f"[{r.capability.value}] confidence={r.confidence:.2f}\n{r.answer}"
        for r in responses
    )


class Orchestrator:
    def __init__(self, llm: BaseChatModel) -> None:
        self.llm = llm

    async def route(self, request: AgentRequest) -> RoutingDecision:
        prompt = ROUTING_PROMPT.format(
            experts=_EXPERTS_TEXT,
            query=request.query,
            context=request.clinical_context.model_dump(),
            constraints=request.constraints,
        )
        return cast(RoutingDecision, await self.llm.with_structured_output(RoutingDecision).ainvoke(prompt))

    async def evaluate(
        self,
        request: AgentRequest,
        responses: list[AgentResponse],
    ) -> EvaluationDecision:
        prompt = EVALUATE_PROMPT.format(
            query=request.query,
            responses=_format_responses(responses),
        )
        return cast(EvaluationDecision, await self.llm.with_structured_output(EvaluationDecision).ainvoke(prompt))

    async def synthesize(
        self,
        request:   AgentRequest,
        responses: list[AgentResponse],
        routing:   RoutingDecision,
    ) -> AgentResponse:
        prompt = SYNTHESIS_PROMPT.format(
            query=request.query,
            responses=_format_responses(responses),
            threshold=ESCALATE_CONFIDENCE_THRESHOLD,
        )
        result = cast(_SynthesisOutput, await self.llm.with_structured_output(_SynthesisOutput).ainvoke(prompt))

        full_trace: list[TraceStep] = [
            TraceStep(agent=_ORCHESTRATOR_AGENT, message=f"Routing: {[e.value for e in routing.experts]} — {routing.reasoning}"),
            *chain.from_iterable(r.reasoning_trace for r in responses),
            *TraceStep.from_messages(_ORCHESTRATOR_AGENT, result.reasoning_trace),
        ]

        expert_escalated = any(r.escalate for r in responses)
        fallback_cap = routing.experts[0] if routing.experts else AgentCapability.CARDIOLOGY
        primary_cap = max(responses, key=lambda r: r.confidence).capability if responses else fallback_cap

        return AgentResponse(
            answer=result.answer,
            citations=result.citations,
            confidence=result.confidence,
            reasoning_trace=full_trace,
            escalate=result.escalate or expert_escalated or result.confidence < ESCALATE_CONFIDENCE_THRESHOLD,
            capability=primary_cap,
        )
