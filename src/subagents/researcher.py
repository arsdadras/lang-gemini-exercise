"""Scoped researcher subagent — handles one sub-question at a time.

The parent agent delegates distinct sub-questions to this subagent so
multiple angles of a topic can be researched with isolated context
windows instead of one long, cluttered conversation.
"""

from prompts import researcher_subagent_prompt
from schemas import ResearchFindings
from tools import web_search

researcher_subagent = {
    "name": "researcher",
    "description": (
        "Researches one specific sub-question using web_search and "
        "returns structured findings with sources. Delegate a single, "
        "narrow sub-question at a time — not the whole topic."
    ),
    "system_prompt": researcher_subagent_prompt,
    "tools": [web_search],
    "response_format": ResearchFindings,
}
