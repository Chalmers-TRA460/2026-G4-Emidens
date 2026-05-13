"""Dev-only direct-agent endpoints. Bypass the orchestrator. Useful for iterating
on a single expert without paying the orchestrator's routing/synthesis tax."""

from __future__ import annotations

import json
from typing import Any, AsyncIterator

from fastapi import APIRouter
from fastapi.requests import Request
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from agents._react import (
    REACT_CONFIDENCE,
    build_user_message,
    extract_citations,
    extract_trace,
    final_answer,
)
from agents.base import AgentCapability, AgentRequest

router = APIRouter()


class DevQueryRequest(BaseModel):
    query: str
    task: str | None = None


def _emit(event: str, data: Any) -> dict[str, str]:
    return {"event": event, "data": json.dumps(data)}


def _final_payload(messages: list[Any], agent_name: str, capability: AgentCapability) -> dict[str, Any]:
    from agents._react import extract_requested_inputs
    from agents.pharmaceutical.tools import REQUEST_INPUT_TOOL_NAME
    return {
        "capability": capability.value,
        "answer": final_answer(messages),
        "confidence": REACT_CONFIDENCE,
        "escalate": False,
        "citations": [c.model_dump() for c in extract_citations(messages)],
        "trace": [
            {"agent": s.agent, "message": s.message, "time": s.formatted_time}
            for s in extract_trace(messages, agent_name)
        ],
        "requested_inputs": extract_requested_inputs(messages, REQUEST_INPUT_TOOL_NAME),
    }


async def _stream_agent_graph(
    graph: CompiledStateGraph,
    body: DevQueryRequest,
    agent_name: str,
    capability: AgentCapability,
) -> AsyncIterator[dict[str, str]]:
    user_text = build_user_message(AgentRequest(query=body.query, task=body.task))
    seen = 0
    final_messages: list[Any] = []

    async for state in graph.astream(
        {"messages": [HumanMessage(content=user_text)]},
        stream_mode="values",
    ):
        msgs = state.get("messages", [])
        for msg in msgs[seen:]:
            if isinstance(msg, AIMessage) and msg.tool_calls:
                # AIMessages that carry tool_calls often also carry the model's
                # freeform reasoning ("I should call X because…") — surface it
                # so the user sees the mini-plan before tools fire.
                if msg.content and (text := str(msg.content).strip()):
                    yield _emit("reasoning", {"text": text})
                for tc in msg.tool_calls:
                    yield _emit("tool_call", {"tool": tc["name"], "input": tc["args"]})
            elif isinstance(msg, ToolMessage):
                yield _emit("tool_result", {"tool": msg.name or "tool", "output": str(msg.content)})
        seen = len(msgs)
        final_messages = msgs

    if final_messages:
        yield _emit("final", _final_payload(final_messages, agent_name, capability))
    yield _emit("done", {})


@router.post("/pharmaceutical/stream")
async def pharmaceutical_stream(
    body: DevQueryRequest, request: Request
) -> EventSourceResponse:
    return EventSourceResponse(
        _stream_agent_graph(
            request.app.state.pharmaceutical_graph,
            body,
            agent_name="pharmaceutical",
            capability=AgentCapability.PHARMACEUTICAL,
        )
    )


@router.post("/research/stream")
async def research_stream(
    body: DevQueryRequest, request: Request
) -> EventSourceResponse:
    return EventSourceResponse(
        _stream_agent_graph(
            request.app.state.research_graph,
            body,
            agent_name="research",
            capability=AgentCapability.RESEARCH,
        )
    )


@router.post("/cardiology/stream")
async def cardiology_stream(
    body: DevQueryRequest, request: Request
) -> EventSourceResponse:
    return EventSourceResponse(
        _stream_agent_graph(
            request.app.state.cardiology_graph,
            body,
            agent_name="cardiology",
            capability=AgentCapability.CARDIOLOGY,
        )
    )
