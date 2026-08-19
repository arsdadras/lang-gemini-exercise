"""Delegated subagents for the research pipeline."""

<<<<<<< HEAD
This package is a placeholder for specialised sub-agents that the
main agent can delegate tasks to.
"""

# pyrefly: ignore [missing-import]
from .subagents import topic_researcher

__all__ = [topic_researcher]
=======
from subagents.researcher import ResearchFindings, researcher_subagent

__all__ = ["ResearchFindings", "researcher_subagent"]
>>>>>>> ac268283fa2050850887180009b388e00afa28e8
