from __future__ import annotations

import warnings
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

# Cosmetic warning from langchain's `with_structured_output` interacting with
# pydantic 2.x serialization. Output is parsed correctly; only the log is noisy.
warnings.filterwarnings("ignore", message="Pydantic serializer warnings")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI

from agents import Orchestrator, make_experts
from graph import build_graph
from settings import settings
from .routes import query_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    llm = ChatOpenAI(model=settings.model, api_key=settings.openai_api_key)
    app.state.graph = build_graph(Orchestrator(llm=llm), make_experts(llm))
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query_router)
