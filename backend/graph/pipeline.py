from __future__ import annotations

from itertools import chain
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Send

from agents.base import Agent, AgentCapability, AgentResponse, TraceStep
from agents.orchestrator import MAX_ITERATIONS, EvaluationAction, Orchestrator

from .state import GraphState

NODE_ORCHESTRATOR = "orchestrator"
_NODE_HUMAN_REVIEW = "human_review"
_NEEDS_INPUT_AGENT = "orchestrator"


def _needs_input_response(responses: list[AgentResponse]) -> AgentResponse | None:
    """If any expert requested clinical inputs, build a final response that
    surfaces the request and skips synthesis."""
    fields: list[str] = []
    seen: set[str] = set()
    for r in responses:
        for field in r.requested_inputs:
            if field not in seen:
                seen.add(field)
                fields.append(field)
    if not fields:
        return None

    requesting_caps = sorted({r.capability.value for r in responses if r.requested_inputs})
    answer = (
        "More patient information is needed before a safe answer can be given. "
        f"Requested by {', '.join(requesting_caps)}: {', '.join(fields)}."
    )
    trace = [
        *chain.from_iterable(r.reasoning_trace for r in responses),
        TraceStep(
            agent=_NEEDS_INPUT_AGENT,
            message=f"Awaiting user input: {', '.join(fields)}",
        ),
    ]
    return AgentResponse(
        answer=answer,
        citations=[],
        confidence=0.0,
        reasoning_trace=trace,
        escalate=False,
        capability=responses[-1].capability,
        requested_inputs=fields,
    )


def _dispatch_or_end(state: GraphState) -> list[Send] | str:
    if state["final_response"] is not None:
        if state["final_response"].escalate:
            return _NODE_HUMAN_REVIEW
        return END
    if not state["pending_dispatch"]:
        return END
    return [
        Send(a.capability.value, {**state, "current_task": a.task})
        for a in state["pending_dispatch"]
    ]


def build_graph(
    orchestrator: Orchestrator,
    experts: dict[AgentCapability, Agent],
) -> CompiledStateGraph:

    async def human_review_node(state: GraphState) -> dict[str, Any]:  # noqa: ARG001
        return {}

    async def orchestrator_node(state: GraphState) -> dict[str, Any]:
        request = state["request"]
        responses = state["responses"]

        if not responses:
            decision = await orchestrator.route(request)
            return {"routing": decision, "pending_dispatch": decision.assignments}

        if (needs_input := _needs_input_response(responses)) is not None:
            return {"final_response": needs_input, "pending_dispatch": []}

        async def _synthesize() -> dict[str, Any]:
            assert state["routing"] is not None
            final = await orchestrator.synthesize(request, responses, state["routing"])
            return {"final_response": final, "pending_dispatch": []}

        if state["iteration"] >= MAX_ITERATIONS:
            return await _synthesize()

        evaluation = await orchestrator.evaluate(request, responses)
        if evaluation.action == EvaluationAction.SYNTHESIZE:
            return await _synthesize()

        return {
            "pending_dispatch": evaluation.re_prompt_assignments,
            "iteration": state["iteration"] + 1,
        }

    graph = StateGraph(GraphState)
    graph.add_node(NODE_ORCHESTRATOR, orchestrator_node)
    graph.add_node(_NODE_HUMAN_REVIEW, human_review_node)

    graph.add_edge(START, NODE_ORCHESTRATOR)
    graph.add_conditional_edges(NODE_ORCHESTRATOR, _dispatch_or_end)
    graph.add_edge(_NODE_HUMAN_REVIEW, END)

    for cap, agent in experts.items():

        async def expert_node(state: GraphState, _agent=agent) -> dict[str, Any]:
            request = state["request"].model_copy(update={"task": state["current_task"]})
            response = await _agent(request)
            return {"responses": [response]}

        graph.add_node(cap.value, expert_node)
        graph.add_edge(cap.value, NODE_ORCHESTRATOR)

    return graph.compile()
