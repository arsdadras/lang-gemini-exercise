"""``read_page``: the text of one web page, so claims are checked against pages, not snippets.

A search result is a snippet the provider chose; a claim is checked against the page it cites.
The tool returns the page's URL on the first line and its text after it, cut to
``MAX_PAGE_CHARS``, which is also how ``pages_read`` finds the pages an agent read in its
message history. A failed read goes back to the model as text (``handle_tool_error``), so the
agent can try another page; the failure still classifies like any external failure
(``WebSearchError`` carries the HTTP status).
"""

import os
from collections.abc import Sequence
from typing import Any
from urllib.parse import urlparse

import requests
from langchain_core.messages import AnyMessage, ToolMessage
from langchain_core.tools import StructuredTool, ToolException
from langchain_tavily._utilities import TAVILY_API_URL

from agentlab.configs.research_config import MAX_PAGE_CHARS
from agentlab.configs.timeouts_config import WEB_SEARCH_TIMEOUT_SECONDS
from agentlab.tools.web_search_tool import WebSearchError

READ_PAGE_TOOL_NAME = "read_page"
TAVILY_KEY_ENV = "TAVILY_API_KEY"


def read_page(url: str) -> str:
    """Read the full text of one web page you found with web_search (cut to its first part)."""
    key = os.getenv(TAVILY_KEY_ENV)
    if not key:
        msg = f"read_page needs {TAVILY_KEY_ENV} in the environment."
        raise WebSearchError(msg)
    response = requests.post(
        f"{TAVILY_API_URL}/extract",
        json={"urls": [url], "extract_depth": "basic", "format": "text"},
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "X-Client-Source": "agentlab",
        },
        timeout=WEB_SEARCH_TIMEOUT_SECONDS,
    )
    if response.status_code != 200:
        msg = f"Error {response.status_code}: the page reader failed."
        raise WebSearchError(msg, response.status_code)
    results: list[dict[str, Any]] = response.json().get("results", [])
    if not results or not results[0].get("raw_content"):
        msg = f"Could not read {url}: no text came back. Try another page."
        raise WebSearchError(msg)
    return f"{url}\n\n{results[0]['raw_content'][:MAX_PAGE_CHARS]}"


def _read_or_report(url: str) -> str:
    """``read_page`` for a model: a failed read becomes a ``ToolException`` the agent sees as text.

    ``from error`` keeps the original on the chain, so the failure still classifies.
    """
    try:
        return read_page(url)
    except WebSearchError as error:
        raise ToolException(str(error)) from error


def domain_allowed(
    url: str, include: Sequence[str] = (), exclude: Sequence[str] = ()
) -> bool:
    """Whether ``url``'s host is inside ``include`` (when given) and outside ``exclude``."""
    host = (urlparse(url).hostname or "").lower()

    def matches(domain: str) -> bool:
        domain = domain.lower().lstrip(".")
        return host == domain or host.endswith(f".{domain}")

    if any(matches(d) for d in exclude):
        return False
    return not include or any(matches(d) for d in include)


def make_read_page_tool(
    include_domains: Sequence[str] = (), exclude_domains: Sequence[str] = ()
) -> StructuredTool:
    """Build the page reading tool; reads ``TAVILY_API_KEY`` from the environment per call.

    The caller's domain filters apply to reading too: a page the search would never return
    can't be read from a URL the model guessed.
    """

    def read_allowed(url: str) -> str:
        if not domain_allowed(url, include_domains, exclude_domains):
            msg = f"{url} is outside the domains this research may read. Pick another page."
            raise ToolException(msg)
        return _read_or_report(url)

    return StructuredTool.from_function(
        read_allowed,
        name=READ_PAGE_TOOL_NAME,
        description=read_page.__doc__,
        handle_tool_error=True,
    )


def pages_read(messages: list[AnyMessage]) -> dict[str, str]:
    """The pages an agent read: URL to text, from its ``read_page`` results in ``messages``."""
    pages: dict[str, str] = {}
    for message in messages:
        if (
            isinstance(message, ToolMessage)
            and message.name == READ_PAGE_TOOL_NAME
            and message.status != "error"
            and isinstance(message.content, str)
        ):
            url, _, text = message.content.partition("\n\n")
            pages[url.strip()] = text
    return pages
