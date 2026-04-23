from __future__ import annotations

from ._stub import make_stub_agent
from .base import AgentCapability

regulatory_expert = make_stub_agent(AgentCapability.REGULATORY)
