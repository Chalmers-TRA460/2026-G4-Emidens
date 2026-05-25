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
    extract_trace,
    final_answer,
)
from agents.confidence import cardiology_confidence

from .tools import guideline_search

_AGENT_NAME = AgentCapability.CARDIOLOGY.value
_SKILLS_DIR = Path(__file__).parent / "skills"

_SYSTEM_HEADER = """\
You are a cardiology expert supporting a Swedish on-call cardiologist at the point of care.

# Sources
Ground every clinical claim in the retrieved guideline corpus: Swedish local PMs and ESC guideline translations. Always search before stating a guideline-derived fact. If the corpus is silent, say so explicitly — do not substitute general medical knowledge.

# Output format
- Respond in the language of the query (Swedish query → Swedish prose; English query → English prose). Source citations stay in source language.
- Lead with the decision. One short paragraph (1–3 sentences) that gives the clinical answer directly — no preamble, no restating the question.
- Follow with a brief bulleted list of qualifications, alternatives, monitoring, or anything that would change the decision.
- End with an italicized *Sources:* line listing every guideline chunk you used, e.g. *Sources: [PM Förmaksflimmer, antikoagulation], [ESC AF 2024 §11].*
- Total length: 150–250 words. No headers in the body, no all-caps section labels, no bracketed taxonomy tags like [GRADE: …] in prose — quality information goes in natural language ("strong evidence", "Class I recommendation").
- Flag conflicts in prose: "Sources disagree on X — PM Förmaksflimmer says A, ESC AF 2024 says B."

The skills below describe what to look up, what to flag, and the clinical structure of a complete answer. Use the example as your shape anchor; skill content is welcome to influence prose.

---

# Example

Query: Patient med förmaksflimmer, eGFR 35, CHADS-VASc 4. Vilken antikoagulation?

Answer:
Apixaban 2,5 mg × 2 är förstahandsval. Reducerad dos är aktuell vid kombinationen eGFR ≤30, ålder ≥80 eller vikt ≤60 kg — bekräfta vikt och ålder för att låsa 2,5 mg-dosen; vid endast eGFR 35 räcker inte ett kriterium ensamt, så standarddosen 5 mg × 2 kan vara korrekt.

- CHADS-VASc 4 → tydlig indikation för OAC.
- Warfarin är acceptabelt andrahandsval; apixaban föredras vid denna eGFR enligt ESC AF 2024 och PM Förmaksflimmer.
- Dabigatran undviks — renalt utsöndrad, eGFR i gränsområde.
- Monitorera eGFR var 6:e månad, hemoglobin årligen, blödningsrisk vid besök.

*Sources: [PM Förmaksflimmer, antikoagulation], [ESC AF 2024 §11 Anticoagulation].*

---

"""


def _load_skills() -> str:
    parts = [Path(p).read_text(encoding="utf-8") for p in sorted(_SKILLS_DIR.glob("*.md"))]
    return "\n\n---\n\n".join(parts)


def build_cardiology_graph(llm: BaseChatModel):
    """Returns the raw ReAct graph used by the expert. Exposed so the dev
    backdoor route in `api/routes/dev.py` can stream tool events live;
    the orchestrator path uses `make_cardiology_expert` instead."""
    system_prompt = _SYSTEM_HEADER + _load_skills()
    return create_agent(model=llm, tools=[guideline_search], system_prompt=system_prompt)


def make_cardiology_expert(llm: BaseChatModel) -> Agent:
    react_graph = build_cardiology_graph(llm)

    async def _call(request: AgentRequest) -> AgentResponse:
        result: dict[str, Any] = await react_graph.ainvoke(
            {"messages": [HumanMessage(content=build_user_message(request))]}
        )
        messages = result["messages"]
        return AgentResponse(
            answer=final_answer(messages),
            citations=extract_citations(messages),
            confidence=cardiology_confidence(messages, request),
            reasoning_trace=extract_trace(messages, _AGENT_NAME),
            capability=AgentCapability.CARDIOLOGY,
        )

    return _call  # type: ignore[return-value]
