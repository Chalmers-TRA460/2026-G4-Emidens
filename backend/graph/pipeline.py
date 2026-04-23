from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents.orchestrator import Orchestrator

from .state import GraphState


def _route_after_orchestrator(state: GraphState) -> str:
    if state["response"] and state["response"].escalate:
        return "human_review"
    return END


async def _human_review_node(state: GraphState) -> dict:
    # stub — future: pause graph, surface to clinician, resume with override
    return {}


def build_graph(orchestrator: Orchestrator):
    async def orchestrator_node(state: GraphState) -> dict:
        response = await orchestrator.run(state["request"])
        return {"response": response}

    graph = StateGraph(GraphState)

    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("human_review", _human_review_node)

    graph.add_edge(START, "orchestrator")
    graph.add_conditional_edges(
        "orchestrator",
        _route_after_orchestrator,
        {"human_review": "human_review", END: END},
    )
    graph.add_edge("human_review", END)

    return graph.compile()
