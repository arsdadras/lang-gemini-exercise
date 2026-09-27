"""Tavily web search tool factory, and an adapter that surfaces the errors it hides."""

import re
from typing import Any

from langchain_tavily import TavilySearch

WEB_SEARCH_TOOL_NAME = "web_search"

_STATUS_PREFIX = re.compile(r"Error (\d{3})")


class WebSearchError(RuntimeError):
    """The search provider failed a request; ``status_code`` is its HTTP status when known."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def make_web_search_tool(max_results: int = 5) -> TavilySearch:
    """Build the web search tool; reads ``TAVILY_API_KEY`` from the environment."""
    return TavilySearch(
        max_results=max_results,
        name=WEB_SEARCH_TOOL_NAME,
        description=(
            "Search the web for current, factual information about any topic. "
            "Returns a list of relevant results with title, URL, and snippet. "
            "Use this whenever the user asks for research on a topic."
        ),
    )


def search_results(response: Any) -> list[dict[str, Any]]:
    """The results in a web search tool's output, raising the error it returned instead.

    ``TavilySearch`` returns a failed request as ``{"error": exc}`` and "no results" as a
    text message. A caller that only reads ``results`` would mistake an outage for an
    empty web. Model callers keep the tool as it is: the model reads the error text.
    """
    if isinstance(response, str):
        return []
    error = response.get("error")
    if isinstance(error, Exception):
        status = _STATUS_PREFIX.match(str(error))
        raise WebSearchError(str(error), int(status[1]) if status else None) from error
    return response.get("results", [])
