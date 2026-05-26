from __future__ import annotations

from contextvars import ContextVar

from langchain_core.tools import tool

REQUEST_INPUT_TOOL_NAME = "request_clinical_input"

REQUESTABLE_FIELDS: frozenset[str] = frozenset(
    {
        "age_years",
        "weight_kg",
        "renal_impairment",
        "hepatic_impairment",
        "active_conditions",
        "current_medications",
    }
)

_skipped_fields: ContextVar[frozenset[str]] = ContextVar(
    "_skipped_fields", default=frozenset()
)


def set_skipped_fields(fields: list[str]) -> None:
    """Mark fields the clinician has explicitly chosen to skip for the current
    request. `request_clinical_input` will refuse to re-request them."""
    _skipped_fields.set(frozenset(fields))


@tool
def request_clinical_input(fields: list[str]) -> str:
    """Request specific clinical inputs from the user when they are needed to answer
    safely and are missing from the clinical context. Call this BEFORE giving a
    dosing recommendation that depends on inputs you do not have.

    Valid field names: age_years, weight_kg, renal_impairment, hepatic_impairment,
    active_conditions, current_medications.

    Pass only the fields you actually need. Do not pad the list. After calling
    this tool, end your turn with a short message telling the user what you need
    and why.
    """
    skipped = _skipped_fields.get()
    valid = [f for f in fields if f in REQUESTABLE_FIELDS and f not in skipped]
    invalid = [f for f in fields if f not in REQUESTABLE_FIELDS]
    blocked = [f for f in fields if f in skipped]
    if not valid:
        if blocked:
            return (
                f"Cannot request {', '.join(blocked)}: the clinician explicitly "
                "skipped these fields for this query. Produce a best-effort answer "
                "with explicit safety caveats — do not call this tool again for "
                "the skipped fields."
            )
        return (
            "No valid fields requested. Use one or more of: "
            f"{', '.join(sorted(REQUESTABLE_FIELDS))}."
        )
    parts = [f"<<NEEDS_INPUT: {','.join(valid)}>>"]
    if blocked:
        parts.append(
            f"(refused to re-request fields the clinician skipped: {', '.join(blocked)})"
        )
    if invalid:
        parts.append(f"(ignored unknown fields: {', '.join(invalid)})")
    return " ".join(parts)
