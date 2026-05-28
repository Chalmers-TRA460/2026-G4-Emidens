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

Query: Patient with atrial fibrillation, eGFR 35, CHA₂DS₂-VASc 4. Which anticoagulation?

Answer:
**Apixaban 5 mg twice daily is the preferred first-line treatment.** [ESC AF 2024 §11]

* **Dosing criteria:** A reduced dose (2.5 mg x2) requires at least two of three criteria: eGFR ≤30, age ≥80, weight ≤60 kg; verify age and weight before prescribing. [ESC AF 2024 §11]
* **Indication:** CHA₂DS₂-VASc 4 provides a strong indication for anticoagulation (Class I). [ESC AF 2024 §11]
* **Alternatives:** Warfarin is an acceptable second-line option. [PM Atrial Fibrillation]
* **Contraindications:** Avoid dabigatran due to heavy renal clearance and borderline eGFR. [PM Atrial Fibrillation]
* **Monitoring:** Reassess eGFR every 6 months and haemoglobin annually. [ESC AF 2024 §11]

*Sources: [ESC AF 2024 §11 Anticoagulation], [PM Atrial Fibrillation, anticoagulation].*

---

# Example

Query: Patient with HFrEF 30. Takes SAMBA (SGLT2i, ARNI, MRA, Beta-blocker). Still hypotensive and low CO. Treatment now?

Answer:
**Refer to a specialized heart failure center for advanced therapies and down-titrate BP-lowering GDMT to restore adequate perfusion.** [ESC HF 2021 §10]

* **GDMT Adjustment:** Temporarily reduce or pause ARNI and beta-blockers to manage symptomatic hypotension and tissue hypoperfusion. [ESC HF 2021 §11.3]
* **Device Therapy:** Evaluate for CRT-D or CRT-P if QRS duration is ≥ 130 ms. [ESC HF 2021 §10.2]
* **Advanced Options:** Assess patient candidacy for Mechanical Circulatory Support (LVAD) or heart transplantation. [ESC HF 2021 §10.2]
* **Acute Stabilization:** Consider short-term intravenous inotropic support (e.g., dobutamine, milrinone) to improve cardiac output if end-organ hypoperfusion is present (Class IIb). [ESC HF 2021 §11.3]

⚠ **Warnings:** Routine use of intravenous inotropes is strictly contraindicated due to increased risks of severe arrhythmias and mortality; reserve only for critical low cardiac output syndrome. [ESC HF 2021 §11.3]

*Sources: [ESC HF 2021 §10 Advanced HF], [ESC HF 2021 §11 Acute HF], [ESC HF 2021 §11.3 Inotropes].*

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
