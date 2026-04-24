from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage

from agents.base import Agent, AgentCapability, AgentRequest, AgentResponse
from agents._react import REACT_CONFIDENCE, build_user_message, extract_citations, extract_trace, final_answer
from .tools import pubmed_tool

_AGENT_NAME = AgentCapability.RESEARCH.value
_SKILLS_DIR = Path(__file__).parent / "skills"

_SYSTEM_HEADER = """\
You are a medical research expert specializing in evidence-based medicine.
Your role is to find, evaluate, and grade clinical evidence to support clinical decision-making.

Always search PubMed before making any evidence-based claim.
Grade every claim using the evidence frameworks provided below.

---

"""


def _load_skills() -> str:
    parts = [Path(p).read_text(encoding="utf-8") for p in sorted(_SKILLS_DIR.glob("*.md"))]
    return "\n\n---\n\n".join(parts)


def make_research_expert(llm: BaseChatModel) -> Agent:
    system_prompt = _SYSTEM_HEADER + _load_skills()
    react_graph = create_agent(model=llm, tools=[pubmed_tool], system_prompt=system_prompt)

    async def _call(request: AgentRequest) -> AgentResponse:
        result: dict[str, Any] = await react_graph.ainvoke(
            {"messages": [HumanMessage(content=build_user_message(request))]}
        )
        messages = result["messages"]
        return AgentResponse(
            answer=final_answer(messages),
            citations=extract_citations(messages),
            confidence=REACT_CONFIDENCE,
            reasoning_trace=extract_trace(messages, _AGENT_NAME),
            capability=AgentCapability.RESEARCH,
        )

    return _call  # type: ignore[return-value]
