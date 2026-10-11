"""``academic_search``: research papers for a query, each with its text (R1 topic 3).

Exa's research-paper index (arXiv, journals, conference papers) returns each paper's text with
the result, so the agent reads a paper in the same call that finds it, and the claim check sees
exactly what the agent saw: up to ``ACADEMIC_TEXT_CHARS`` of each paper, carried as
``SourceDocument`` artifacts of kind ``academic``. The caller's domain filters drop papers outside
them, as they do for web pages.

A failed search goes back to the model as text (``handle_tool_error``); the failure still
classifies like any external failure (``WebSearchError`` carries the HTTP status).
"""

import os
from collections.abc import Sequence
from typing import Any

import requests
from langchain_core.tools import StructuredTool, ToolException

from agentlab.configs.research_config import (
    ACADEMIC_RESULTS,
    ACADEMIC_TEXT_CHARS,
    EXA_KEY_ENV,
    EXA_SEARCH_URL,
)
from agentlab.configs.timeouts_config import ACADEMIC_SEARCH_TIMEOUT_SECONDS
from agentlab.schemas.output.research_output_schema import SourceDocument
from agentlab.tools.read_page_tool import domain_allowed
from agentlab.tools.research_source_tool import as_artifact, format_documents
from agentlab.tools.web_search_tool import WebSearchError

ACADEMIC_SEARCH_TOOL_NAME = "academic_search"


def search_papers(query: str) -> list[SourceDocument]:
    """Research papers matching ``query``, each with the first part of its text."""
    key = os.getenv(EXA_KEY_ENV)
    if not key:
        msg = f"academic_search needs {EXA_KEY_ENV} in the environment."
        raise WebSearchError(msg)
    response = requests.post(
        EXA_SEARCH_URL,
        json={
            "query": query,
            "numResults": ACADEMIC_RESULTS,
            "category": "research paper",
            "contents": {"text": {"maxCharacters": ACADEMIC_TEXT_CHARS}},
        },
        headers={"x-api-key": key, "Content-Type": "application/json"},
        timeout=ACADEMIC_SEARCH_TIMEOUT_SECONDS,
    )
    if response.status_code != 200:
        msg = f"Error {response.status_code}: the academic search failed."
        raise WebSearchError(msg, response.status_code)
    results: list[dict[str, Any]] = response.json().get("results", [])
    return [
        SourceDocument(
            url=result["url"],
            title=result.get("title") or "",
            kind="academic",
            text=result["text"],
        )
        for result in results
        if result.get("url") and result.get("text")
    ]


def make_academic_search_tool(
    include_domains: Sequence[str] = (), exclude_domains: Sequence[str] = ()
) -> StructuredTool:
    """Build the academic search tool; reads ``EXA_API_KEY`` from the environment per call."""

    def academic_search(query: str) -> tuple[str, list[dict[str, Any]]]:
        """Find research papers (preprints, journal and conference papers) on a query and
        read the first part of each. Use it for studies, benchmarks, methods, and findings
        published as research; cite a paper by the URL it returns."""
        try:
            papers = search_papers(query)
        except WebSearchError as error:
            raise ToolException(str(error)) from error
        papers = [
            paper
            for paper in papers
            if domain_allowed(paper.url, include_domains, exclude_domains)
        ]
        if not papers:
            return "No papers found. Try a different query.", []
        return format_documents(papers), as_artifact(papers)

    return StructuredTool.from_function(
        academic_search,
        name=ACADEMIC_SEARCH_TOOL_NAME,
        handle_tool_error=True,
        response_format="content_and_artifact",
    )
