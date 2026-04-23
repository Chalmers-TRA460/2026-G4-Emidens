from __future__ import annotations

from ._stub import make_stub_agent
from .base import AgentCapability

drug_dosing_expert = make_stub_agent(AgentCapability.DRUG_DOSING)
