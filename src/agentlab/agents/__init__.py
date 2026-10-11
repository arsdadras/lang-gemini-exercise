"""Role agents: each builds one focused agent with its own harness and no run loop.

A role agent does one job and may delegate only for an internal need. Coordinators, which
orchestrate role agents toward a composite goal, live in ``agents/coordinators/`` (ADR-0030).
Apps call these factories at startup (the composition root); nothing is built at import time.
"""

from agentlab.agents.interpreter_agent import make_interpreter_agent
from agentlab.agents.personal_assistant_agent import make_personal_assistant_agent
from agentlab.agents.researcher_agent import make_researcher_agent

__all__ = [
    "make_interpreter_agent",
    "make_personal_assistant_agent",
    "make_researcher_agent",
]
