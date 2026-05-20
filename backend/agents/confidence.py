"""Centralised confidence-score logic for Emidens experts.

This is the single place to tune how each agent reports its confidence.
Each ``*_confidence`` function takes the ReAct message list (the same
``messages = result["messages"]`` returned by ``react_graph.ainvoke``)
plus the originating :class:`AgentRequest`, and returns a float in
``[0, 1]``.

The functions are deliberately interpretable: they compute a small
number of named signals from the tool outputs, combine them with
named weights, and clip to ``[MIN_CONFIDENCE, MAX_CONFIDENCE]``. Tune
the ``*_WEIGHT_*`` / ``*_THRESHOLD_*`` / ``*_PENALTY_*`` constants
below to change behaviour without touching the per-agent code.

================================================================================
Tool API response shapes (recap of what each agent has to work with)
================================================================================

CARDIOLOGY — ``guideline_search`` (BM25 over Swedish PMs + ESC translations)
    POST https://…/external/guidelines/search
    Response (JSON):
        {
          "results": [
            {
              "chunk_id":     str,    # stable hash, dedup key
              "doc_id":       int,    # which guideline document
              "heading_path": str,    # section heading, e.g. "Terapirekommendation"
              "text":         str,    # the matched chunk
              "score":        float,  # BM25, ~0.0–1.0 in observed range
            },
            ...
          ]
        }
    Useful signals: score of top hit, number of hits above a threshold,
    whether the corpus returned anything at all.

PHARMACEUTICAL — ``fass_search`` (semantic search over Swedish FASS labels)
    POST https://…/external/fass/search
    Raw API response (JSON):
        {
          "results": [
            {
              "chunk_id":       str,
              "doc_folder":     str,   # e.g. "C07AB02_Metoprolol_Teva_(…)"
              "lakemedel":      str,   # branded product
              "substans":       str,   # active substance
              "beredningsform": str,   # dose form/strength
              "section":        str,   # e.g. "4.2: Dosering och administreringssätt"
              "atc_code":       str,
              "content":        str,   # the label chunk
              "score":          float, # observed ~0.5–0.8 for solid matches
            },
            ...
          ]
        }
    NOTE: the ``fass_search`` *tool* (agents/pharmaceutical/tools/fass_search.py)
    reformats this into Markdown blocks like::
        ## Metoprolol Teva — 4.2: Dosering och administreringssätt
        ATC: C07AB02 | Beredningsform: … | Substans: …
        Dosering...
    So when we read ``ToolMessage.content`` we work with that string form
    (score is discarded by the formatter). On an empty result the tool
    returns ``"No FASS results for query: …"``.

    Useful signals: number of chunks returned, whether any returned
    ``section`` matches the query intent (e.g. "4.2 Dosering" for a
    dosing question), and whether ``request_clinical_input`` was
    triggered (missing patient data → less confident dose claims).

RESEARCH — ``pubmed_tool`` (LangChain ``PubmedQueryRun`` wrapping NCBI E-utilities)
    Returns a *plain string* (not JSON). One block per article, separated
    by blank lines, looking like:
        Published: 2026-05-04
        Title: …
        Copyright Information: …
        Summary::
        BACKGROUND: …
    On a miss it returns ``"No good PubMed Result was found"``.
    Useful signals: number of "Title:" blocks (≈ number of articles),
    recency of "Published:" dates, presence of the no-result sentinel.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Iterable

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage

from .base import AgentRequest

# ================================================================================
# Global bounds — every score is clipped to this range so callers can rely on
# a strict (0, 1) interval and never see 0.0/1.0 collapses.
# ================================================================================
MIN_CONFIDENCE: float = 0.05
MAX_CONFIDENCE: float = 0.95
BASELINE_CONFIDENCE: float = 0.50  # starting point before signals are applied

# ================================================================================
# Cardiology tuning
# ================================================================================
CARD_TOOL_NAME: str = "guideline_search"

# Penalties (subtracted from baseline) when the agent did not engage with
# the guideline corpus the way it was supposed to.
CARD_MISSING_TOOL_PENALTY: float = 0.40   # agent never searched guidelines
CARD_EMPTY_RESULTS_PENALTY: float = 0.30  # searched but got zero hits
CARD_ABSTENTION_PENALTY: float = 0.20     # answer says "corpus is silent"

# Positive signal weights (added to baseline after penalties).
CARD_TOP_SCORE_WEIGHT: float = 0.30       # scales the top BM25 score
CARD_STRONG_HITS_WEIGHT: float = 0.15     # full credit at this many strong hits
CARD_STRONG_HIT_FULL_CREDIT_AT: int = 3
CARD_STRONG_HIT_SCORE_FLOOR: float = 0.60 # minimum score to count as "strong"

# ================================================================================
# Pharmaceutical tuning
# ================================================================================
PHARM_TOOL_NAME: str = "fass_search"
PHARM_NEEDS_INPUT_TOOL_NAME: str = "request_clinical_input"

PHARM_MISSING_TOOL_PENALTY: float = 0.40
PHARM_EMPTY_RESULTS_PENALTY: float = 0.30
PHARM_NEEDS_INPUT_PENALTY: float = 0.25   # asked for patient data we don't have

PHARM_HIT_COUNT_WEIGHT: float = 0.20      # full credit at this many chunks
PHARM_HIT_FULL_CREDIT_AT: int = 4
PHARM_SECTION_MATCH_BONUS: float = 0.20   # right FASS section for the question

# Sentinel emitted by `_format_chunk` when the FASS API returns no rows.
PHARM_NO_RESULT_SENTINEL: str = "No FASS results for query:"

# Map query intent → FASS section prefix that should appear among results.
# Tune by adding (regex, section-prefix) pairs as new intent classes emerge.
PHARM_INTENT_SECTION_MAP: tuple[tuple[str, str], ...] = (
    (r"\b(dos|dose|dosing|dosering)\b",                            "4.2"),
    (r"\b(kontraindik|contraindic)\b",                             "4.3"),
    (r"\b(varning|försiktighet|warning|precaution)\b",             "4.4"),
    (r"\b(interakt|interaction)\b",                                "4.5"),
    (r"\b(graviditet|amning|pregnan|lactation)\b",                 "4.6"),
    (r"\b(biverk|adverse|side[- ]effect)\b",                       "4.8"),
)

# ================================================================================
# Research tuning
# ================================================================================
RES_TOOL_NAME: str = "pubmed_tool"

RES_MISSING_TOOL_PENALTY: float = 0.40
RES_NO_RESULTS_PENALTY: float = 0.30

RES_ARTICLE_COUNT_WEIGHT: float = 0.20
RES_ARTICLE_FULL_CREDIT_AT: int = 5        # full count credit at ≥ this many
RES_RECENCY_WEIGHT: float = 0.15
RES_RECENT_WINDOW_YEARS: int = 5           # newer than this → full recency credit

# Sentinel strings emitted by langchain's PubmedQueryRun on empty results.
RES_NO_RESULT_SENTINELS: tuple[str, ...] = (
    "No good PubMed Result was found",
    "No good Pubmed Result was found",
)


# ================================================================================
# Internal helpers
# ================================================================================

def _clip(x: float) -> float:
    return max(MIN_CONFIDENCE, min(MAX_CONFIDENCE, x))


def _tool_messages(messages: Iterable[BaseMessage], tool_name: str) -> list[ToolMessage]:
    return [m for m in messages if isinstance(m, ToolMessage) and m.name == tool_name]


def _final_text(messages: Iterable[BaseMessage]) -> str:
    """Best-effort extraction of the agent's final natural-language answer."""
    for m in reversed(list(messages)):
        if isinstance(m, AIMessage) and m.content and not m.tool_calls:
            if isinstance(m.content, list):
                return " ".join(b.get("text", "") for b in m.content if isinstance(b, dict))
            return str(m.content)
    return ""


