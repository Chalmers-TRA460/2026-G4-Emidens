from __future__ import annotations

import time
from collections import OrderedDict
from typing import Any

import httpx
import xmltodict
from langchain_core.tools import tool

from agents._artifacts import (
    PubMedAbstractSection,
    PubMedArtifact,
    PubMedItem,
)
from settings import settings

_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
_EFETCH_URL  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
_PUBMED_URL  = "https://pubmed.ncbi.nlm.nih.gov"

_TOP_K       = 5
_TIMEOUT_S   = 15.0
_CACHE_TTL_S = 86_400
_CACHE_MAX   = 200

_CACHE: OrderedDict[str, tuple[float, tuple[str, PubMedArtifact]]] = OrderedDict()


def _cache_key(query: str) -> str:
    return query.strip().lower()


def _cache_get(query: str) -> tuple[str, PubMedArtifact] | None:
    key = _cache_key(query)
    entry = _CACHE.get(key)
    if entry is None:
        return None
    ts, value = entry
    if time.time() - ts > _CACHE_TTL_S:
        _CACHE.pop(key, None)
        return None
    _CACHE.move_to_end(key)
    return value


def _cache_set(query: str, value: tuple[str, PubMedArtifact]) -> None:
    key = _cache_key(query)
    _CACHE[key] = (time.time(), value)
    _CACHE.move_to_end(key)
    while len(_CACHE) > _CACHE_MAX:
        _CACHE.popitem(last=False)


def _esearch(client: httpx.Client, query: str, api_key: str) -> list[str]:
    response = client.get(_ESEARCH_URL, params={
        "db": "pubmed",
        "term": query,
        "retmax": _TOP_K,
        "retmode": "json",
        "api_key": api_key,
    })
    response.raise_for_status()
    return response.json().get("esearchresult", {}).get("idlist", []) or []


