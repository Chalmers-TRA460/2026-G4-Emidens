import asyncio

from langchain_ollama import ChatOllama

from agents import AgentCapability, AgentRequest, Orchestrator, make_stub_agent
from graph import build_graph, initial_state
from settings import settings

EXPERTS = {cap: make_stub_agent(cap) for cap in AgentCapability}


async def main() -> None:
    llm = ChatOllama(
        model=settings.model,
        base_url=settings.ollama_base_url,
    )

    orchestrator = Orchestrator(llm=llm)
    graph = build_graph(orchestrator, EXPERTS)

    request = AgentRequest(
        query="What is the correct metoprolol dose for a patient with heart failure and renal impairment?"
    )

    result = await graph.ainvoke(initial_state(request))

    response = result["final_response"]
    if response is None:
        print("Error: graph completed without producing a response")
        return
    print(f"Answer:     {response.answer}")
    print(f"Confidence: {response.confidence:.2f}")
    print(f"Escalate:   {response.escalate}")
    print(f"Capability: {response.capability.value}")
    print("Trace:")
    for step in response.reasoning_trace:
        print(f"  [{step.formatted_time}] [{step.agent}] {step.message}")


if __name__ == "__main__":
    asyncio.run(main())
