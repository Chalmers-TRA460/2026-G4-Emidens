import asyncio

from langchain_ollama import ChatOllama

from agents import AgentCapability, AgentRequest, Orchestrator, make_stub_agent, make_research_expert
from graph import build_graph, initial_state
from settings import settings


async def main() -> None:
    llm = ChatOllama(
        model=settings.model,
        base_url=settings.ollama_base_url,
    )

    experts = {
        AgentCapability.CARDIOLOGY:  make_stub_agent(AgentCapability.CARDIOLOGY),
        AgentCapability.RESEARCH:    make_research_expert(llm),
        AgentCapability.REGULATORY:  make_stub_agent(AgentCapability.REGULATORY),
        AgentCapability.DRUG_DOSING: make_stub_agent(AgentCapability.DRUG_DOSING),
    }

    orchestrator = Orchestrator(llm=llm)
    graph = build_graph(orchestrator, experts)

    request = AgentRequest(
        query="What does the latest clinical evidence say about metoprolol in heart failure patients with renal impairment? Are there recent RCTs or guidelines?"
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
