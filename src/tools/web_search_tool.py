"""web search tool using Tavily"""

from __future__ import annotations

from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()

web_search = TavilySearch(
    max_results=5,
    name="web_search",
    description=(
        "Search the web for current, factual information about any topic. "
        "Returns a list of relevant results with title, URL, and snippet. "
        "Use this whenever the user asks for research on a topic."
    ),
)
