"""Interactive runner for the pharmaceutical expert.

From `backend/`, run:
    uv run python -m agents.pharmaceutical

At each round you'll be prompted for two strings:
  1. Clinical scenario — the full original prompt to the orchestrator
     (e.g. "65 y/o with acute STEMI, eGFR 45, on aspirin + apixaban").
  2. Specific task — what the orchestrator would ask this expert
     (e.g. "for metoprolol, dosing inputs + interactions"). May be blank.

Empty scenario or Ctrl+D / Ctrl+C exits.
"""

from __future__ import annotations

import asyncio

from langchain_ollama import ChatOllama

from agents.base import AgentRequest, AgentResponse
from settings import settings

from .agent import make_pharmaceutical_expert


def _print_response(response: AgentResponse) -> None:
    print(f"\nAnswer:\n{response.answer}\n")
    print(f"Confidence: {response.confidence:.2f}")
    print(f"Capability: {response.capability.value}")
    print(f"Citations:  {len(response.citations)}")
    print("\nTrace:")
    for step in response.reasoning_trace:
        print(f"  [{step.formatted_time}] [{step.agent}] {step.message}")


def _prompt(label: str) -> str | None:
    try:
        return input(f"{label}> ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None


async def main() -> None:
    llm = ChatOllama(model=settings.model, base_url=settings.ollama_base_url)
    agent = make_pharmaceutical_expert(llm)

    print(f"Pharmaceutical agent ready (model: {settings.model}). Empty input or Ctrl+C exits.")

    while True:
        print("\n--- new query ---")
        query = _prompt("scenario ")
        if not query:
            break
        task = _prompt("task     ") or None

        response = await agent(AgentRequest(query=query, task=task))
        _print_response(response)


if __name__ == "__main__":
    asyncio.run(main())