def _parse_json_results(tool_message: ToolMessage) -> list[dict]:
    """Parse a Konsulten tool message whose body is a JSON ``{"results": [...]}``.
    Returns ``[]`` if parsing fails — confidence functions then treat the call
    as an empty-result hit, which is the safe default.
    """
    try:
        data = json.loads(str(tool_message.content))
    except (ValueError, TypeError):
        return []
    if isinstance(data, dict):
        results = data.get("results")
        return results if isinstance(results, list) else []
    return []


def _max_score(results: list[dict]) -> float:
    scores = [r.get("score") for r in results if isinstance(r.get("score"), (int, float))]
    return max(scores) if scores else 0.0


def _section_matches_intent(query: str, sections: list[str]) -> bool:
    """Did *any* returned FASS section live in the area that the query
    intent points at? E.g. dosing question + a result tagged "4.2 Dosering"."""
    q = query.lower()
    target_prefixes = [
        prefix for pattern, prefix in PHARM_INTENT_SECTION_MAP if re.search(pattern, q)
    ]
    if not target_prefixes:
        return False
    for section in sections:
        s = section.lower().lstrip()
        if any(s.startswith(prefix) for prefix in target_prefixes):
            return True
    return False


# `## {drug} — {section}` blocks emitted by `_format_chunk` in fass_search.py.
# The separator is an em-dash; we accept en-dash and hyphen too for robustness.
_FASS_HEADER_RE = re.compile(r"^##\s+.+?\s+[—–-]\s+(?P<section>.+)$", re.MULTILINE)


def _parse_fass_chunks(text: str) -> list[str]:
    """Return the section label of each chunk in the FASS formatted output."""
    if PHARM_NO_RESULT_SENTINEL in text:
        return []
    return [m.group("section").strip() for m in _FASS_HEADER_RE.finditer(text)]


_ABSTENTION_PATTERNS = (
    r"\bcorpus is silent\b",
    r"\bno (relevant )?guidelines? (found|available|cover)\b",
    r"\bnot covered (by|in) (the )?guidelines?\b",
    r"\bdo(?:es)? not (?:have|contain) (?:enough )?information\b",
    r"\bguidelines? (?:are|is) silent\b",
)
_ABSTENTION_RE = re.compile("|".join(_ABSTENTION_PATTERNS), re.IGNORECASE)


