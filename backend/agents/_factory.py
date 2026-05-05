from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from .base import Agent, AgentCapability
from ._stub import make_stub_agent
from .pharmaceutical import make_pharmaceutical_expert
from .research import make_research_expert


def make_experts(llm: BaseChatModel) -> dict[AgentCapability, Agent]:
    return {
        AgentCapability.CARDIOLOGY:     make_stub_agent(AgentCapability.CARDIOLOGY),
        AgentCapability.RESEARCH:       make_research_expert(llm),
        AgentCapability.PHARMACEUTICAL: make_pharmaceutical_expert(llm),
    }
