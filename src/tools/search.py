"""Web search tool for the research agent, built on langchain-tavily."""

from langchain_tavily import TavilySearch

web_search = TavilySearch(
    max_results=5,
    name="web_search",
    description=(
        "Search the web for current, factual information about any topic. "
        "Returns a list of relevant results, each with a title, URL, and "
        "content snippet. Use this whenever the user asks for research, "
        "current events, or facts that may not be in your training data."
    ),
)
