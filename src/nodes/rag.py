"""Node functions for the P2 RAG agent's graph."""

from typing import cast

from models.llm import lite_model
from prompts.rag import (
    _generate_prompt,
    _grade_prompt,
    _rewrite_prompt,
    _generate_from_web_prompt,
)
from retrieval.index import get_retriever
from schemas.rag import GradeDocument
from state import RAGState
from tools.search import web_search
from utils.text import get_text


def retrieve(state: RAGState) -> dict:
    """Fetch candidate documents for the search query from the persisted index."""
    retriever = get_retriever()
    query = state.get("search_query", state["question"])
    documents = retriever.invoke(query)
    return {"documents": documents}


def grade_documents(state: RAGState) -> dict:
    """Keep only documents an LLM judges relevant to the question."""
    _grader = lite_model.with_structured_output(GradeDocument)
    chain = _grade_prompt | _grader
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


def query_rewrite(state: RAGState) -> dict:
    """Rewrite the search query when grading found nothing relevant, and retry."""
    chain = _rewrite_prompt | lite_model
    query = state.get("search_query", state["question"])
    response = chain.invoke({"question": state["question"], "search_query": query})
    return {"search_query": get_text(response), "retries": state.get("retries", 0) + 1}


def generate(state: RAGState) -> dict:
    """Answer the question grounded in the surviving documents."""
    context = "\n\n".join(
        f"[{doc.metadata['source']}]\n{doc.page_content}" for doc in state["documents"]
    )
    chain = _generate_prompt | lite_model
    response = chain.invoke({"question": state["question"], "context": context})
    return {"generation": get_text(response)}


def web_search_fallback(state: RAGState) -> dict:
    """Fall back to a live web search when the local corpus has nothing relevant."""
    response = web_search.invoke({"query": state["question"]})
    results = response.get("results", [])
    if not results:
        return {
            "generation": "I couldn't find anything relevant on the indexed corpus or the web to answer that."
        }

    context = "\n\n".join(f"[{r['url']}]\n{r['content']}" for r in results)
    chain = _generate_from_web_prompt | lite_model
    answer = chain.invoke({"question": state["question"], "context": context})
    return {"generation": get_text(answer)}
