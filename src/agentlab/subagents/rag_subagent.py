"""P2's boundary: ``run_rag`` returns the specialist envelope; the adapter serves DeepAgents coordinators."""

from typing import Any

from deepagents import CompiledSubAgent
from langchain_core.runnables import Runnable, RunnableLambda

from agentlab.graphs.rag_graph import build_rag_graph
from agentlab.schemas.output.specialist_output_schema import (
    Provenance,
    SpecialistResult,
)
from agentlab.utils.subagent_util import (
    new_delegation_config,
    task_text_from_state,
    to_subagent_reply,
)

RAG_SPECIALIST = "rag"
DEFAULT_RAG_SUBAGENT_NAME = "rag_subagent"
DEFAULT_RAG_SUBAGENT_DESCRIPTION = (
    "Answers questions using the indexed document corpus, falling back "
    "to a live web search when nothing relevant is found locally."
)

# answer_source -> (status, reason): the graph records where its answer came from; the
# boundary turns that fact into what a caller needs to decide.
_OUTCOMES = {
    "corpus": ("success", "Answered from the indexed corpus."),
    "web": ("partial", "The local corpus had nothing relevant; answered from the web."),
    "unverified": ("failed", "The corpus answer wasn't supported by its documents."),
    "none": ("failed", "Nothing relevant in the corpus or on the web."),
}


def run_rag(graph: Runnable, question: str) -> SpecialistResult[str]:
    """Answer ``question`` with the RAG graph, on a fresh thread, as a specialist envelope."""
    state = graph.invoke(
        {
            "question": question,
            "search_query": question,
            "retries": 0,
        },
        config=new_delegation_config(),
    )
    source = state.get("answer_source", "none")
    status, reason = _OUTCOMES.get(source, ("failed", "Unknown source."))
    kind = "web" if source == "web" else "corpus"
    sources = dict.fromkeys(
        doc.metadata.get("source", "") for doc in state.get("documents", [])
    )
    provenance = [Provenance(kind=kind, ref=ref) for ref in sources if ref]
    return SpecialistResult(
        specialist=RAG_SPECIALIST,
        status=status,
        reason=reason,
        output=state.get("generation") if status != "failed" else None,
        provenance=provenance if status != "failed" else [],
    )
