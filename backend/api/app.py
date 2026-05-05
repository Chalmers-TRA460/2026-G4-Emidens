from __future__ import annotations

import warnings
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

# Cosmetic warning from langchain's `with_structured_output` interacting with
# pydantic 2.x serialization. Output is parsed correctly; only the log is noisy.
warnings.filterwarnings("ignore", message="Pydantic serializer warnings")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_anthropic import ChatAnthropic

from agents import Orchestrator, make_experts
from agents.pharmaceutical import build_pharmaceutical_graph
from agents.research import build_research_graph
from graph import build_graph
from settings import settings

from .routes import dev_router, query_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    llm = ChatAnthropic(
        model_name=settings.model,
        base_url=settings.ollama_base_url,
        temperature=0.0,
        stop=None,
        timeout=None,
    )
    app.state.graph = build_graph(Orchestrator(llm=llm), make_experts(llm))
    app.state.pharmaceutical_graph = build_pharmaceutical_graph(llm)
    app.state.research_graph = build_research_graph(llm)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query_router)
app.include_router(dev_router, prefix="/dev")
