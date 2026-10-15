"""Graph assembly for the P2 RAG agent: retrieve -> grade -> (rewrite loop | generate | web search)."""

from typing import Literal, NewType

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
from agentlab.schemas.state.rag_state import RAGState
from agentlab.utils.failure_util import TRANSIENT_RETRY


def route_after_grading(
    state: RAGState,
) -> Literal["generate", "query_rewrite", "web_search"]:
    """Relevant chunks -> generate; none yet with retries left -> rewrite and retry; else the web."""
    if state.get("chunks"):
        return "generate"
    if state.get("retries", 0) < MAX_RETRIES:
        return "query_rewrite"
    return "web_search"


def route_after_web_search(state: RAGState) -> Literal["generate_from_web", "__end__"]:
    """Results -> answer from them; none -> end with the no-answer reply."""
    return "generate_from_web" if state.get("chunks") else "__end__"


def build_rag_graph(
    checkpointer: BaseCheckpointSaver | None = None,
) -> RagGraph:
    """Compile the RAG graph (defaults to an in-memory checkpointer)."""
    graph = StateGraph(RAGState)
    # The two nodes whose external call has no retry of its own: embeddings and web search.
    graph.add_node("retrieve", retrieve_node, retry_policy=TRANSIENT_RETRY)
    graph.add_node("grade_chunks", grade_chunks_node)
    graph.add_node("query_rewrite", query_rewrite_node)
    graph.add_node("generate", generate_node)
    graph.add_node("web_search", web_search_node, retry_policy=TRANSIENT_RETRY)
    graph.add_node("generate_from_web", generate_from_web_node)
    graph.add_node("check_hallucination", check_hallucination_node)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "grade_chunks")
    graph.add_conditional_edges("grade_chunks", route_after_grading)
    graph.add_edge("query_rewrite", "retrieve")
    graph.add_edge("generate", "check_hallucination")
    graph.add_conditional_edges("web_search", route_after_web_search)
    graph.add_edge("generate_from_web", END)
    graph.add_edge("check_hallucination", END)
    compiled = graph.compile(
        checkpointer=checkpointer if checkpointer is not None else InMemorySaver(),
    )
    setattr(compiled, "_is_rag_graph", True)  # noqa: B010
    return RagGraph(compiled)
