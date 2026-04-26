from __future__ import annotations

import json
from enum import StrEnum
from typing import Any, AsyncIterator

from fastapi import APIRouter
from fastapi.requests import Request
from langchain_core.runnables.schema import StreamEvent
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from agents import AgentCapability, AgentRequest, AgentResponse
from graph import (
    KEY_FINAL_RESPONSE,
    KEY_RESPONSES,
    KEY_ROUTING,
    NODE_ORCHESTRATOR,
    initial_state,
)

router = APIRouter()

_EXPERT_NODES = {cap.value for cap in AgentCapability}


class SSEEvent(StrEnum):
    ROUTING = "routing"
    EXPERT_RESPONSE = "expert_response"
    FINAL = "final"
    DONE = "done"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"


class QueryRequest(BaseModel):
    query: str


def _emit(event: SSEEvent, data: Any) -> dict[str, str]:
    # print("Emitting:", event, "with data:", data)
    return {"event": event, "data": json.dumps(data)}


def _serialize_response(r: AgentResponse) -> dict[str, Any]:
    return {
        "capability": r.capability.value,
        "answer": r.answer,
        "confidence": r.confidence,
        "escalate": r.escalate,
        "citations": [c.model_dump() for c in r.citations],
        "trace": [
            {"agent": s.agent, "message": s.message, "time": s.formatted_time}
            for s in r.reasoning_trace
        ],
    }


async def _stream(
    graph: CompiledStateGraph, request: AgentRequest
) -> AsyncIterator[dict[str, str]]:
    ev: StreamEvent
    async for ev in graph.astream_events(initial_state(request), version="v2"):
        kind = ev["event"]
        name = ev.get("name", "")
        data = ev.get("data", {})

        if kind == "on_tool_start":
            yield _emit(SSEEvent.TOOL_CALL, {"tool": name, "input": data.get("input")})
            continue

        if kind == "on_tool_end":
            output = data.get("output")
            content = getattr(output, "content", output)
            yield _emit(SSEEvent.TOOL_RESULT, {"tool": name, "output": content})
            continue

        if kind != "on_chain_end":
            continue

        output = data.get("output") or {}

        if name == NODE_ORCHESTRATOR:
            if KEY_ROUTING in output:
                routing = output[KEY_ROUTING]
                yield _emit(
                    SSEEvent.ROUTING,
                    {
                        "assignments": [
                            {"capability": a.capability.value, "task": a.task}
                            for a in routing.assignments
                        ],
                        "reasoning": routing.reasoning,
                    },
                )

            elif (final := output.get(KEY_FINAL_RESPONSE)) is not None:
                yield _emit(SSEEvent.FINAL, _serialize_response(final))

        elif name in _EXPERT_NODES:
            for r in output.get(KEY_RESPONSES, []):
                yield _emit(SSEEvent.EXPERT_RESPONSE, _serialize_response(r))

    yield _emit(SSEEvent.DONE, {})


@router.post("/query/stream")
async def query_stream(body: QueryRequest, request: Request) -> EventSourceResponse:
    agent_request = AgentRequest(query=body.query)
    return EventSourceResponse(_stream(request.app.state.graph, agent_request))
