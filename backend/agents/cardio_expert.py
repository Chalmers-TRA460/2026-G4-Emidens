from __future__ import annotations

from ._stub import make_stub_agent
from .base import AgentCapability

cardio_expert = make_stub_agent(AgentCapability.CARDIOLOGY)
