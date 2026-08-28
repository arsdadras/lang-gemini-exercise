"""Graph assembly for the P2 RAG agent: wires nodes into retrieve -> grade -> generate."""

from typing import Literal, cast

from configs.rag import MAX_RETRIES
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from nodes import (
    check_hallucination_node,
    generate_node,
    grade_documents_node,
    query_rewrite_node,
    retrieve_node,
    web_search_fallback_node,
)
from state import RAGState


def route_after_grading(
    state: RAGState,
) -> Literal["generate", "query_rewrite", "web_search_fallback"]:
    """Conditional edge: relevant docs -> generate; none yet & retries left -> rewrite+retry; else fallback."""
    if state["documents"]:
        return "generate"
    if state.get("retries", 0) < MAX_RETRIES:
        return "query_rewrite"
    return "web_search_fallback"


def build_rag_graph():
    graph = StateGraph(cast(type, RAGState))
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
    return graph.compile(checkpointer=InMemorySaver())
