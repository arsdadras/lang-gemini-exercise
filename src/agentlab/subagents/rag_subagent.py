"""P2 subagent adapter over ``workflows/rag_workflow.py`` (ADR-0033)."""

from deepagents import CompiledSubAgent
from langgraph.graph.state import CompiledStateGraph

from agentlab.workflows.rag_workflow import (
    DEFAULT_RAG_DESCRIPTION,
    RAG_SPECIALIST,
)

DEFAULT_RAG_SUBAGENT_NAME = "rag_subagent"
DEFAULT_RAG_SUBAGENT_DESCRIPTION = DEFAULT_RAG_DESCRIPTION


def make_rag_subagent(
    graph: CompiledStateGraph | None = None,
    *,
    name: str = DEFAULT_RAG_SUBAGENT_NAME,
    description: str = DEFAULT_RAG_SUBAGENT_DESCRIPTION,
) -> CompiledSubAgent:
    """Wrap a compiled RAG graph (default: ``build_rag_graph()``) as a ``CompiledSubAgent``."""
    return RAG_SPECIALIST.as_subagent(
        graph,
        name=name,
        description=description,
    )
