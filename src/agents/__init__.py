"""Composed, ready-to-invoke agent definitions.

Each module here builds a fully-assembled agent (model, prompt, tools,
subagents, middleware, checkpointer) with no execution loop of its own.
`apps/` modules import from here and add the run loop for a specific use case.
"""

from agents.coding_coordinator_agent import (
    coding_coordinator_agent,
    make_coding_coordinator_agent,
)
from agents.interpreter_agent import interpreter_agent, make_interpreter_agent
from agents.personal_assistant_agent import (
    make_personal_assistant_agent,
    personal_assistant_agent,
    personal_assistant_manifest,
)
from agents.repo_insight_agent import repo_insight_agent
from agents.web_researcher_agent import web_researcher_agent

__all__ = [
    "coding_coordinator_agent",
    "interpreter_agent",
    "make_coding_coordinator_agent",
    "make_interpreter_agent",
    "make_personal_assistant_agent",
    "personal_assistant_agent",
    "personal_assistant_manifest",
    "repo_insight_agent",
    "web_researcher_agent",
]
