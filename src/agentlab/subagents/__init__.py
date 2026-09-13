"""Subagent factories for delegation from DeepAgents coordinators."""

from agentlab.subagents.code_review_subagent import make_code_review_subagent
from agentlab.subagents.interpreter_subagent import make_interpreter_subagent
from agentlab.subagents.rag_subagent import make_rag_subagent
from agentlab.subagents.research_subagent import make_researcher_subagent

__all__ = [
    "make_code_review_subagent",
    "make_interpreter_subagent",
    "make_rag_subagent",
    "make_researcher_subagent",
]
