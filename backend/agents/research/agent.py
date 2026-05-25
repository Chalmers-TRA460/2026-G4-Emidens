from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage

from agents.base import Agent, AgentCapability, AgentRequest, AgentResponse
from agents._react import build_user_message, extract_citations, extract_trace, final_answer
from agents.confidence import research_confidence
from .tools import pubmed_tool

_AGENT_NAME = AgentCapability.RESEARCH.value
_SKILLS_DIR = Path(__file__).parent / "skills"

_SYSTEM_HEADER = """\
You are a medical research expert specializing in evidence-based medicine. Your role is to find, evaluate, and grade clinical evidence to support clinical decision-making.

# Tool
- `pubmed_tool` — searches PubMed via NCBI E-utilities. Use short, focused queries of 2–4 key terms ("metoprolol renal impairment", not "metoprolol heart failure renal impairment guidelines RCT"). Returns top-5 with structured abstracts.
- Use `pubmed_tool` at most 5 times per query. If the first 2–3 searches yield enough evidence, stop searching and synthesize — extra calls slow the response and rarely add value.

# Output format
- Respond in the language of the query. Source citations stay in source language.
- Lead with the evidence-based conclusion in one sentence: what the literature shows and how strong the support is ("Strong evidence from two large RCTs shows …", "Limited evidence — one small observational study suggests …").
- Follow with brief bullets for: study designs and effect sizes, quality caveats (heterogeneity, exclusion criteria, follow-up duration), guideline alignment if relevant.
- Embed evidence quality in natural prose ("high-quality RCTs", "underpowered", "consistent across subgroups") — no [GRADE: …] or [Oxford: …] tags in prose.
- End with an italicized *Sources:* line citing PMIDs and any guideline references, e.g. *Sources: [PMID 31535829 DAPA-HF], [PMID 32865377 EMPEROR-Reduced], [ESC HF 2023].*
- Total length: 150–250 words. No headers in the body, no all-caps section labels.
- Flag conflicts: "Trial X showed benefit; trial Y did not — the difference is attributed to …"

The skills below describe what to look up, what to flag, and how to grade evidence. Use the example as your shape anchor; skill content is welcome to influence prose.

---

# Example

Query: Evidence for SGLT2 inhibitors in HFrEF without diabetes?

Answer:
Strong evidence — two large RCTs (DAPA-HF, EMPEROR-Reduced) show clear benefit in HFrEF regardless of diabetes status. Combined HR for CV death or HF hospitalization is ~0.75 (95% CI 0.65–0.86), with the effect consistent in pre-specified non-diabetic subgroups (interaction p > 0.2).

- **DAPA-HF** (n=4744, dapagliflozin 10 mg vs placebo, 18-month follow-up): HR 0.74 for primary composite; benefit in both diabetic and non-diabetic cohorts.
- **EMPEROR-Reduced** (n=3730, empagliflozin 10 mg vs placebo): HR 0.75 for primary composite; consistent across NYHA class.
- **Quality**: high — two well-powered RCTs, consistent direction, plausible mechanism (natriuresis + cardiac efficiency).
- **Caveats**: DAPA-HF excluded eGFR <30, EMPEROR-Reduced <20. Long-term renal-decline data still maturing.
- **Guideline status**: Class I recommendation in ESC HF 2023 for NYHA II–IV HFrEF, independent of diabetes.

*Sources: [PMID 31535829 DAPA-HF], [PMID 32865377 EMPEROR-Reduced], [ESC HF 2023, §5 SGLT2i].*

---

"""


def _load_skills() -> str:
    parts = [Path(p).read_text(encoding="utf-8") for p in sorted(_SKILLS_DIR.glob("*.md"))]
    return "\n\n---\n\n".join(parts)


def build_research_graph(llm: BaseChatModel):
    """Returns the raw ReAct graph used by the expert. Exposed so the dev
    backdoor route in `api/routes/dev.py` can stream tool events live;
    the orchestrator path uses `make_research_expert` instead."""
    system_prompt = _SYSTEM_HEADER + _load_skills()
    return create_agent(model=llm, tools=[pubmed_tool], system_prompt=system_prompt)


def make_research_expert(llm: BaseChatModel) -> Agent:
    react_graph = build_research_graph(llm)

    async def _call(request: AgentRequest) -> AgentResponse:
        result: dict[str, Any] = await react_graph.ainvoke(
            {"messages": [HumanMessage(content=build_user_message(request))]}
        )
        messages = result["messages"]
        return AgentResponse(
            answer=final_answer(messages),
            citations=extract_citations(messages),
            confidence=research_confidence(messages, request),
            reasoning_trace=extract_trace(messages, _AGENT_NAME),
            capability=AgentCapability.RESEARCH,
        )

    return _call  # type: ignore[return-value]
