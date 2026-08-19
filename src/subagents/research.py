"""Subagent configuration for scoped topic research."""

from tools import web_search


topic_researcher = {
    "name": "topic_researcher",
    "description": (
        "Researches a single, narrow sub-topic using web search and "
        "returns a focused summary with sources. Delegate to this "
        "subagent when a research topic has multiple distinct "
        "sub-questions that should be investigated independently."
    ),
    "system_prompt": (
        "You are a focused sub-topic researcher. You receive one "
        "narrow research question. Use `web_search` to investigate it "
        "thoroughly, then return a concise summary with the source "
        "URLs you used. Do not go beyond the scope of the question you "
        "were given."
    ),
    "tools": [web_search],
}
