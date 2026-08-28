"""Node functions for the P2 RAG agent's graph."""

from typing import cast

from models import llm_model
from output_schemas.rag import GradeDocument, GradeHallucination
from prompts.nodes.rag_nodes import (
    _generate_from_web_prompt,
    _generate_prompt,
    _grade_prompt,
    _hallucination_prompt,
    _rewrite_prompt,
)
from retrieval.index import get_retriever
from state import RAGState
from tools.search import web_search
from utils.get_docs_context import get_docs_context
from utils.get_text import get_text


def retrieve_node(state: RAGState) -> dict:
    """Fetch candidate documents for the search query from the persisted index."""
    retriever = get_retriever()
    query = state.get("search_query", state["question"])
    documents = retriever.invoke(query)
    return {"documents": documents}


def grade_documents_node(state: RAGState) -> dict:
    """Keep only documents an LLM judges relevant to the question."""
    grader = llm_model.chain("low", structured=GradeDocument)
    chain = _grade_prompt | grader
    relevant = [
        doc
        for doc in state["documents"]
        if cast(
            GradeDocument,
            chain.invoke({"question": state["question"], "document": doc.page_content}),
        ).binary_score
        == "yes"
    ]
    return {"documents": relevant}


def query_rewrite_node(state: RAGState) -> dict:
    """Rewrite the search query when grading found nothing relevant, and retry."""
    chain = _rewrite_prompt | llm_model.chain("low")
    query = state.get("search_query", state["question"])
    response = chain.invoke({"question": state["question"], "search_query": query})
    return {"search_query": get_text(response), "retries": state.get("retries", 0) + 1}


def generate_node(state: RAGState) -> dict:
    """Answer the question grounded in the surviving documents."""
    context = get_docs_context(state["documents"])
    chain = _generate_prompt | llm_model.chain("medium")
    response = chain.invoke({"question": state["question"], "context": context})
    return {"generation": get_text(response)}


def check_hallucination_node(state: RAGState) -> dict:
    context = get_docs_context(state["documents"])
    grader = llm_model.chain("low", structured=GradeHallucination)
    chain = _hallucination_prompt | grader
    verdict = cast(
        GradeHallucination,
        chain.invoke({"context": context, "generation": state["generation"]}),
    )
    if verdict.binary_score == "yes":
        return {}
    return {
        "generation": "I found a possible answer, but couldn't verify it's fully supported by the indexed corpus, so I'm not confident enough to state it."
    }


def web_search_fallback_node(state: RAGState) -> dict:
    """Fall back to a live web search when the local corpus has nothing relevant."""
    response = web_search.invoke({"query": state["question"]})
    results = response.get("results", [])
    if not results:
        return {
            "generation": "I couldn't find anything relevant on the indexed corpus or the web to answer that."
        }

    context = "\n\n".join(f"[{r['url']}]\n{r['content']}" for r in results)
    chain = _generate_from_web_prompt | llm_model.chain("low")
    answer = chain.invoke({"question": state["question"], "context": context})
    return {"generation": get_text(answer)}
