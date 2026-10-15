"""P2 domain workflow & specialist: ``RagWorkflow``, ``run_rag``, and ``RAG_SPECIALIST``."""

from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agentlab.graphs.rag_graph import RagGraph, build_rag_graph
from agentlab.schemas.input.rag_input_schema import RagInput
from agentlab.schemas.output.rag_output_schema import (
    RagGroundingVerdict,
    RagReport,
    RagRetrievalMode,
)
from agentlab.schemas.output.research_output_schema import SourceKind
from agentlab.schemas.output.specialist_output_schema import (
    Provenance,
    SpecialistResult,
    SpecialistStatus,
)
from agentlab.utils.subagent_util import new_delegation_config
from agentlab.workflows.specialist_workflow import (
    SpecialistSpec,
    Workflow,
    WorkflowOverallState,
)

DEFAULT_RAG_DESCRIPTION = (
    "Answers questions using the indexed chunk corpus, falling back "
    "to a live web search when nothing relevant is found locally."
)

# answer_source -> (status, reason, retrieval_mode, grounding_verdict)
_OUTCOMES: dict[
    str,
    tuple[SpecialistStatus, str, RagRetrievalMode, RagGroundingVerdict],
] = {
    "corpus": ("ok", "", "corpus", "grounded"),
    "web": (
        "partial",
        "The local corpus had nothing relevant; answered from the web.",
        "web",
        "none",
    ),
    "unverified": (
        "failed",
        "The corpus answer wasn't supported by its chunks.",
        "corpus",
        "unverified",
    ),
    "none": (
        "failed",
        "Nothing relevant in the corpus or on the web.",
        "none",
        "none",
    ),
}


def render_rag_report(report: RagReport) -> str:
    """Render a ``RagReport`` as its answer text for ``SpecialistResult.to_text``."""
    return report.answer


class RagWorkflowState(WorkflowOverallState[RagReport]):
    """Overall state for the RAG workflow graph."""

    question: str


class RagWorkflow(Workflow[RagInput, RagReport]):
    """Active Rung-2 RAG domain workflow wrapping ``RagGraph``."""

    spec = SpecialistSpec(
        name="rag",
        description=DEFAULT_RAG_DESCRIPTION,
        input_schema=RagInput,
        report_schema=RagReport,
    )

    def __init__(
        self,
        graph: RagGraph | CompiledStateGraph | Any = None,
    ) -> None:
        self._rag_graph = graph

    @property
    def rag_graph(self) -> CompiledStateGraph:
        if self._rag_graph is None:
            self._rag_graph = build_rag_graph()
        return self._rag_graph

    def render(self, report: RagReport) -> str:
        return render_rag_report(report)

    def build_graph(self) -> CompiledStateGraph:
        def _rag_step(state: RagWorkflowState) -> dict[str, Any]:
            question = state["question"]
            sub_state = self.rag_graph.invoke(
                {
                    "question": question,
                    "search_query": question,
                    "retries": 0,
                },
                config=new_delegation_config(),
            )
            source = sub_state.get("answer_source", "none")
            status, reason, retrieval_mode, grounding_verdict = _OUTCOMES.get(
                source,
                ("failed", "Unknown RAG outcome.", "none", "none"),
            )
            kind: SourceKind = "web" if source == "web" else "corpus"
            sources = [
                ref
                for ref in dict.fromkeys(
                    chunk.metadata.get("source", "")
                    for chunk in sub_state.get("chunks", [])
                )
                if ref
            ]
            answer = sub_state.get("answer")
            report = (
                RagReport(
                    answer=str(answer),
                    citations=sources,
                    retrieval_mode=retrieval_mode,
                    grounding_verdict=grounding_verdict,
                )
                if status != "failed" and answer is not None
                else None
            )
            problems = [reason] if reason else []
            provenance = (
                [Provenance(kind=kind, ref=ref) for ref in sources]
                if status != "failed"
                else []
            )
            return {
                "report": report,
                "problems": problems,
                "provenance": provenance,
            }

        graph = StateGraph(RagWorkflowState)
        graph.add_node("rag_step", _rag_step)
        graph.add_node("pack_result", self.pack_node)
        graph.add_edge(START, "rag_step")
        graph.add_edge("rag_step", "pack_result")
        graph.add_edge("pack_result", END)
        return graph.compile()


def run_rag(
    graph: RagGraph | CompiledStateGraph | Any,
    question: str,
) -> SpecialistResult[RagReport]:
    """Answer ``question`` with the RAG graph, on a fresh thread, as a specialist envelope."""
    return RagWorkflow(graph).run(question=question)


def make_rag_specialist(
    engine: RagGraph | CompiledStateGraph | Any = None,
) -> RagWorkflow:
    """Create a RAG Workflow bound to an engine or lazy default."""
    return RagWorkflow(engine)


RAG_SPECIALIST = RagWorkflow()
rag_workflow = RAG_SPECIALIST
