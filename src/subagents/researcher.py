"""Scoped researcher subagent — handles one sub-question at a time.

The parent agent delegates distinct sub-questions to this subagent so
multiple angles of a topic can be researched with isolated context
windows instead of one long, cluttered conversation.
"""

from schemas.research import Source
from tools import web_search

from pydantic import BaseModel, Field


class ResearchFindings(BaseModel):
    """Structured findings returned by the researcher subagent."""

    sub_question: str = Field(description="The specific sub-question researched")
    answer: str = Field(description="Concise answer to the sub-question")
    sources: list[Source] = Field(description="Sources backing the answer")


researcher_subagent = {
    "name": "researcher",
    "description": (
        "Researches one specific sub-question using web_search and "
        "returns structured findings with sources. Delegate a single, "
        "narrow sub-question at a time — not the whole topic."
    ),
    "system_prompt": (
        "You are a focused researcher. Use web_search to answer the "
        "exact sub-question you were given. Do not go off-topic. "
        "Return your findings with real source URLs."
    ),
    "tools": [web_search],
    "response_format": ResearchFindings,
}
