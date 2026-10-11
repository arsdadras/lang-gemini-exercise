"""P2's boundary: ``run_rag`` returns the specialist envelope; the adapter serves DeepAgents coordinators."""

from deepagents import CompiledSubAgent

from agentlab.graphs.rag_graph import RagGraph, build_rag_graph
from agentlab.schemas.output.research_output_schema import SourceKind
from agentlab.schemas.output.specialist_output_schema import (
    Provenance,
    SpecialistResult,
    SpecialistStatus,
)
from agentlab.utils.failure_util import failure_kind, failure_reason
from agentlab.utils.subagent_util import (
    new_delegation_config,
    specialist_subagent,
)

RAG_SPECIALIST = "rag"
DEFAULT_RAG_SUBAGENT_NAME = "rag_subagent"
DEFAULT_RAG_SUBAGENT_DESCRIPTION = (
    "Answers questions using the indexed chunk corpus, falling back "
    "to a live web search when nothing relevant is found locally."
)

# answer_source -> (status, reason): the graph records where its answer came from; the
# boundary turns that fact into what a caller needs to decide.
_OUTCOMES: dict[str, tuple[SpecialistStatus, str]] = {
    "corpus": ("ok", ""),
    "web": ("partial", "The local corpus had nothing relevant; answered from the web."),
    "unverified": ("failed", "The corpus answer wasn't supported by its chunks."),
    "none": ("failed", "Nothing relevant in the corpus or on the web."),
}


def run_rag(graph: RagGraph, question: str) -> SpecialistResult[str]:
    """Answer ``question`` with the RAG graph, on a fresh thread, as a specialist envelope.

    An external failure that outlasted the graph's retries becomes ``failed``; a bug raises.
    """
    try:
        state = graph.invoke(
            {"question": question, "search_query": question, "retries": 0},
            config=new_delegation_config(),
        )
    except Exception as error:
        if failure_kind(error) is None:
            raise
        return SpecialistResult[str](
            specialist=RAG_SPECIALIST,
            status="failed",
            reason=failure_reason(error),
        )
    source = state.get("answer_source", "none")
    status, reason = _OUTCOMES[source]
    kind: SourceKind = "web" if source == "web" else "corpus"
    sources = dict.fromkeys(
        chunk.metadata.get("source", "") for chunk in state.get("chunks", [])
    )
    return SpecialistResult[str](
        specialist=RAG_SPECIALIST,
        status=status,
        reason=reason,
        output=state.get("answer") if status != "failed" else None,
        provenance=[Provenance(kind=kind, ref=ref) for ref in sources if ref]
        if status != "failed"
        else [],
    )


def make_rag_subagent(
    graph: RagGraph | None = None,
    *,
    name: str = DEFAULT_RAG_SUBAGENT_NAME,
    description: str = DEFAULT_RAG_SUBAGENT_DESCRIPTION,
) -> CompiledSubAgent:
    """Wrap a compiled RAG graph (default: ``build_rag_graph()``) as a ``CompiledSubAgent``.

    The coordinator's task becomes the question; the envelope comes back as text, so the
    coordinator sees the status and sources too.
    """
    rag_graph = graph if graph is not None else build_rag_graph()

    return specialist_subagent(name, description, lambda task: run_rag(rag_graph, task))
