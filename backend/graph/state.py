from __future__ import annotations

from typing_extensions import TypedDict

from agents.base import AgentRequest, AgentResponse


class GraphState(TypedDict):
    request:  AgentRequest
    response: AgentResponse | None
