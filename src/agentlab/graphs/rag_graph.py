"""Graph assembly for the P2 RAG agent: retrieve -> grade -> (rewrite loop | generate | web search) -> format_report -> pack_result."""

from typing import Any, Literal, NewType

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

RagGraph = NewType("RagGraph", CompiledStateGraph)

from agentlab.configs.rag_config import MAX_RETRIES
from agentlab.nodes.rag_node import (
    check_hallucination_node,
    generate_from_web_node,
    generate_node,
    grade_chunks_node,
    query_rewrite_node,
    retrieve_node,
    web_search_node,
)
from agentlab.schemas.input.rag_input_schema import RagInput
from agentlab.schemas.output.rag_output_schema import (
    RagGroundingVerdict,
    RagReport,
    RagRetrievalMode,
)
from agentlab.schemas.output.research_output_schema import SourceKind
from agentlab.schemas.output.specialist_output_schema import (
    Provenance,
    SpecialistStatus,
)
from agentlab.schemas.state.rag_state import RAGState
from agentlab.utils.failure_util import TRANSIENT_RETRY
from agentlab.workflows.specialist_workflow import ResultNode, SpecialistSpec

DEFAULT_RAG_DESCRIPTION = (
    "Answers questions using the indexed chunk corpus, falling back "
    "to a live web search when nothing relevant is found locally."
)

RAG_SPEC = SpecialistSpec[RagInput, RagReport](
    name="rag",
    description=DEFAULT_RAG_DESCRIPTION,
    input_schema=RagInput,
    report_schema=RagReport,
)

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


def route_after_grading(
    state: RAGState,
) -> Literal["generate", "query_rewrite", "web_search"]:
    """Relevant chunks -> generate; none yet with retries left -> rewrite and retry; else the web."""
    if state.get("chunks"):
        return "generate"
    if state.get("retries", 0) < MAX_RETRIES:
        return "query_rewrite"
    return "web_search"


def route_after_web_search(
    state: RAGState,
) -> Literal["generate_from_web", "format_report"]:
    """Results -> answer from them; none -> format the report (ending in no-answer reply)."""
    return "generate_from_web" if state.get("chunks") else "format_report"


def format_rag_report_node(state: RAGState) -> dict[str, Any]:
    """Format the answer and chunks into a structured ``RagReport`` and workflow channels."""
    source = state.get("answer_source", "none")
    status, reason, retrieval_mode, grounding_verdict = _OUTCOMES.get(
        source,
        ("failed", "Unknown RAG outcome.", "none", "none"),
    )
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


def build_rag_graph(
    checkpointer: BaseCheckpointSaver | None = None,
) -> RagGraph:
    """Compile the RAG graph ending in ``format_report -> pack_result``."""
    graph = StateGraph(RAGState)
    # The two nodes whose external call has no retry of its own: embeddings and web search.
    graph.add_node("retrieve", retrieve_node, retry_policy=TRANSIENT_RETRY)
    graph.add_node("grade_chunks", grade_chunks_node)
    graph.add_node("query_rewrite", query_rewrite_node)
    graph.add_node("generate", generate_node)
    graph.add_node("web_search", web_search_node, retry_policy=TRANSIENT_RETRY)
    graph.add_node("generate_from_web", generate_from_web_node)
    graph.add_node("check_hallucination", check_hallucination_node)
    graph.add_node("format_report", format_rag_report_node)
    graph.add_node("pack_result", ResultNode(RAG_SPEC))

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "grade_chunks")
    graph.add_conditional_edges("grade_chunks", route_after_grading)
    graph.add_edge("query_rewrite", "retrieve")
    graph.add_edge("generate", "check_hallucination")
    graph.add_conditional_edges("web_search", route_after_web_search)
    graph.add_edge("generate_from_web", "format_report")
    graph.add_edge("check_hallucination", "format_report")
    graph.add_edge("format_report", "pack_result")
    graph.add_edge("pack_result", END)
    compiled = graph.compile(
        checkpointer=checkpointer if checkpointer is not None else InMemorySaver(),
    )
    return RagGraph(compiled)
