"""Graph assembly for the P2 RAG agent: retrieve -> grade -> (rewrite loop | generate | web fallback)."""

from typing import Literal

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agentlab.configs.rag_config import MAX_RETRIES
from agentlab.nodes.rag_node import (
    check_hallucination_node,
    generate_node,
    grade_documents_node,
    query_rewrite_node,
    retrieve_node,
    web_search_fallback_node,
)
from agentlab.schemas.state.rag_state import RAGState


def route_after_grading(
    state: RAGState,
) -> Literal["generate", "query_rewrite", "web_search_fallback"]:
    """Relevant docs -> generate; none yet with retries left -> rewrite and retry; else web fallback."""
    if state.get("documents"):
        return "generate"
    if state.get("retries", 0) < MAX_RETRIES:
        return "query_rewrite"
    return "web_search_fallback"


def build_rag_graph(checkpointer: BaseCheckpointSaver | None = None) -> CompiledStateGraph:
    """Compile the RAG graph (defaults to an in-memory checkpointer)."""
    graph = StateGraph(RAGState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("grade_documents", grade_documents_node)
    graph.add_node("query_rewrite", query_rewrite_node)
    graph.add_node("generate", generate_node)
    graph.add_node("web_search_fallback", web_search_fallback_node)
    graph.add_node("check_hallucination", check_hallucination_node)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "grade_documents")
    graph.add_conditional_edges("grade_documents", route_after_grading)
    graph.add_edge("query_rewrite", "retrieve")
    graph.add_edge("generate", "check_hallucination")
    graph.add_edge("web_search_fallback", END)
    graph.add_edge("check_hallucination", END)
    return graph.compile(checkpointer=checkpointer if checkpointer is not None else InMemorySaver())
