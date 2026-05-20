from __future__ import annotations

import httpx
from langchain_core.tools import tool

from agents._artifacts import DrugLabelArtifact

# TODO: supplement with FASS for Swedish-regulatory alignment.
# openFDA covers US labels and is API-key-free, can we use it partily? I will use it to begin with for getting the agent running.

_BASE_URL = "https://api.fda.gov/drug/label.json"
_TIMEOUT_S = 10.0
_LABEL_LIMIT = 1
_MAX_SECTION_CHARS = 1500  # keep tool output tractable for the LLM context

_SECTIONS = (
    "indications_and_usage",
    "dosage_and_administration",
    "contraindications",
    "warnings_and_cautions",
    "drug_interactions",
    "adverse_reactions",
)


def _section_text(record: dict, key: str) -> str | None:
    value = record.get(key)
    if not value:
        return None
    text = value[0] if isinstance(value, list) else str(value)
    return text[:_MAX_SECTION_CHARS]


def _format_label(record: dict) -> str:
    parts: list[str] = []
    for section in _SECTIONS:
        if (text := _section_text(record, section)) is not None:
            parts.append(f"## {section}\n{text}")
    return "\n\n".join(parts) if parts else "Label found but contained none of the requested sections."


@tool(response_format="content_and_artifact")
def drug_label(drug_name: str) -> tuple[str, DrugLabelArtifact]:
    """Look up a drug's regulatory label by name. Returns indications, dosage, contraindications,
    warnings, drug interactions, and adverse reactions in that order.

    Source: openFDA (US labels) — to be supplemented with FASS for Swedish-regulatory alignment.
    Use the generic name for best results (e.g. "metoprolol", not "Lopressor").
    Returns "no label found" if the drug is not indexed by the source.
    """
    safe_name = drug_name.replace("/", " ")
    params = {"search": f"openfda.generic_name:{safe_name}", "limit": _LABEL_LIMIT}
    with httpx.Client(timeout=_TIMEOUT_S) as client:
        response = client.get(_BASE_URL, params=params)
    empty = DrugLabelArtifact(drug_name=drug_name, sections={})
    if response.status_code == 404:
        return (f"No openFDA label found for '{drug_name}'.", empty)
    response.raise_for_status()
    results = response.json().get("results") or []
    if not results:
        return (f"No openFDA label found for '{drug_name}'.", empty)
    record = results[0]
    sections = {
        s: text for s in _SECTIONS
        if (text := _section_text(record, s)) is not None
    }
    artifact = DrugLabelArtifact(drug_name=drug_name, sections=sections)
    return (_format_label(record), artifact)
