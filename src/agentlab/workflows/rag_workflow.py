"""P2 domain workflow & specialist: ``RagWorkflow``, ``run_rag``, and ``RAG_SPECIALIST``."""

from typing import Any

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph

from agentlab.graphs.rag_graph import (
    DEFAULT_RAG_DESCRIPTION,
    RAG_SPEC,
    RagGraph,
    build_rag_graph,
)
from agentlab.schemas.input.rag_input_schema import RagInput
from agentlab.schemas.output.rag_output_schema import RagReport
from agentlab.schemas.output.specialist_output_schema import SpecialistResult
from agentlab.workflows.specialist_workflow import Workflow

__all__ = [
    "DEFAULT_RAG_DESCRIPTION",
    "RAG_SPECIALIST",
    "RagWorkflow",
    "build_rag_graph",
    "make_rag_specialist",
    "render_rag_report",
    "run_rag",
]


def render_rag_report(report: RagReport) -> str:
    """Render a ``RagReport`` as its answer text for ``SpecialistResult.to_text``."""
    return report.answer


class RagWorkflow(Workflow[RagInput, RagReport]):
    """Active Rung-2 RAG domain workflow wrapping ``RagGraph`` as a Runnable facade."""

    spec = RAG_SPEC

    def __init__(
        self,
        graph: RagGraph | CompiledStateGraph | Any | None = None,
        *,
        checkpointer: BaseCheckpointSaver | None = None,
    ) -> None:
        super().__init__(graph)
        self.checkpointer = checkpointer

    def build_default_graph(self) -> CompiledStateGraph:
        return build_rag_graph(checkpointer=self.checkpointer)

    def render(self, report: RagReport) -> str:
        return render_rag_report(report)

    def prepare_payload(self, inputs: RagInput) -> dict[str, Any]:
        return {
            "question": inputs.question,
            "search_query": inputs.question,
            "retries": 0,
        }


def run_rag(
    graph: RagGraph | CompiledStateGraph | Any,
    question: str,
) -> SpecialistResult[RagReport]:
    """Answer ``question`` with the RAG graph, on a fresh thread, as a specialist envelope."""
    return RagWorkflow(graph).invoke(question)["result"]


def make_rag_specialist(
    engine: RagGraph | CompiledStateGraph | Any = None,
) -> RagWorkflow:
    """Create a RAG Workflow bound to an engine or lazy default."""
    return RagWorkflow(engine)


RAG_SPECIALIST = RagWorkflow()