def _efetch(client: httpx.Client, pmids: list[str], api_key: str) -> str:
    response = client.get(_EFETCH_URL, params={
        "db": "pubmed",
        "id": ",".join(pmids),
        "rettype": "abstract",
        "retmode": "xml",
        "api_key": api_key,
    })
    response.raise_for_status()
    return response.text


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _text(node: Any) -> str:
    """xmltodict surfaces text either as a plain string or as {'#text': str, '@attr': ...}."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        return str(node.get("#text", ""))
    return str(node)


def _parse_year(date_node: Any) -> int | None:
    if not isinstance(date_node, dict):
        return None
    raw = date_node.get("Year") or date_node.get("MedlineDate")
    if raw is None:
        return None
    digits = "".join(c for c in str(raw) if c.isdigit())[:4]
    return int(digits) if len(digits) == 4 else None


def _parse_authors(author_list_node: Any) -> list[str]:
    if not isinstance(author_list_node, dict):
        return []
    authors: list[str] = []
    for author in _as_list(author_list_node.get("Author")):
        if not isinstance(author, dict):
            continue
        last = author.get("LastName")
        initials = author.get("Initials") or author.get("ForeName")
        collective = author.get("CollectiveName")
        if last:
            authors.append(f"{last} {initials}".strip() if initials else str(last))
        elif collective:
            authors.append(_text(collective))
    return authors


def _parse_abstract(abstract_node: Any) -> list[PubMedAbstractSection]:
    if not isinstance(abstract_node, dict):
        return []
    sections: list[PubMedAbstractSection] = []
    for piece in _as_list(abstract_node.get("AbstractText")):
        if isinstance(piece, dict):
            label = piece.get("@Label")
            text = _text(piece)
        else:
            label = None
            text = _text(piece)
        if text:
            sections.append(PubMedAbstractSection(label=label, text=text))
    return sections


def _parse_article(art: dict[str, Any]) -> PubMedItem | None:
    citation = art.get("MedlineCitation") or {}
    if not isinstance(citation, dict):
        return None
    article = citation.get("Article") or {}
    if not isinstance(article, dict):
        return None

    pmid = _text(citation.get("PMID"))
    if not pmid:
        return None

    title = _text(article.get("ArticleTitle"))
    journal_node = article.get("Journal") or {}
    journal = _text(journal_node.get("Title")) if isinstance(journal_node, dict) else None

    pub_date = None
    if isinstance(journal_node, dict):
        issue = journal_node.get("JournalIssue") or {}
        if isinstance(issue, dict):
            pub_date = issue.get("PubDate")
    year = _parse_year(pub_date)

    authors = _parse_authors(article.get("AuthorList"))
    abstract = _parse_abstract(article.get("Abstract"))

    return PubMedItem(
        pmid=pmid,
        title=title or "(no title)",
        year=year,
        journal=journal or None,
        authors=authors,
        abstract=abstract,
        url=f"{_PUBMED_URL}/{pmid}/",
    )


def _parse_articles(xml_text: str) -> list[PubMedItem]:
    parsed = xmltodict.parse(xml_text)
    article_set = parsed.get("PubmedArticleSet") or {}
    items: list[PubMedItem] = []
    for raw in _as_list(article_set.get("PubmedArticle") if isinstance(article_set, dict) else None):
        if not isinstance(raw, dict):
            continue
        item = _parse_article(raw)
        if item is not None:
            items.append(item)
    return items


def _format_section(s: PubMedAbstractSection) -> str:
    if s.label:
        return f"  {s.label}: {s.text}"
    return f"  {s.text}"


def _format_authors(authors: list[str]) -> str:
    if not authors:
        return ""
    if len(authors) > 6:
        return ", ".join(authors[:6]) + ", et al."
    return ", ".join(authors)


def _format_item(idx: int, item: PubMedItem) -> str:
    year_str = str(item.year) if item.year is not None else "—"
    header = f"[{idx}] PMID {item.pmid} ({year_str}) — {item.title}"
    authors = _format_authors(item.authors)
    abstract_block = (
        "\n".join(_format_section(s) for s in item.abstract)
        if item.abstract else "  (no abstract)"
    )
    parts: list[str | None] = [
        header,
        f"Authors: {authors}" if authors else None,
        item.journal,
        "Abstract:",
        abstract_block,
    ]
    return "\n".join(p for p in parts if p)


def _build_response(query: str, items: list[PubMedItem]) -> tuple[str, PubMedArtifact]:
    artifact = PubMedArtifact(query=query, results=items)
    if not items:
        return (f"No PubMed results for query: {query!r}.", artifact)
    content = "\n\n".join(_format_item(i + 1, item) for i, item in enumerate(items))
    return (content, artifact)


@tool(response_format="content_and_artifact")
def pubmed_tool(query: str) -> tuple[str, PubMedArtifact]:
    """Search PubMed for clinical evidence. Use short, focused queries of 2-4 key terms.
    Good: "metoprolol renal impairment", "beta blockers heart failure CKD"
    Bad:  "metoprolol heart failure renal impairment guidelines RCT systematic review"
    Returns titles, abstracts (with Background/Methods/Results/Conclusions labels when present),
    journals, authors, and publication years for the top 5 matches.
    """
    cached = _cache_get(query)
    if cached is not None:
        return cached

    api_key = settings.ncbi_api_key.get_secret_value()
    try:
        with httpx.Client(timeout=_TIMEOUT_S) as client:
            pmids = _esearch(client, query, api_key)
            if not pmids:
                response = _build_response(query, [])
                _cache_set(query, response)
                return response
            xml_text = _efetch(client, pmids, api_key)
    except httpx.HTTPStatusError as e:
        empty = PubMedArtifact(query=query, results=[])
        if e.response.status_code == 429:
            return (
                f"PubMed rate-limit hit; skipping literature search for query: {query!r}.",
                empty,
            )
        return (
            f"PubMed returned HTTP {e.response.status_code} for query: {query!r}.",
            empty,
        )
    except (httpx.TimeoutException, httpx.RequestError):
        empty = PubMedArtifact(query=query, results=[])
        return (
            f"PubMed unavailable (timeout/connection error) for query: {query!r}.",
            empty,
        )

    items = _parse_articles(xml_text)
    response = _build_response(query, items)
    _cache_set(query, response)
    return response
