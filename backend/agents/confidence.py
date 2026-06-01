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

RESEARCH — ``pubmed_tool`` (custom NCBI E-utilities client, see
    agents/research/tools/pubmed.py)
    Uses ``response_format="content_and_artifact"``: ``content`` is a
    human-readable block per article (``[1] PMID 12345 (2026) — title…``)
    for the LLM, while the typed rows live on ``tool_message.artifact``
    as a :class:`PubMedArtifact` (``.results`` is a list of
    :class:`PubMedItem`, each with ``year``). On a miss the artifact's
    ``results`` is empty and ``content`` is a sentinel like
    ``"No PubMed results for query: …"``.
    We read the artifact (not the prose) so article count and recency
    survive — mirroring how the cardiology confidence reads its artifact.
    Useful signals: number of result rows (≈ number of articles),
    recency of the newest ``year``, whether any results came back at all.
"""

from __future__ import annotations

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
PHARM_SKIPPED_FIELDS_PENALTY: float = 0.25  # clinician declined to provide requested data

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


# ================================================================================
# Internal helpers
# ================================================================================

def _clip(x: float) -> float:
    return max(MIN_CONFIDENCE, min(MAX_CONFIDENCE, x))


def _log_breakdown(
    agent: str,
    request: AgentRequest,
    deltas: list[tuple[str, float]],
    final: float,
) -> None:
    """Print a transparent breakdown of how the confidence score was assembled.

    ``deltas`` is the ordered list of (label, delta) pairs applied after the
    baseline. The unclipped running sum is shown in the rightmost column so
    you can see when/where the score hits the [MIN, MAX] bound.
    """
    query = (request.query or "").strip().replace("\n", " ")
    if len(query) > 80:
        query = query[:77] + "..."
    label_w = 38
    running = BASELINE_CONFIDENCE
    print(f"[confidence] {agent}  q=\"{query}\"")
    print(f"  {'baseline':<{label_w}}        = {running:6.3f}")
    for label, delta in deltas:
        running += delta
        print(f"  {label:<{label_w}} {delta:+6.3f}  → {running:6.3f}")
    print(f"  {'─' * (label_w + 20)}")
    note = "" if abs(final - running) < 1e-9 else f"  (clipped from {running:.3f})"
    print(f"  {'final':<{label_w}}        = {final:6.3f}{note}")


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
    """Extract structured result rows from a Konsulten tool message.

    These tools use ``response_format="content_and_artifact"``: ``content`` is
    a Markdown preview for the LLM, while the typed rows (with ``score``) live
    on ``tool_message.artifact``. We pull from the artifact so the scores
    survive — parsing the Markdown back into JSON would always fail.
    Returns ``[]`` if no artifact is present, which the confidence functions
    treat as an empty-result hit.
    """
    artifact = getattr(tool_message, "artifact", None)
    results = getattr(artifact, "results", None) if artifact is not None else None
    if not results:
        return []
    return [r.model_dump() if hasattr(r, "model_dump") else dict(r) for r in results]


def _max_score(results: list[dict]) -> float:
    scores = [s for r in results if isinstance(s := r.get("score"), (int, float))]
    return float(max(scores)) if scores else 0.0


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


# PubMed artifact parsing. The custom pubmed_tool returns its rows on the
# ToolMessage artifact (PubMedArtifact.results), not in the prose content, so
# we read those structured rows rather than regex-parsing the LLM-facing text.
def _pubmed_results(messages: Iterable[BaseMessage]) -> list[dict]:
    rows: list[dict] = []
    for m in _tool_messages(messages, RES_TOOL_NAME):
        rows.extend(_parse_json_results(m))
    return rows


def _pubmed_recency_credit(results: list[dict]) -> float:
    """Return 0.0–1.0 based on how recent the newest article is."""
    years = [int(y) for r in results if isinstance(y := r.get("year"), (int, float))]
    if not years:
        return 0.0
    newest = max(years)
    current_year = datetime.now(timezone.utc).year
    age = max(0, current_year - newest)
    if age >= RES_RECENT_WINDOW_YEARS:
        return 0.0
    return 1.0 - (age / RES_RECENT_WINDOW_YEARS)


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
    tool_calls = _tool_messages(messages, CARD_TOOL_NAME)
    score = BASELINE_CONFIDENCE
    deltas: list[tuple[str, float]] = []

    if not tool_calls:
        deltas.append(("no guideline_search call", -CARD_MISSING_TOOL_PENALTY))
        final = _clip(score - CARD_MISSING_TOOL_PENALTY)
        _log_breakdown("cardiology", request, deltas, final)
        return final

    all_results = [r for tc in tool_calls for r in _parse_json_results(tc)]
    if not all_results:
        deltas.append(("empty guideline results", -CARD_EMPTY_RESULTS_PENALTY))
        final = _clip(score - CARD_EMPTY_RESULTS_PENALTY)
        _log_breakdown("cardiology", request, deltas, final)
        return final

    top = _max_score(all_results)
    strong_hits = sum(1 for r in all_results if (r.get("score") or 0) >= CARD_STRONG_HIT_SCORE_FLOOR)
    strong_credit = min(1.0, strong_hits / CARD_STRONG_HIT_FULL_CREDIT_AT)

    top_delta = CARD_TOP_SCORE_WEIGHT * top
    strong_delta = CARD_STRONG_HITS_WEIGHT * strong_credit
    score += top_delta
    score += strong_delta
    deltas.append((f"top BM25 score (top={top:.2f})", top_delta))
    deltas.append((f"strong hits ({strong_hits}/{CARD_STRONG_HIT_FULL_CREDIT_AT} ≥{CARD_STRONG_HIT_SCORE_FLOOR})", strong_delta))

    if _looks_like_abstention(_final_text(messages)):
        score -= CARD_ABSTENTION_PENALTY
        deltas.append(("abstention detected in answer", -CARD_ABSTENTION_PENALTY))

    final = _clip(score)
    _log_breakdown("cardiology", request, deltas, final)
    return final


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
        6. Did the clinician explicitly skip requested fields? Same hit as
           (5), since the agent answered without the data either way.
    """
    fass_calls = _tool_messages(messages, PHARM_TOOL_NAME)
    needs_input_calls = _tool_messages(messages, PHARM_NEEDS_INPUT_TOOL_NAME)
    score = BASELINE_CONFIDENCE
    deltas: list[tuple[str, float]] = []

    if not fass_calls:
        score -= PHARM_MISSING_TOOL_PENALTY
        deltas.append(("no fass_search call", -PHARM_MISSING_TOOL_PENALTY))
    else:
        sections = [s for tc in fass_calls for s in _parse_fass_chunks(str(tc.content))]
        if not sections:
            score -= PHARM_EMPTY_RESULTS_PENALTY
            deltas.append(("empty FASS results", -PHARM_EMPTY_RESULTS_PENALTY))
        else:
            hit_credit = min(1.0, len(sections) / PHARM_HIT_FULL_CREDIT_AT)
            hit_delta = PHARM_HIT_COUNT_WEIGHT * hit_credit
            score += hit_delta
            deltas.append((f"FASS hit count ({len(sections)}/{PHARM_HIT_FULL_CREDIT_AT})", hit_delta))
            if _section_matches_intent(request.query, sections):
                score += PHARM_SECTION_MATCH_BONUS
                deltas.append(("intent section match", PHARM_SECTION_MATCH_BONUS))

    if needs_input_calls:
        score -= PHARM_NEEDS_INPUT_PENALTY
        deltas.append(("requested clinical input", -PHARM_NEEDS_INPUT_PENALTY))

    if request.skipped_fields:
        score -= PHARM_SKIPPED_FIELDS_PENALTY
        deltas.append((f"clinician skipped fields ({len(request.skipped_fields)})", -PHARM_SKIPPED_FIELDS_PENALTY))

    final = _clip(score)
    _log_breakdown("pharmaceutical", request, deltas, final)
    return final


