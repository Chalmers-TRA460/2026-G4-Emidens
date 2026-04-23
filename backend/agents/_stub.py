from __future__ import annotations

from .base import Agent, AgentCapability, AgentRequest, AgentResponse, TraceStep


def make_stub_agent(capability: AgentCapability) -> Agent:
    async def stub(request: AgentRequest) -> AgentResponse:
        return AgentResponse(
            answer=f"[{capability.value.upper()} STUB] Received query: '{request.query}'",
            citations=[],
            confidence=0.5,
            reasoning_trace=[TraceStep(agent=capability.value, message="Stub: no real reasoning performed")],
            escalate=False,
            capability=capability,
        )
    return stub  # type: ignore[return-value]
