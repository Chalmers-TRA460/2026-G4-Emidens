from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from .base import Agent, AgentCapability
from ._stub import make_stub_agent
from .research import make_research_expert


def make_experts(llm: BaseChatModel) -> dict[AgentCapability, Agent]:
    return {
        AgentCapability.CARDIOLOGY:  make_stub_agent(AgentCapability.CARDIOLOGY),
        AgentCapability.RESEARCH:    make_research_expert(llm),
        AgentCapability.REGULATORY:  make_stub_agent(AgentCapability.REGULATORY),
        AgentCapability.DRUG_DOSING: make_stub_agent(AgentCapability.DRUG_DOSING),
    }
