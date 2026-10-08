"""Node functions for the P2 RAG graph."""

from typing import cast

from langchain_core.documents import Document

from agentlab.models import llm_model
from agentlab.prompts.nodes.rag_prompt import (
    GENERATE_FROM_WEB_PROMPT,
    GENERATE_PROMPT,
    GRADE_PROMPT,
    HALLUCINATION_PROMPT,
    REWRITE_PROMPT,
)
from agentlab.retrieval.index_retrieval import get_retriever
from agentlab.schemas.output.rag_output_schema import GradeChunk, GradeHallucination
from agentlab.schemas.state.rag_state import RAGState
from agentlab.tools.web_search_tool import make_web_search_tool, search_results
from agentlab.utils.format_chunks_util import format_chunks
from agentlab.utils.get_text_util import get_text

UNVERIFIED_ANSWER = (
    "I found a possible answer, but couldn't verify it's fully supported by the "
    "indexed corpus, so I'm not confident enough to state it."
)
NO_ANSWER = "I couldn't find anything relevant in the indexed corpus or on the web to answer that."


def retrieve_node(state: RAGState) -> dict:
    """Fetch candidate chunks for the current search query."""
    query = state.get("search_query", state["question"])
    return {"chunks": get_retriever().invoke(query)}


def grade_chunks_node(state: RAGState) -> dict:
    """Keep only chunks an LLM judges relevant (one grading call per chunk)."""
    grader = GRADE_PROMPT | llm_model.chain(
        "opensource",
        structured=GradeChunk,
    )
    relevant = [
        chunk
        for chunk in state.get("chunks", [])
        if cast(
            GradeChunk,
            grader.invoke(
                {
                    "question": state["question"],
                    "chunk": chunk.page_content,
                },
            ),
        ).binary_score
        == "yes"
    ]
    return {"chunks": relevant}


def query_rewrite_node(state: RAGState) -> dict:
    """Rewrite the search query after grading found nothing relevant."""
    chain = REWRITE_PROMPT | llm_model.chain("opensource")
    query = state.get("search_query", state["question"])
    response = chain.invoke(
        {"question": state["question"], "search_query": query},
    )
    return {
        "search_query": get_text(response),
        "retries": state.get("retries", 0) + 1,
    }


def generate_node(state: RAGState) -> dict:
    """Answer the question from the surviving chunks."""
    # "medium": the user-facing answer itself, not a gate (see ADR-0014).
    context = format_chunks(state.get("chunks", []))
    response = (GENERATE_PROMPT | llm_model.chain("medium")).invoke(
        {"question": state["question"], "context": context},
    )
    return {"answer": get_text(response)}


def check_hallucination_node(state: RAGState) -> dict:
    """Replace the answer with a disclaimer when the chunks don't support it."""
    # Trust gate, kept on a paid tier deliberately: this is P2's core anti-hallucination
    # guarantee, with no live-verified opensource-tier baseline yet (ADR-0014).
    context = format_chunks(state.get("chunks", []))
    grader = HALLUCINATION_PROMPT | llm_model.chain(
        "low",
        structured=GradeHallucination,
    )
    verdict = cast(
        GradeHallucination,
        grader.invoke(
            {
                "context": context,
                "answer": state.get("answer", ""),
            },
        ),
    )
    if verdict.binary_score == "yes":
        return {"answer_source": "corpus"}
    return {
        "answer": UNVERIFIED_ANSWER,
        "answer_source": "unverified",
    }


def web_search_node(state: RAGState) -> dict:
    """Search the web when the local corpus had nothing relevant; results become chunks.

    Only the search happens here, so a retry policy on this node retries the search alone.
    """
    results = search_results(
        make_web_search_tool().invoke({"query": state["question"]})
    )
    if not results:
        return {"answer": NO_ANSWER, "answer_source": "none", "chunks": []}
    chunks = [
        Document(page_content=result["content"], metadata={"source": result["url"]})
        for result in results
    ]
    return {"chunks": chunks}


def generate_from_web_node(state: RAGState) -> dict:
    """Answer from the web search results."""
    context = "\n\n".join(
        f"[{chunk.metadata['source']}]\n{chunk.page_content}"
        for chunk in state.get("chunks", [])
    )
    # "low", not "opensource": this is the user-facing answer, same reasoning as generate_node.
    answer = (GENERATE_FROM_WEB_PROMPT | llm_model.chain("low")).invoke(
        {"question": state["question"], "context": context},
    )
    return {"answer": get_text(answer), "answer_source": "web"}
