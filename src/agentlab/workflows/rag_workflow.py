"""P2 domain workflow & specialist: ``run_rag`` and ``RAG_SPECIALIST``."""

from langgraph.graph.state import CompiledStateGraph

from agentlab.graphs.rag_graph import build_rag_graph
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
from agentlab.utils.failure_util import failure_kind, failure_reason
from agentlab.utils.subagent_util import new_delegation_config
from agentlab.workflows.base import Specialist

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


def run_rag(
    graph: CompiledStateGraph,
    question: str,
) -> SpecialistResult[RagReport]:
    """Answer ``question`` with the RAG graph, on a fresh thread, as a specialist envelope.

    An external failure that outlasted the graph's retries becomes ``failed``; a bug raises.
    """
    try:
        state = graph.invoke(
            {
                "question": question,
                "search_query": question,
                "retries": 0,
            },
            config=new_delegation_config(),
        )
    except Exception as error:
        if failure_kind(error) is None:
            raise
        return SpecialistResult[RagReport](
            specialist="rag",
            status="failed",
            reason=failure_reason(error),
        )
    source = state.get("answer_source", "none")
    status, reason, retrieval_mode, grounding_verdict = _OUTCOMES[source]
    kind: SourceKind = "web" if source == "web" else "corpus"
    sources = [
        ref
        for ref in dict.fromkeys(
            chunk.metadata.get("source", "") for chunk in state.get("chunks", [])
        )
        if ref
    ]
    answer = state.get("answer")
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
    return SpecialistResult[RagReport](
        specialist="rag",
        status=status,
        reason=reason,
        output=report,
        provenance=[Provenance(kind=kind, ref=ref) for ref in sources]
        if status != "failed"
        else [],
    )


from typing import Any


def make_rag_specialist(
    engine: CompiledStateGraph | None = None,
) -> Specialist[RagInput, RagReport]:
    """Create a RAG Specialist pre-bound to an engine or lazy default."""

    def run_bound(
        task: RagInput | str | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> SpecialistResult[RagReport]:
        resolved_engine = engine if engine is not None else build_rag_graph()
        data = task if task is not None else kwargs
        if isinstance(data, RagInput):
            question = data.question
        elif isinstance(data, dict):
            question = str(data["question"])
        else:
            question = str(data)
        return run_rag(resolved_engine, question, **kwargs)

    return Specialist[RagInput, RagReport](
        name="rag",
        description=DEFAULT_RAG_DESCRIPTION,
        input_schema=RagInput,
        report_schema=RagReport,
        run=run_bound,
        render=render_rag_report,
    )


RAG_SPECIALIST = make_rag_specialist()
