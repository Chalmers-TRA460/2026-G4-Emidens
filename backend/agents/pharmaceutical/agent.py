from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage

from agents.base import Agent, AgentCapability, AgentRequest, AgentResponse
from agents._react import (
    build_user_message,
    extract_citations,
    extract_requested_inputs,
    extract_trace,
    final_answer,
)
from agents.confidence import pharmaceutical_confidence

from .tools import REQUEST_INPUT_TOOL_NAME, fass_search, request_clinical_input

_AGENT_NAME = "pharmaceutical"
_SKILLS_DIR = Path(__file__).parent / "skills"

_CAPABILITY = AgentCapability.PHARMACEUTICAL

_SYSTEM_HEADER = """\
You are a pharmaceutical expert supporting a clinician at the point of care.

For a drug-related query, your job is to surface, in this order:
1. Dosing — recommended dose for the indication, the inputs needed to choose it, and which inputs are missing from the clinical context.
2. Adverse effects — ranked by clinical relevance to the patient context, with serious effects always surfaced first.
3. Interactions — drugs and conditions that contraindicate, modify, or require monitoring of the regimen.

Always look up the drug via your tools before stating any clinical fact. Never guess values to fill missing patient inputs.

Using `fass_search` (your only FASS tool):
- It is a semantic-search RAG endpoint over Swedish FASS labels, not a browseable SPC. You cannot navigate to a section directly — you query, you get the top-k most relevant label chunks back.
- Phrase queries specifically, combining drug + topic (in Swedish where possible): "metoprolol dosering hjärtsvikt NYHA III", "apixaban interaktion NSAID", "amiodaron biverkningar lunga". A bare drug name will return shallow, unfocused chunks.
- Each result is tagged with `lakemedel`, `substans`, `section` (e.g. "4.2 Dosering och administreringssätt"), and `atc_code`. Cite these tags when you reference a fact — e.g. "FASS, Metoprolol Teva, avsnitt 4.2". Do NOT fabricate fass.se URLs; the tool does not return links.
- If the skills tell you to attach a FASS link or quote a section you have not retrieved, ignore that instruction — quote only from chunks `fass_search` actually returned, and re-query if you need a different section.

If a clinical input is required to answer safely (e.g. weight for a weight-based dose, renal function for a renally-cleared drug) and it is missing from the clinical context, call the `request_clinical_input` tool with the specific fields you need before producing a recommendation. After the tool returns, end your turn with a short message naming what you need and why — do not guess values, and do not produce a dosing recommendation that depends on the missing inputs.

If the user message lists fields under "Intentionally skipped by clinician", treat those as a deliberate decision: do NOT call `request_clinical_input` for them, and do not re-request them in your final message. Instead, produce a best-effort answer that (a) names the safety gap each skipped field creates, (b) gives the most conservative reasonable guidance you can without that input (e.g. standard adult dosing when weight is skipped, the most cautious renal adjustment when renal status is skipped), and (c) explicitly tells the clinician what would change if the missing data were available.

---

"""


def _load_skills() -> str:
    parts = [Path(p).read_text(encoding="utf-8") for p in sorted(_SKILLS_DIR.glob("*.md"))]
    return "\n\n---\n\n".join(parts)


def build_pharmaceutical_graph(llm: BaseChatModel):
    """Returns the raw ReAct graph used by the expert. Exposed so the dev
    backdoor route in `api/routes/dev.py` can stream tool events live;
    the orchestrator path uses `make_pharmaceutical_expert` instead."""
    system_prompt = _SYSTEM_HEADER + _load_skills()
    return create_agent(
        model=llm,
        tools=[fass_search, request_clinical_input],
        system_prompt=system_prompt,
    )


def make_pharmaceutical_expert(llm: BaseChatModel) -> Agent:
    react_graph = build_pharmaceutical_graph(llm)

    async def _call(request: AgentRequest) -> AgentResponse:
        user_message = build_user_message(request)
        if request.skipped_fields:
            user_message += (
                "\n\nIntentionally skipped by clinician: "
                f"{', '.join(request.skipped_fields)}. "
                "Do not request these fields again — answer with caveats."
            )
        result: dict[str, Any] = await react_graph.ainvoke(
            {"messages": [HumanMessage(content=user_message)]}
        )
        messages = result["messages"]
        return AgentResponse(
            answer=final_answer(messages),
            citations=extract_citations(messages),
            confidence=pharmaceutical_confidence(messages, request),
            reasoning_trace=extract_trace(messages, _AGENT_NAME),
            capability=_CAPABILITY,
            requested_inputs=extract_requested_inputs(messages, REQUEST_INPUT_TOOL_NAME),
        )

    return _call  # type: ignore[return-value]
