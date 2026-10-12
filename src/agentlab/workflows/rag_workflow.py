"""P2 domain workflow & specialist: ``run_rag`` and ``RAG_SPECIALIST_SPEC``."""

from typing import Any, overload

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
    Specialist,
    SpecialistResult,
    SpecialistStatus,
)
from agentlab.utils.failure_util import failure_kind, failure_reason
from agentlab.utils.subagent_util import new_delegation_config

RAG_SPECIALIST = "rag"
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


@overload
def run_rag(
    question: str,
    *,
    graph: Any = None,
) -> SpecialistResult[RagReport]: ...


@overload
def run_rag(
    graph: Any,
    question: str,
    /,
) -> SpecialistResult[RagReport]: ...


def run_rag(*args: Any, **kwargs: Any) -> SpecialistResult[RagReport]:
    """Answer ``question`` with the RAG graph, on a fresh thread, as a specialist envelope.

    Supports both ``run_rag(graph, question)`` and ``run_rag(question, graph=...)``.
    An external failure that outlasted the graph's retries becomes ``failed``; a bug raises.
    """
    graph_or_question = args[0] if len(args) >= 1 else None
    pos_question = args[1] if len(args) >= 2 else kwargs.get("question")
    kw_graph = kwargs.get("graph")

    if isinstance(graph_or_question, str):
        resolved_question = graph_or_question
        resolved_graph = kw_graph if kw_graph is not None else build_rag_graph()
    elif graph_or_question is None and isinstance(pos_question, str):
        resolved_question = pos_question
        resolved_graph = kw_graph if kw_graph is not None else build_rag_graph()
    else:
        if not isinstance(pos_question, str):
            msg = "run_rag requires a question string"
            raise TypeError(msg)
        resolved_graph = graph_or_question
        resolved_question = pos_question

    if resolved_graph is None:
        resolved_graph = build_rag_graph()

    try:
        state = resolved_graph.invoke(
            {
                "question": resolved_question,
                "search_query": resolved_question,
                "retries": 0,
            },
            config=new_delegation_config(),
        )
    except Exception as error:
        if failure_kind(error) is None:
            raise
        return SpecialistResult[RagReport](
            specialist=RAG_SPECIALIST,
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
        specialist=RAG_SPECIALIST,
        status=status,
        reason=reason,
        output=report,
        provenance=[Provenance(kind=kind, ref=ref) for ref in sources]
        if status != "failed"
        else [],
    )


RAG_SPECIALIST_SPEC = Specialist[RagInput, RagReport](
    name=RAG_SPECIALIST,
    description=DEFAULT_RAG_DESCRIPTION,
    input_schema=RagInput,
    report_schema=RagReport,
    run=run_rag,
    render=render_rag_report,
)
