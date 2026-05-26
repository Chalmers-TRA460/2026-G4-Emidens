from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage

from agents._react import (
    build_user_message,
    extract_citations,
    extract_requested_inputs,
    extract_trace,
    final_answer,
)
from agents.base import Agent, AgentCapability, AgentRequest, AgentResponse
from agents.confidence import pharmaceutical_confidence

from .tools import (
    REQUEST_INPUT_TOOL_NAME,
    dosage_calculator,
    fass_search,
    request_clinical_input,
)

_AGENT_NAME = "pharmaceutical"
_SKILLS_DIR = Path(__file__).parent / "skills"

_CAPABILITY = AgentCapability.PHARMACEUTICAL

_SYSTEM_HEADER = """\
You are a pharmaceutical expert supporting a clinician at the point of care.

# Job
For a drug-related query, surface in this order:
1. Dosing — recommended dose for the indication, the inputs needed to choose it, and which inputs are missing from the clinical context.
2. Adverse effects — ranked by clinical relevance to the patient context, with serious effects always surfaced first.
3. Interactions — drugs and conditions that contraindicate, modify, or require monitoring of the regimen.

Always look up the drug via your tools before stating any clinical fact. Never guess values to fill missing patient inputs.

# Tools
- `fass_search` — semantic-search RAG over Swedish FASS labels. Not a browseable SPC: you query, you get top-k label chunks. Phrase queries specifically, combining drug + topic in Swedish where possible ("metoprolol dosering hjärtsvikt NYHA III", "apixaban interaktion NSAID", "amiodaron biverkningar lunga"). A bare drug name returns shallow chunks. Each result is tagged with `lakemedel`, `substans`, `section`, and `atc_code` — cite these tags (e.g. "FASS, Metoprolol Teva, avsnitt 4.2") and never fabricate fass.se URLs.
- `request_clinical_input` — call when a critical input (weight, eGFR, etc.) is missing and the answer would be unsafe without it. After calling, end your turn naming what you need and why. Never guess values, and never produce a recommendation that depends on the missing input.
- `dosage_calculator` — deterministic arithmetic. Use for weight-based or mg/kg/h calculations; never hand-roll the math.

If a skill tells you to attach a FASS link or quote a section you have not retrieved, ignore that instruction — quote only from chunks `fass_search` actually returned, and re-query if you need a different section.

# Skipped fields
If the user message lists fields under "Intentionally skipped by clinician", treat those as a deliberate decision: do NOT call `request_clinical_input` for them, and do not re-request them in your final message. Give a best-effort answer that (a) names the safety gap each skipped field creates, (b) gives the most conservative reasonable guidance you can without it (e.g. standard adult dosing when weight is skipped, the most cautious renal adjustment when renal status is skipped), and (c) tells the clinician what would change with the missing data.

# Output format
- Respond in the language of the query. Source citations stay in source language.
- Lead with the decision in **bold** — the dose, the contraindication, or the "cannot recommend without X". One or two sentences.
- Follow with brief bulleted lines for: rationale, alternatives, monitoring, interaction caveats. Embed frequency and severity in natural prose ("very common (~20%)", "rare but serious", "contraindicated").
- End with an italicized *Sources:* line.
- Total length: 180–300 words. Polypharmacy or multi-system queries may push the upper end.
- No all-caps section headers, no bracketed taxonomy tags ([ADR: …], [INTERACTION: …]) in prose.
- Flag conflicts: "FASS säger A, Strama säger B — följer Strama eftersom …"

The skills below describe what to look up, what to flag, and the clinical structure of a complete answer. Use the example as your shape anchor; skill content is welcome to influence prose.

---

# Example

Query: Starta metoprolol hos 78-årig kvinna med hjärtsvikt, eGFR 42, redan på verapamil.

Answer:
**Starta inte metoprolol så länge patienten står på verapamil.** Kombinationen non-DHP CCB + betablockerare ger hög risk för bradykardi, AV-block och akut dekompensation — byt verapamil till amlodipin först, därefter starta metoprolol.

- **Efter byte:** metoprololsuccinat 12,5 mg × 1, titrera var 2:a vecka mot måldos 200 mg/dygn eller maximalt tolererat. Låg startdos motiveras av ålder 78 och hjärtsvikt (start low, go slow).
- **Monitorera:** puls (håll vid <50), blodtryck, vikt, trötthet. eGFR 42 → ingen dosjustering för metoprolol.
- **Vanliga biverkningar att informera om:** trötthet, kalla extremiteter, yrsel vid uppstigande. Allvarlig men ovanlig: bronkospasm hos astmatiker.
- **Övrigt att kolla:** övriga AV-blockerande läkemedel (digoxin, diltiazem), diabetesläkemedel (maskerade hypoglykemisymtom).

*Sources: [FASS Metoprolol Teva, §4.5 Interaktioner], [FASS Metoprolol Teva, §4.2 Dosering], [janusmed metoprolol+verapamil].*

---

"""


def _load_skills() -> str:
    parts = [
        Path(p).read_text(encoding="utf-8") for p in sorted(_SKILLS_DIR.glob("*.md"))
    ]
    return "\n\n---\n\n".join(parts)


def build_pharmaceutical_graph(llm: BaseChatModel):
    """Returns the raw ReAct graph used by the expert. Exposed so the dev
    backdoor route in `api/routes/dev.py` can stream tool events live;
    the orchestrator path uses `make_pharmaceutical_expert` instead."""
    system_prompt = _SYSTEM_HEADER + _load_skills()
    return create_agent(
        model=llm,
        tools=[fass_search, request_clinical_input, dosage_calculator],
        system_prompt=system_prompt,
    )


def make_pharmaceutical_expert(llm: BaseChatModel) -> Agent:
    react_graph = build_pharmaceutical_graph(llm)

    async def _call(request: AgentRequest) -> AgentResponse:
        result: dict[str, Any] = await react_graph.ainvoke(
            {"messages": [HumanMessage(content=build_user_message(request))]}
        )
        messages = result["messages"]
        return AgentResponse(
            answer=final_answer(messages),
            citations=extract_citations(messages),
            confidence=pharmaceutical_confidence(messages, request),
            reasoning_trace=extract_trace(messages, _AGENT_NAME),
            capability=_CAPABILITY,
            requested_inputs=extract_requested_inputs(
                messages, REQUEST_INPUT_TOOL_NAME
            ),
        )

    return _call  # type: ignore[return-value]
