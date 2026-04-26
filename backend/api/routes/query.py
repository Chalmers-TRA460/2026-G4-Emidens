from __future__ import annotations

import json
from typing import Any, AsyncIterator

from fastapi import APIRouter
from fastapi.requests import Request
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from agents import AgentCapability, AgentRequest, AgentResponse
from graph import NODE_ORCHESTRATOR, initial_state

router = APIRouter()

_EXPERT_NODES = {cap.value for cap in AgentCapability}


class QueryRequest(BaseModel):
    query: str


def _emit(event: str, data: Any) -> dict[str, str]:
    return {"event": event, "data": json.dumps(data)}


def _serialize_response(r: AgentResponse) -> dict[str, Any]:
    return {
        "capability": r.capability.value,
        "answer":     r.answer,
        "confidence": r.confidence,
        "escalate":   r.escalate,
        "citations":  [c.model_dump() for c in r.citations],
        "trace": [
            {"agent": s.agent, "message": s.message, "time": s.formatted_time}
            for s in r.reasoning_trace
        ],
    }


async def _stream(graph: CompiledStateGraph, request: AgentRequest) -> AsyncIterator[dict[str, str]]:
    async for ev in graph.astream_events(initial_state(request), version="v2"):
        if ev["event"] != "on_chain_end":
            continue

        name = ev.get("name", "")
        output = ev.get("data", {}).get("output") or {}

        if name == NODE_ORCHESTRATOR:
            if "routing" in output:
                routing = output["routing"]
                yield _emit("routing", {
                    "assignments": [
                        {"capability": a.capability.value, "task": a.task}
                        for a in routing.assignments
                    ],
                    "reasoning": routing.reasoning,
                })

            elif (final := output.get("final_response")) is not None:
                yield _emit("final", _serialize_response(final))

        elif name in _EXPERT_NODES:
            for r in output.get("responses", []):
                yield _emit("expert_response", _serialize_response(r))

    yield _emit("done", {})


@router.post("/query/stream")
async def query_stream(body: QueryRequest, request: Request) -> EventSourceResponse:
    agent_request = AgentRequest(query=body.query)
    return EventSourceResponse(_stream(request.app.state.graph, agent_request))