def _looks_like_abstention(text: str) -> bool:
    return bool(_ABSTENTION_RE.search(text))


# PubMed text-output parsing
_PUBMED_TITLE_RE = re.compile(r"^Title:", re.MULTILINE)
_PUBMED_PUB_RE = re.compile(r"^Published:\s*(\d{4})-\d{2}-\d{2}", re.MULTILINE)


def _pubmed_article_count(text: str) -> int:
    return len(_PUBMED_TITLE_RE.findall(text))


def _pubmed_recency_credit(text: str) -> float:
    """Return 0.0–1.0 based on how recent the newest article is."""
    years = [int(m.group(1)) for m in _PUBMED_PUB_RE.finditer(text)]
    if not years:
        return 0.0
    newest = max(years)
    current_year = datetime.now(timezone.utc).year
    age = max(0, current_year - newest)
    if age >= RES_RECENT_WINDOW_YEARS:
        return 0.0
    return 1.0 - (age / RES_RECENT_WINDOW_YEARS)


def _pubmed_says_no_results(text: str) -> bool:
    return any(s in text for s in RES_NO_RESULT_SENTINELS)


# ================================================================================
# Per-agent confidence functions
# ================================================================================

def cardiology_confidence(messages: list[BaseMessage], request: AgentRequest) -> float:
    """Confidence in a cardiology answer.

    Signals (in order of importance):
        1. Did the agent search the guideline corpus at all?
        2. Did any search return results?
        3. How high is the top BM25 score?
        4. How many strong (≥ floor) hits were returned across all searches?
        5. Did the final answer explicitly abstain ("corpus is silent")?
    """
    del request  # unused for now — kept in signature for future tuning
    tool_calls = _tool_messages(messages, CARD_TOOL_NAME)
    score = BASELINE_CONFIDENCE

    if not tool_calls:
        return _clip(score - CARD_MISSING_TOOL_PENALTY)

    all_results = [r for tc in tool_calls for r in _parse_json_results(tc)]
    if not all_results:
        return _clip(score - CARD_EMPTY_RESULTS_PENALTY)

    top = _max_score(all_results)
    strong_hits = sum(1 for r in all_results if (r.get("score") or 0) >= CARD_STRONG_HIT_SCORE_FLOOR)

    score += CARD_TOP_SCORE_WEIGHT * top
    score += CARD_STRONG_HITS_WEIGHT * min(1.0, strong_hits / CARD_STRONG_HIT_FULL_CREDIT_AT)

    if _looks_like_abstention(_final_text(messages)):
        score -= CARD_ABSTENTION_PENALTY

    return _clip(score)


def pharmaceutical_confidence(messages: list[BaseMessage], request: AgentRequest) -> float:
    """Confidence in a pharmaceutical answer.

    Signals:
        1. Did the agent search FASS?
        2. Did FASS return chunks (vs. the no-result sentinel)?
        3. How many chunks across all FASS calls (capped)?
        4. Did *any* returned chunk live in the section that the user's
           query intent points at (e.g. 4.2 Dosering for a dose question)?
        5. Did the agent emit ``request_clinical_input``? Missing patient
           data lowers confidence in any dose recommendation.
    """
    fass_calls = _tool_messages(messages, PHARM_TOOL_NAME)
    needs_input_calls = _tool_messages(messages, PHARM_NEEDS_INPUT_TOOL_NAME)
    score = BASELINE_CONFIDENCE

    if not fass_calls:
        score -= PHARM_MISSING_TOOL_PENALTY
    else:
        sections = [s for tc in fass_calls for s in _parse_fass_chunks(str(tc.content))]
        if not sections:
            score -= PHARM_EMPTY_RESULTS_PENALTY
        else:
            score += PHARM_HIT_COUNT_WEIGHT * min(1.0, len(sections) / PHARM_HIT_FULL_CREDIT_AT)
            if _section_matches_intent(request.query, sections):
                score += PHARM_SECTION_MATCH_BONUS

    if needs_input_calls:
        score -= PHARM_NEEDS_INPUT_PENALTY

    return _clip(score)


def research_confidence(messages: list[BaseMessage], request: AgentRequest) -> float:
    """Confidence in a research / evidence-grading answer.

    Signals:
        1. Did the agent query PubMed?
        2. Did PubMed return any articles (no sentinel string)?
        3. How many articles did it find, across all queries?
        4. How recent is the newest article?
    """
    del request
    pubmed_calls = _tool_messages(messages, RES_TOOL_NAME)
    score = BASELINE_CONFIDENCE

    if not pubmed_calls:
        return _clip(score - RES_MISSING_TOOL_PENALTY)

    joined = "\n\n".join(str(m.content) for m in pubmed_calls)

    if _pubmed_says_no_results(joined) and _pubmed_article_count(joined) == 0:
        return _clip(score - RES_NO_RESULTS_PENALTY)

    article_count = _pubmed_article_count(joined)
    score += RES_ARTICLE_COUNT_WEIGHT * min(1.0, article_count / RES_ARTICLE_FULL_CREDIT_AT)
    score += RES_RECENCY_WEIGHT * _pubmed_recency_credit(joined)

    return _clip(score)
