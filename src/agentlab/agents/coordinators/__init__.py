"""Coordinators: deep agents built to orchestrate role agents toward a composite goal.

A coordinator has no narrow task of its own. It plans and delegates to role agents through
their subagent (or tool) versions, and grows a large harness: many subagents and tools,
memory, and long-lived skills (ADR-0030). Role agents live one level up, in ``agents/``.
"""

from agentlab.agents.coordinators.coding_coordinator_agent import (
    make_coding_coordinator_agent,
)
from agentlab.agents.coordinators.repo_insight_agent import make_repo_insight_agent

__all__ = ["make_coding_coordinator_agent", "make_repo_insight_agent"]
