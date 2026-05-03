from __future__ import annotations

from agents._stub import make_stub_agent
from agents.base import AgentCapability

# TODO: switch to AgentCapability.PHARMACEUTICAL when that enum value is added.
# Until then, the closest existing slot is DRUG_DOSING.
pharmaceutical_expert = make_stub_agent(AgentCapability.DRUG_DOSING)
