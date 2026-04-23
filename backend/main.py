import asyncio

from langchain_ollama import ChatOllama

from agents import (
    AgentCapability,
    AgentRequest,
    Orchestrator,
    cardio_expert,
    regulatory_expert,
)
from graph import build_graph
from settings import settings


async def main() -> None:
    llm = ChatOllama(
        model=settings.model,
        base_url=settings.ollama_base_url,
    )

    orchestrator = Orchestrator(
        experts={
            AgentCapability.CARDIOLOGY: cardio_expert,
            AgentCapability.REGULATORY: regulatory_expert,
        },
        llm=llm,
    )

    graph = build_graph(orchestrator)

    request = AgentRequest(
        query="What is the correct metoprolol dose for a patient with heart failure and renal impairment?"
    )

    result = await graph.ainvoke({"request": request, "response": None})
    response = result["response"]

    print(f"Answer:     {response.answer}")
    print(f"Confidence: {response.confidence:.2f}")
    print(f"Escalate:   {response.escalate}")
    print(f"Capability: {response.capability.value}")
    print(f"Trace:")
    for step in response.reasoning_trace:
        print(f"  - {step}")


if __name__ == "__main__":
    asyncio.run(main())
