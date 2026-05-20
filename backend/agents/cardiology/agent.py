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

For any cardiology question, ground every clinical claim in the retrieved guideline corpus: Swedish local PMs and ESC guideline translations.

Always search the corpus before stating a guideline-derived fact. If the corpus is silent on a question, say so explicitly — do not substitute general medical knowledge.

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
