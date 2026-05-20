from __future__ import annotations

import httpx
from langchain_core.tools import tool

from agents._artifacts import FassArtifact, FassChunk
from settings import settings

_BASE_URL = "https://konsulten-intelligence-gaf4gqgwbvgcgca8.swedencentral-01.azurewebsites.net/external/fass/search"
_TIMEOUT_S = 20.0
_DEFAULT_TOP_K = 5
_MAX_TOP_K = 10
_MAX_CHUNK_CHARS = 1500


def _format_chunk(chunk: FassChunk) -> str:
    drug = chunk.lakemedel or "Okänt läkemedel"
    section = chunk.section or "Okänd sektion"
    header = f"## {drug} — {section}"

    meta: list[str] = []
    if chunk.atc_code:
        meta.append(f"ATC: {chunk.atc_code}")
    if chunk.beredningsform:
        meta.append(f"Beredningsform: {chunk.beredningsform}")
    if chunk.substans:
        meta.append(f"Substans: {chunk.substans}")
    meta_line = " | ".join(meta)

    content = chunk.content.strip()
    if len(content) > _MAX_CHUNK_CHARS:
        content = content[:_MAX_CHUNK_CHARS] + "…"

    parts = [header]
    if meta_line:
        parts.append(meta_line)
    if content:
        parts.append(content)
    return "\n".join(parts)


@tool(response_format="content_and_artifact")
def fass_search(query: str, top_k: int = _DEFAULT_TOP_K) -> tuple[str, FassArtifact]:
    """Search Swedish FASS drug labels (Läkemedelsfakta) with a natural-language question.

    Use this for any Swedish-regulatory drug question: dosing, indications, contraindications,
    interactions, adverse effects, monitoring. Prefer over `drug_label` (openFDA) when the
    patient is being treated in Sweden, since FASS reflects the locally approved label.

    The query can be in Swedish or English; phrase it specifically (e.g. "metoprolol dosering vid
    hjärtsvikt NYHA III" rather than "metoprolol"). Each result is a label chunk from one product,
    tagged with section (e.g. "4.2 Dosering"), ATC code, and substance.

    `top_k` defaults to 5; raise it for broad questions, lower for narrow ones.
    """
    top_k = max(1, min(int(top_k), _MAX_TOP_K))
    headers = {
        "X-API-Key": settings.konsulten_api_key.get_secret_value(),
        "Content-Type": "application/json",
    }
    payload = {"query": query, "top_k": top_k}
    with httpx.Client(timeout=_TIMEOUT_S) as client:
        response = client.post(_BASE_URL, headers=headers, json=payload)
    response.raise_for_status()
    results = response.json().get("results") or []
    chunks = [FassChunk(**r) for r in results]
    artifact = FassArtifact(query=query, results=chunks)
    if not chunks:
        return (f"No FASS results for query: {query!r}.", artifact)
    content = "\n\n".join(_format_chunk(c) for c in chunks)
    return (content, artifact)
