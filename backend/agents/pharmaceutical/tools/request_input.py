from __future__ import annotations

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
    valid = [f for f in fields if f in REQUESTABLE_FIELDS]
    invalid = [f for f in fields if f not in REQUESTABLE_FIELDS]
    if not valid:
        return (
            "No valid fields requested. Use one or more of: "
            f"{', '.join(sorted(REQUESTABLE_FIELDS))}."
        )
    parts = [f"<<NEEDS_INPUT: {','.join(valid)}>>"]
    if invalid:
        parts.append(f"(ignored unknown fields: {', '.join(invalid)})")
    return " ".join(parts)
