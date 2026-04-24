from __future__ import annotations

from langchain_community.tools.pubmed.tool import PubmedQueryRun
from langchain_community.utilities.pubmed import PubMedAPIWrapper
from langchain_core.tools import tool

_TOP_K_RESULTS      = 5     # balance between coverage and latency
_MAX_CONTENT_CHARS  = 2000  # enough for a full abstract

_pubmed_run = PubmedQueryRun(api_wrapper=PubMedAPIWrapper(top_k_results=_TOP_K_RESULTS, doc_content_chars_max=_MAX_CONTENT_CHARS))

# TODO: parse individual PMIDs from result text for per-article citations


@tool
def pubmed_tool(query: str) -> str:
    """Search PubMed for clinical evidence. Use short, focused queries of 2-4 key terms.
    Good: "metoprolol renal impairment", "beta blockers heart failure CKD"
    Bad: "metoprolol heart failure renal impairment guidelines RCT systematic review"
    Returns titles, abstracts, and publication dates.
    """
    return _pubmed_run.run(query)
