"""Web search tool for the research agent."""

from langchain_community.tools.tavily_search import TavilySearchResults

web_search = TavilySearchResults(
    max_results=5,
    name="web_search",
    description=(
        "Search the web for current, factual information about any topic. "
        "Returns a list of relevant results, each with a title, URL, and "
        "content snippet. Use this whenever the user asks for research, "
        "current events, or facts that may not be in your training data."
    ),
)
