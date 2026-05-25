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
You are a clinical query router. Assign the minimum set of expert agents needed to answer the query. \
For each expert, provide a specific task describing exactly what aspect they should address.

Prefer fewer experts unless multiple domains are clearly required. \
Be specific in each task — the expert will only see their own task, not the others'.

# Example

Query: "Vilken dos av apixaban hos äldre med eGFR 35?"

Good routing:
- pharmaceutical: "Recommend apixaban dose for patient age ≥80 with eGFR 35. \
Address dose-reduction criteria (age, weight, creatinine) and monitoring."

Why this is good: single expert, specific task. Cardiology is not needed — \
the dosing recommendation itself answers the clinical question. Research is \
not needed — apixaban dosing is settled in FASS/janusmed.

Bad routing: cardiology + pharmaceutical + research all assigned. Adds \
latency without changing the answer.

# Inputs

Available experts:
{experts}

Query: {query}
Clinical context: {context}
Constraints: {constraints}
"""

EVALUATE_PROMPT = """\
You are a clinical quality evaluator. Review the following expert responses to a clinical query.

Decide whether the responses are sufficient to produce a complete, safe clinical answer, \
or whether specific experts need re-prompting with refined tasks.

Only re-prompt if genuinely necessary — unnecessary iterations add latency in a time-critical setting. \
For any expert that needs re-prompting, provide a specific refined task addressing the gap.

# Example

If pharmaceutical answered the dosing question completely with sources and confidence >0.7, \
SYNTHESIZE. Do not re-prompt for "more detail" or "additional context" — the synthesis step \
handles polish. Only re-prompt when an expert missed a specific factual gap that the clinician \
explicitly asked about.

# Inputs

Original query: {query}

Expert responses:
{responses}
"""

SYNTHESIS_PROMPT = """\
You are a clinical synthesizer. Merge the following expert responses into a single coherent answer for a clinician under time pressure.

# Rules
- One unified answer, not a stitched-together summary of each expert.
- Lead with the decision in **bold** — one sentence, what the clinician should do or know. No "the experts have analyzed your query" preamble.
- Follow with bullets that integrate findings: dose + monitoring + interactions + evidence in the right order for clinical action, not in expert order.
- Flag conflicts explicitly when experts disagree. Do not paper over them.
- End with an italicized *Sources:* line citing the strongest references from any expert.
- Total length: 120–200 words. Match the query's language. No all-caps section headers, no bracketed taxonomy tags in prose.
- Set escalate=True if any expert escalated, if experts contradict on a safety-critical point, or if overall confidence is below {threshold}.

# Example

Query: 78-årig kvinna, hjärtsvikt EF 28%, vill starta SGLT2-hämmare. Bevisstöd? Dosering? Säker mot pågående furosemid + lisinopril?

Answer:
**Starta empagliflozin 10 mg × 1 oralt.** Stark evidens för minskad mortalitet och HF-hospitalisering i HFrEF oavsett diabetesstatus. Ingen direkt interaktion med furosemid + lisinopril, men additiv volymeffekt kräver justering av furosemid under de första veckorna.

- **Dosering:** 10 mg × 1 oralt, ingen titrering. Ingen njurdosjustering vid eGFR ≥20.
- **Förväntat:** mild eGFR-dipp vid uppstart (5–10 %) — godartad, gå inte ned i dos om <30 % minskning.
- **Monitorera:** eGFR + elektrolyter vid 2 veckor, volymstatus veckovis initialt, blodsocker om diabetes-risk.
- **Säkerhet:** håll vid symtom på euglykemisk DKA (illamående, takypné). Pausa vid akut sjukdom, dehydrering eller fasta.

*Sources: [PMID 31535829 DAPA-HF], [PMID 32865377 EMPEROR-Reduced], [ESC HF 2023, §5], [FASS Jardiance, §4.2].*

# Inputs

Original query: {query}

Expert responses:
{responses}
"""


class EvaluationAction(str, Enum):
    SYNTHESIZE = "synthesize"
    RE_PROMPT  = "re_prompt"


class ExpertAssignment(BaseModel):
    capability: AgentCapability
    task:       str


class RoutingDecision(BaseModel):
    assignments: list[ExpertAssignment] = Field(min_length=1)
    reasoning:   str


class EvaluationDecision(BaseModel):
    action:              EvaluationAction
    re_prompt_assignments: list[ExpertAssignment] = Field(default_factory=list)
    reasoning:           str


class _SynthesisOutput(BaseModel):
    answer:          str
    confidence:      float
    reasoning_trace: list[str]
    escalate:        bool = False


def _format_responses(
    responses: list[AgentResponse],
    tasks: dict[AgentCapability, str] | None = None,
) -> str:
    parts = []
    for r in responses:
        task_line = f"\nTask: {tasks[r.capability]}" if tasks and r.capability in tasks else ""
        parts.append(f"[{r.capability.value}] confidence={r.confidence:.2f}{task_line}\n{r.answer}")
    return "\n\n".join(parts)


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
        tasks = {a.capability: a.task for a in routing.assignments}
        prompt = SYNTHESIS_PROMPT.format(
            query=request.query,
            responses=_format_responses(responses, tasks),
            threshold=ESCALATE_CONFIDENCE_THRESHOLD,
        )
        result = cast(_SynthesisOutput, await self.llm.with_structured_output(_SynthesisOutput).ainvoke(prompt))

        assignment_summary = ", ".join(
            f"{a.capability.value}({a.task!r})" for a in routing.assignments
        )
        full_trace: list[TraceStep] = [
            TraceStep(agent=_ORCHESTRATOR_AGENT, message=f"Routing: {assignment_summary} — {routing.reasoning}"),
            *chain.from_iterable(r.reasoning_trace for r in responses),
            *TraceStep.from_messages(_ORCHESTRATOR_AGENT, result.reasoning_trace),
        ]

        expert_escalated = any(r.escalate for r in responses)
        fallback_cap = routing.assignments[0].capability if routing.assignments else AgentCapability.CARDIOLOGY
        primary_cap = max(responses, key=lambda r: r.confidence).capability if responses else fallback_cap
        all_citations: list[Citation] = list(chain.from_iterable(r.citations for r in responses))

        return AgentResponse(
            answer=result.answer,
            citations=all_citations,
            confidence=result.confidence,
            reasoning_trace=full_trace,
            escalate=result.escalate or expert_escalated or result.confidence < ESCALATE_CONFIDENCE_THRESHOLD,
            capability=primary_cap,
        )
