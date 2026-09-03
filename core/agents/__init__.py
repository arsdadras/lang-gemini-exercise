"""Composed, ready-to-invoke agent definitions.

Each module here builds a fully-assembled agent (model, prompt, tools,
subagents, middleware, checkpointer) with no execution loop of its own.
`apps/` modules import from here and add the run loop for a specific use case.
"""

from agents.repo_insight import repo_insight_agent
from agents.web_researcher import web_researcher_agent

__all__ = ["repo_insight_agent", "web_researcher_agent"]
