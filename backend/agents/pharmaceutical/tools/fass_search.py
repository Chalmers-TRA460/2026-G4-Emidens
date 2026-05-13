from __future__ import annotations

import httpx
from langchain_core.tools import tool

from settings import settings

_BASE_URL = "https://konsulten-intelligence-gaf4gqgwbvgcgca8.swedencentral-01.azurewebsites.net/external/fass/search"
_TIMEOUT_S = 20.0
_DEFAULT_TOP_K = 5
_MAX_TOP_K = 10
_MAX_CHUNK_CHARS = 1500


def _format_chunk(chunk: dict) -> str:
    drug = chunk.get("lakemedel") or "Okänt läkemedel"
    section = chunk.get("section") or "Okänd sektion"
    header = f"## {drug} — {section}"

    meta: list[str] = []
    if (atc := chunk.get("atc_code")):
        meta.append(f"ATC: {atc}")
    if (form := chunk.get("beredningsform")):
        meta.append(f"Beredningsform: {form}")
    if (sub := chunk.get("substans")):
        meta.append(f"Substans: {sub}")
    meta_line = " | ".join(meta)

    content = (chunk.get("content") or "").strip()
    if len(content) > _MAX_CHUNK_CHARS:
        content = content[:_MAX_CHUNK_CHARS] + "…"

    parts = [header]
    if meta_line:
        parts.append(meta_line)
    if content:
        parts.append(content)
    return "\n".join(parts)


@tool
def fass_search(query: str, top_k: int = _DEFAULT_TOP_K) -> str:
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
    if not results:
        return f"No FASS results for query: {query!r}."
    return "\n\n".join(_format_chunk(r) for r in results)
