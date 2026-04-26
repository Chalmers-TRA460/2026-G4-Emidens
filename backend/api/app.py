from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_ollama import ChatOllama

from agents import Orchestrator, make_experts
from graph import build_graph
from settings import settings
from .routes import query_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    llm = ChatOllama(model=settings.model, base_url=settings.ollama_base_url)
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
