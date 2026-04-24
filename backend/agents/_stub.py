from __future__ import annotations

from .base import Agent, AgentCapability, AgentRequest, AgentResponse, TraceStep


def make_stub_agent(capability: AgentCapability) -> Agent:
    async def stub(request: AgentRequest) -> AgentResponse:
        task_note = f" | Task: {request.task}" if request.task else ""
        return AgentResponse(
            answer=f"[{capability.value.upper()} STUB] Query: '{request.query}'{task_note}",
            citations=[],
            confidence=0.5,
            reasoning_trace=[TraceStep(agent=capability.value, message=f"Stub: no real reasoning performed{task_note}")],
            escalate=False,
            capability=capability,
        )
    return stub  # type: ignore[return-value]
