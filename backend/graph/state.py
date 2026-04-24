from __future__ import annotations

import operator
from typing import Annotated

from typing_extensions import TypedDict

from agents.base import AgentRequest, AgentResponse
from agents.orchestrator import ExpertAssignment, RoutingDecision


class GraphState(TypedDict):
    request:          AgentRequest
    responses:        Annotated[list[AgentResponse], operator.add]
    routing:          RoutingDecision | None
    final_response:   AgentResponse | None
    iteration:        int
    pending_dispatch: list[ExpertAssignment]
    current_task:     str | None


def initial_state(request: AgentRequest) -> GraphState:
    return {
        "request":          request,
        "responses":        [],
        "routing":          None,
        "final_response":   None,
        "iteration":        0,
        "pending_dispatch": [],
        "current_task":     None,
    }
