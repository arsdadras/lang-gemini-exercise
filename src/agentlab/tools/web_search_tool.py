"""Tavily web search tool factory."""

from langchain_tavily import TavilySearch

WEB_SEARCH_TOOL_NAME = "web_search"


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
