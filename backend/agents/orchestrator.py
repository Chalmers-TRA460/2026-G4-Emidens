from __future__ import annotations

import asyncio
import warnings
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel

from .base import Agent, AgentCapability, AgentRequest, AgentResponse, Citation

ESCALATE_CONFIDENCE_THRESHOLD = 0.6

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

SYNTHESIS_PROMPT = """\
You are a clinical synthesizer. Merge the following expert responses into a single coherent answer.

Original query: {query}

Expert responses:
{responses}

Rules:
- Attribute every claim to its source citations
- If experts contradict each other, flag it explicitly in the answer
- Set escalate=True if any expert escalated or if overall confidence is below {ESCALATE_CONFIDENCE_THRESHOLD}
- Include all citations from all experts
- Be concise — this answer goes directly to a clinician under time pressure
"""


class RoutingDecision(BaseModel):
    experts: list[AgentCapability]
    reasoning: str


class _SynthesisOutput(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: float
    reasoning_trace: list[str]
    escalate: bool = False


class Orchestrator:
    def __init__(
        self,
        experts: dict[AgentCapability, Agent],
        llm: BaseChatModel,
    ):
        self.experts = experts
        self.llm = llm

    async def run(self, request: AgentRequest) -> AgentResponse:
        routing = await self._route(request)

        active, unregistered = [], []
        for cap in routing.experts:
            (active if cap in self.experts else unregistered).append(cap)
        if unregistered:
            warnings.warn(f"Routing requested unregistered experts: {unregistered}", stacklevel=2)
        responses: list[AgentResponse] = await asyncio.gather(
            *[self.experts[cap](request) for cap in active]
        )

        return await self._synthesize(request, responses, routing)

    async def _route(self, request: AgentRequest) -> RoutingDecision:
        prompt = ROUTING_PROMPT.format(
            experts=_EXPERTS_TEXT,
            query=request.query,
            context=request.clinical_context.model_dump(),
            constraints=request.constraints,
        )
        return await self.llm.with_structured_output(RoutingDecision).ainvoke(prompt)

    async def _synthesize(
        self,
        request: AgentRequest,
        responses: list[AgentResponse],
        routing: RoutingDecision,
    ) -> AgentResponse:
        responses_text = "\n\n".join(
            f"[{r.capability.value}] confidence={r.confidence:.2f}\n{r.answer}"
            for r in responses
        )
        prompt = SYNTHESIS_PROMPT.format(
            query=request.query,
            responses=responses_text,
            ESCALATE_CONFIDENCE_THRESHOLD=ESCALATE_CONFIDENCE_THRESHOLD,
        )

        result = await self.llm.with_structured_output(_SynthesisOutput).ainvoke(prompt)

        full_trace = [
            f"Routing decision: {[e.value for e in routing.experts]} — {routing.reasoning}",
            *[step for r in responses for step in r.reasoning_trace],
            *result.reasoning_trace,
        ]

        expert_escalated = False
        primary_cap = routing.experts[0] if routing.experts else AgentCapability.CARDIOLOGY
        best_confidence = -1.0
        for r in responses:
            if r.escalate:
                expert_escalated = True
            if r.confidence > best_confidence:
                best_confidence = r.confidence
                primary_cap = r.capability

        return AgentResponse(
            answer=result.answer,
            citations=result.citations,
            confidence=result.confidence,
            reasoning_trace=full_trace,
            escalate=result.escalate or expert_escalated or result.confidence < ESCALATE_CONFIDENCE_THRESHOLD,
            capability=primary_cap,
        )
