"""Standalone runner for the pharmaceutical expert.

From `backend/`, run:
    uv run python -m agents.pharmaceutical

Edit the `request` below to test different drugs / clinical contexts.
"""

from __future__ import annotations

import asyncio

from langchain_openai import ChatOpenAI

from agents.base import AgentRequest
from settings import settings

from .agent import make_pharmaceutical_expert


async def main() -> None:
    llm = ChatOpenAI(model=settings.model, api_key=settings.openai_api_key)
    agent = make_pharmaceutical_expert(llm)

    # `query` mimics the original prompt to the orchestrator (full clinical scenario).
    # `task` is what the orchestrator would ask this expert specifically (the drug + asks).
    request = AgentRequest(
        query=(
            "65-year-old presenting with acute STEMI. eGFR 45 mL/min/1.73m². "
            "Currently on aspirin 75 mg and apixaban 5 mg BID. "
            "Planning to start a beta-blocker for rate control."
        ),
        task=(
            "For metoprolol: dose-calculation inputs needed for this patient, "
            "expected adverse effects given the clinical context, and any drug "
            "interactions that would contraindicate or modify the regimen."
        ),
    )

    response = await agent(request)

    print(f"Answer:\n{response.answer}\n")
    print(f"Confidence: {response.confidence:.2f}")
    print(f"Capability: {response.capability.value}")
    print(f"Citations:  {len(response.citations)}")
    print("\nTrace:")
    for step in response.reasoning_trace:
        print(f"  [{step.formatted_time}] [{step.agent}] {step.message}")


if __name__ == "__main__":
    asyncio.run(main())