def research_confidence(messages: list[BaseMessage], request: AgentRequest) -> float:
    """Confidence in a research / evidence-grading answer.

    Signals:
        1. Did the agent query PubMed?
        2. Did PubMed return any articles (no sentinel string)?
        3. How many articles did it find, across all queries?
        4. How recent is the newest article?
    """
    pubmed_calls = _tool_messages(messages, RES_TOOL_NAME)
    score = BASELINE_CONFIDENCE
    deltas: list[tuple[str, float]] = []

    if not pubmed_calls:
        deltas.append(("no pubmed_tool call", -RES_MISSING_TOOL_PENALTY))
        final = _clip(score - RES_MISSING_TOOL_PENALTY)
        _log_breakdown("research", request, deltas, final)
        return final

    results = _pubmed_results(messages)

    if not results:
        deltas.append(("no PubMed results", -RES_NO_RESULTS_PENALTY))
        final = _clip(score - RES_NO_RESULTS_PENALTY)
        _log_breakdown("research", request, deltas, final)
        return final

    article_count = len(results)
    article_credit = min(1.0, article_count / RES_ARTICLE_FULL_CREDIT_AT)
    article_delta = RES_ARTICLE_COUNT_WEIGHT * article_credit
    recency_credit = _pubmed_recency_credit(results)
    recency_delta = RES_RECENCY_WEIGHT * recency_credit

    score += article_delta
    score += recency_delta
    deltas.append((f"article count ({article_count}/{RES_ARTICLE_FULL_CREDIT_AT})", article_delta))
    deltas.append((f"recency credit ({recency_credit:.2f})", recency_delta))

    final = _clip(score)
    _log_breakdown("research", request, deltas, final)
    return final
