"""Node functions for the P2 RAG graph."""

from typing import cast

from agentlab.models import llm_model
from agentlab.prompts.nodes.rag_prompt import (
    GENERATE_FROM_WEB_PROMPT,
    GENERATE_PROMPT,
    GRADE_PROMPT,
    HALLUCINATION_PROMPT,
    REWRITE_PROMPT,
)
from agentlab.retrieval.index_retrieval import get_retriever
from agentlab.schemas.output.rag_output_schema import GradeDocument, GradeHallucination
from agentlab.schemas.state.rag_state import RAGState
from agentlab.tools.web_search_tool import make_web_search_tool
from agentlab.utils.get_docs_context_util import get_docs_context
from agentlab.utils.get_text_util import get_text

UNVERIFIED_ANSWER = (
    "I found a possible answer, but couldn't verify it's fully supported by the "
    "indexed corpus, so I'm not confident enough to state it."
)
NO_ANSWER = "I couldn't find anything relevant in the indexed corpus or on the web to answer that."


def retrieve_node(state: RAGState) -> dict:
    """Fetch candidate documents for the current search query."""
    query = state.get("search_query", state["question"])
    return {"documents": get_retriever().invoke(query)}


def grade_documents_node(state: RAGState) -> dict:
    """Keep only documents an LLM judges relevant (one grading call per document)."""
    grader = GRADE_PROMPT | llm_model.chain("low", structured=GradeDocument)
    relevant = [
        document
        for document in state.get("documents", [])
        if cast(
            GradeDocument,
            grader.invoke({"question": state["question"], "document": document.page_content}),
        ).binary_score
        == "yes"
    ]
    return {"documents": relevant}


def query_rewrite_node(state: RAGState) -> dict:
    """Rewrite the search query after grading found nothing relevant."""
    chain = REWRITE_PROMPT | llm_model.chain("low")
    query = state.get("search_query", state["question"])
    response = chain.invoke({"question": state["question"], "search_query": query})
    return {"search_query": get_text(response), "retries": state.get("retries", 0) + 1}


def generate_node(state: RAGState) -> dict:
    """Answer the question from the surviving documents."""
    context = get_docs_context(state.get("documents", []))
    response = (GENERATE_PROMPT | llm_model.chain("medium")).invoke(
        {"question": state["question"], "context": context}
    )
    return {"generation": get_text(response)}


def check_hallucination_node(state: RAGState) -> dict:
    """Replace the answer with a disclaimer when the documents don't support it."""
    context = get_docs_context(state.get("documents", []))
    grader = HALLUCINATION_PROMPT | llm_model.chain("low", structured=GradeHallucination)
    verdict = cast(
        GradeHallucination,
        grader.invoke({"context": context, "generation": state.get("generation", "")}),
    )
    if verdict.binary_score == "yes":
        return {}
    return {"generation": UNVERIFIED_ANSWER}


def web_search_fallback_node(state: RAGState) -> dict:
    """Answer from a live web search when the local corpus had nothing relevant."""
    response = make_web_search_tool().invoke({"query": state["question"]})
    results = response.get("results", [])
    if not results:
        return {"generation": NO_ANSWER}

    context = "\n\n".join(f"[{result['url']}]\n{result['content']}" for result in results)
    answer = (GENERATE_FROM_WEB_PROMPT | llm_model.chain("low")).invoke(
        {"question": state["question"], "context": context}
    )
    return {"generation": get_text(answer)}
