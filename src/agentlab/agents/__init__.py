"""Agent factories: each builds a fully composed agent with no run loop of its own.

Apps call these factories at startup (the composition root); nothing is built at
import time.
"""

from agentlab.agents.coding_coordinator_agent import make_coding_coordinator_agent
from agentlab.agents.interpreter_agent import make_interpreter_agent
from agentlab.agents.personal_assistant_agent import make_personal_assistant_agent
from agentlab.agents.repo_insight_agent import make_repo_insight_agent
from agentlab.agents.web_researcher_agent import make_web_researcher_agent

__all__ = [
    "make_coding_coordinator_agent",
    "make_interpreter_agent",
    "make_personal_assistant_agent",
    "make_repo_insight_agent",
    "make_web_researcher_agent",
]
