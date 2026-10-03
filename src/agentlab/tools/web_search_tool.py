"""Tavily web search tool factory, and an adapter that surfaces the errors it hides."""

import json
import re
from typing import Any

import aiohttp
import requests
from langchain_tavily import TavilySearch
from langchain_tavily._utilities import TAVILY_API_URL, TavilySearchAPIWrapper
from pydantic import SecretStr

from agentlab.configs.timeouts_config import WEB_SEARCH_TIMEOUT_SECONDS

WEB_SEARCH_TOOL_NAME = "web_search"

_STATUS_PREFIX = re.compile(r"Error (\d{3})")


class WebSearchError(RuntimeError):
    """The search provider failed a request; ``status_code`` is its HTTP status when known."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class _TimeoutSearchWrapper(TavilySearchAPIWrapper):
    """Tavily's search wrapper with a request timeout.

    langchain-tavily 0.2.18 calls ``requests.post`` with no timeout (a silent server hangs the
    caller forever) and opens an ``aiohttp`` session on its five-minute default, and the
    wrapper has no setting for either. These overrides send the same request with a timeout.
    Drop the class once the library takes one; ``tests/test_timeouts.py`` shows what to check.
    """

    timeout_seconds: float = WEB_SEARCH_TIMEOUT_SECONDS

    def _request(
        self, params: dict[str, Any]
    ) -> tuple[str, dict[str, Any], dict[str, str]]:
        key: SecretStr = self.tavily_api_key
        headers = {
            "Authorization": f"Bearer {key.get_secret_value()}",
            "Content-Type": "application/json",
            "X-Client-Source": "langchain-tavily",
        }
        body = {name: value for name, value in params.items() if value is not None}
        return f"{self.api_base_url or TAVILY_API_URL}/search", body, headers

    def raw_results(self, **params: Any) -> dict[str, Any]:  # type: ignore[override]
        url, body, headers = self._request(params)
        response = requests.post(
            url, json=body, headers=headers, timeout=self.timeout_seconds
        )
        if response.status_code != 200:
            detail = response.json().get("detail", {})
            error_message = (
                detail.get("error") if isinstance(detail, dict) else "Unknown error"
            )
            raise ValueError(f"Error {response.status_code}: {error_message}")
        return response.json()

    async def raw_results_async(self, **params: Any) -> dict[str, Any]:  # type: ignore[override]
        url, body, headers = self._request(params)
        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
        async with (
            aiohttp.ClientSession(timeout=timeout) as session,
            session.post(url, json=body, headers=headers) as response,
        ):
            if response.status != 200:
                raise ValueError(f"Error {response.status}: {response.reason}")
            return json.loads(await response.text())


def make_web_search_tool(max_results: int = 5) -> TavilySearch:
    """Build the web search tool; reads ``TAVILY_API_KEY`` from the environment."""
    return TavilySearch(
        api_wrapper=_TimeoutSearchWrapper(),  # type: ignore[call-arg]
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
