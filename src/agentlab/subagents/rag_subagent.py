"""P2 subagent adapter over ``workflows/rag_workflow.py`` (ADR-0033)."""

from typing import Any

from deepagents import CompiledSubAgent

from agentlab.graphs.rag_graph import build_rag_graph
from agentlab.utils.subagent_util import specialist_subagent
from agentlab.workflows.rag_workflow import (
    DEFAULT_RAG_DESCRIPTION,
    RAG_SPECIALIST,
    RAG_SPECIALIST_SPEC,
    render_rag_report,
    run_rag,
)

DEFAULT_RAG_SUBAGENT_NAME = "rag_subagent"
DEFAULT_RAG_SUBAGENT_DESCRIPTION = DEFAULT_RAG_DESCRIPTION


def make_rag_subagent(
    graph: Any = None,
    *,
    name: str = DEFAULT_RAG_SUBAGENT_NAME,
    description: str = DEFAULT_RAG_SUBAGENT_DESCRIPTION,
) -> CompiledSubAgent:
    """Wrap a compiled RAG graph (default: ``build_rag_graph()``) as a ``CompiledSubAgent``."""
    rag_graph = graph if graph is not None else build_rag_graph()

    return specialist_subagent(
        name,
        description,
        lambda task: run_rag(rag_graph, task),
        render=render_rag_report,
    )


__all__ = [
    "DEFAULT_RAG_SUBAGENT_DESCRIPTION",
    "DEFAULT_RAG_SUBAGENT_NAME",
    "RAG_SPECIALIST",
    "RAG_SPECIALIST_SPEC",
    "make_rag_subagent",
    "render_rag_report",
    "run_rag",
]
