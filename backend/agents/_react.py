from __future__ import annotations

import re

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage

from ._artifacts import (
    DosageCalculatorArtifact,
    DrugLabelArtifact,
    FassArtifact,
    GuidelinesArtifact,
    PubMedArtifact,
)
from .base import AgentRequest, Citation, TraceStep

_CITATION_PREVIEW_LEN = 200
_TRACE_CONTENT_LEN = 300
_TRACE_RESULT_LEN = 200

_PUBMED_WITH_ABSTRACT = 0.7   # item-level confidence when the abstract is present
_PUBMED_STUB_ONLY     = 0.4   # item-level confidence when only metadata returned
_DRUG_LABEL_HIT       = 0.8   # openFDA returned at least one section

_NEEDS_INPUT_PATTERN = re.compile(r"<<NEEDS_INPUT:\s*([^>]+)>>")


def extract_requested_inputs(messages: list[BaseMessage], tool_name: str) -> list[str]:
    """Return the union of fields requested via the given input-request tool.
    Tool result format: ``<<NEEDS_INPUT: field1,field2>>``."""
    fields: list[str] = []
    seen: set[str] = set()
    for m in messages:
        if not isinstance(m, ToolMessage) or m.name != tool_name:
            continue
        match = _NEEDS_INPUT_PATTERN.search(str(m.content))
        if not match:
            continue
        for raw in match.group(1).split(","):
            field = raw.strip()
            if field and field not in seen:
                seen.add(field)
                fields.append(field)
    return fields


def _citation_confidence(m: ToolMessage) -> float:
    """Per-citation confidence derived from the tool's structured artifact.

    - DosageCalculator: deterministic; 1.0 on success, 0.0 on invalid input.
    - Guidelines / FASS: clamped mean of similarity scores across returned chunks.
    - PubMed: NCBI does not expose relevance; use abstract coverage as a proxy
      (items with abstracts contribute 0.7, stub-only items 0.4, averaged).
    - openFDA drug label: 0.8 if any sections returned, else 0.0.
    - Anything without a recognized artifact (e.g. request_clinical_input): 0.0.
    """
    artifact = getattr(m, "artifact", None)

    if isinstance(artifact, DosageCalculatorArtifact):
        return 1.0 if artifact.result is not None else 0.0

    if isinstance(artifact, (GuidelinesArtifact, FassArtifact)):
        if not artifact.results:
            return 0.0
        mean = sum(r.score for r in artifact.results) / len(artifact.results)
        return max(0.0, min(1.0, mean))

    if isinstance(artifact, PubMedArtifact):
        if not artifact.results:
            return 0.0
        per_item = [
            _PUBMED_WITH_ABSTRACT if r.abstract else _PUBMED_STUB_ONLY
            for r in artifact.results
        ]
        return sum(per_item) / len(per_item)

    if isinstance(artifact, DrugLabelArtifact):
        return _DRUG_LABEL_HIT if artifact.sections else 0.0

    return 0.0


def extract_citations(messages: list[BaseMessage]) -> list[Citation]:
    return [
        Citation(
            source=m.name or "tool",
            section=str(m.content)[:_CITATION_PREVIEW_LEN],
            tool_call_id=m.tool_call_id,
            confidence=_citation_confidence(m),
        )
        for m in messages
        if isinstance(m, ToolMessage)
    ]


def extract_trace(messages: list[BaseMessage], agent_name: str) -> list[TraceStep]:
    steps: list[TraceStep] = []
    for m in messages:
        if isinstance(m, HumanMessage):
            steps.append(
                TraceStep(
                    agent=agent_name,
                    message=f"Input: {str(m.content)[:_TRACE_CONTENT_LEN]}",
                )
            )
        elif isinstance(m, AIMessage):
            if m.tool_calls:
                for tc in m.tool_calls:
                    steps.append(
                        TraceStep(
                            agent=agent_name,
                            message=f"Tool call: {tc['name']}({tc['args']})",
                        )
                    )
            elif m.content:
                steps.append(
                    TraceStep(
                        agent=agent_name,
                        message=f"Reasoning: {str(m.content)[:_TRACE_CONTENT_LEN]}",
                    )
                )
        elif isinstance(m, ToolMessage):
            steps.append(
                TraceStep(
                    agent=agent_name,
                    message=f"Tool result [{m.name}]: {str(m.content)[:_TRACE_RESULT_LEN]}",
                )
            )
    return steps


def build_user_message(request: AgentRequest) -> str:
    if request.task:
        return f"Original query: {request.query}\n\nYour task: {request.task}"
    return request.query


def final_answer(messages: list[BaseMessage]) -> str:
    for m in reversed(messages):
        if isinstance(m, AIMessage) and m.content and not m.tool_calls:
            if isinstance(m.content, list):
                return "".join(
                    b["text"]
                    for b in m.content
                    if isinstance(b, dict) and b.get("type") == "text"
                )
            return str(m.content)
    return "[no answer produced]"
