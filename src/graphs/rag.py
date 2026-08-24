"""Graph assembly for the P2 RAG agent: wires nodes into retrieve -> grade -> generate."""

from typing import Literal, cast

from langgraph.graph import END, START, StateGraph

from nodes.rag import (
    MAX_RETRIES,
    generate,
    grade_documents,
    no_relevant_docs,
    query_rewrite,
    retrieve,
)
from state import RAGState


def route_after_grading(
    state: RAGState,
) -> Literal["generate", "query_rewrite", "no_relevant_docs"]:
    """Conditional edge: relevant docs -> generate; none yet & retries left -> rewrite+retry; else fallback."""
    if state["documents"]:
        return "generate"
    if state.get("retries", 0) < MAX_RETRIES:
        return "query_rewrite"
    return "no_relevant_docs"


def build_rag_graph():
    graph = StateGraph(cast(type, RAGState))
    graph.add_node("retrieve", retrieve)
    graph.add_node("grade_documents", grade_documents)
    graph.add_node("query_rewrite", query_rewrite)
    graph.add_node("generate", generate)
    graph.add_node("no_relevant_docs", no_relevant_docs)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "grade_documents")
    graph.add_conditional_edges("grade_documents", route_after_grading)
    graph.add_edge("query_rewrite", "retrieve")
    graph.add_edge("generate", END)
    graph.add_edge("no_relevant_docs", END)

    return graph.compile()
