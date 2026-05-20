from __future__ import annotations

import httpx
from langchain_core.tools import tool

from agents._artifacts import GuidelineChunk, GuidelinesArtifact
from settings import settings

_ENDPOINT = (
    "https://konsulten-intelligence-gaf4gqgwbvgcgca8."
    "swedencentral-01.azurewebsites.net/external/guidelines/search"
)
_TOP_K = 5
_TIMEOUT_SECONDS = 30.0


def _format_chunk(c: GuidelineChunk, idx: int) -> str:
    header = c.heading_path or f"Document {c.doc_id}"
    return f"## [{idx}] {header}\n{c.text}"


@tool(response_format="content_and_artifact")
def guideline_search(query: str) -> tuple[str, GuidelinesArtifact]:
    """Search Swedish cardiology guidelines (local PMs, ESC translations) using BM25.
    Use short, focused queries of 2-5 key terms.
    Good: "förmaksflimmer antikoagulation", "hjärtsvikt diuretika"
    Bad: "what is the recommended treatment for atrial fibrillation in elderly patients with chronic kidney disease"
    Returns the top-matching guideline chunks with their source metadata.
    """
    response = httpx.post(
        _ENDPOINT,
        headers={"X-API-Key": settings.konsulten_api_key.get_secret_value()},
        json={"query": query, "top_k": _TOP_K},
        timeout=_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    raw = response.json().get("results") or []
    chunks = [GuidelineChunk(**r) for r in raw]
    artifact = GuidelinesArtifact(query=query, results=chunks)
    if not chunks:
        return (f"No guideline results for query: {query!r}.", artifact)
    content = "\n\n".join(_format_chunk(c, i + 1) for i, c in enumerate(chunks))
    return (content, artifact)
