import re

from langchain_core.tools import tool

from agents._artifacts import DosageCalculatorArtifact


@tool(response_format="content_and_artifact")
def dosage_calculator(query: str) -> tuple[str, DosageCalculatorArtifact]:
    """
    Evaluates a mathematical expression string and returns a deterministic numeric result. Use this tool whenever a precise arithmetic calculation is needed, such as computing drug doses, unit conversions, rate calculations, or any formula-based result where accuracy is critical. Prefer this over reasoning through math mentally.

    Common use cases:
        - Dose by weight: "80 * 0.5" (mg/kg for an 80kg patient at 0.5 mg/kg)
        - Infusion rates: "500 / 8" (mg/hr over 8 hours)
        - Unit conversion: "1200 / 1000" (mcg to mg)
        - BSA-based dosing: "1.73 * 75" (dose scaled to body surface area)
        - Renal adjustment: "120 * 0.75" (reduced dose for renal impairment)

    Input rules — the expression must contain ONLY:
        - Numbers (integers or decimals): 0-9, .
        - Operators: + - * / ** (exponentiation)
        - Parentheses: ( )
        - Whitespace

    Any letters, function names, or other characters are not allowed and will raise an error. Do not pass variable names, units, or words — resolve all values to numbers first.

    Good:   "80 * 0.5"
    Good:   "(1200 / 1000) * 2"
    Bad:    "weight * dose"       ← no variable names
    Bad:    "round(80 * 0.5, 2)"  ← no function calls
    Bad:    "80 * 0.5 mg"         ← no units in the string
    """

    artifact = DosageCalculatorArtifact(query=query)
    if not re.fullmatch(r"[\d\s\+\-\*\/\(\)\.\*\*]+", query):
        return f"Invalid characters in expression: {query!r}", artifact

    try:
        result = eval(query)
    except Exception as e:
        return (
            f"Could not evaluate expression {query!r}: {e.__class__.__name__}",
            artifact,
        )

    content = f"The expression {query} equates to {result}"
    artifact.result = result
    return content, artifact

