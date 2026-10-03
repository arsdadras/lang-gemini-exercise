"""The real P2 RAG graph's routing, run with a scripted grader and rewriter (no real model)."""

from typing import Any

from agentlab.configs.rag_config import MAX_RETRIES
from agentlab.graphs.rag_graph import build_rag_graph
from agentlab.nodes import rag_node
from tests.fakes import scripted_rag

CONFIG: Any = {"configurable": {"thread_id": "rag-routing"}}


def run(question: str = "What is X?") -> dict:
    return build_rag_graph().invoke({"question": question}, CONFIG)


def test_relevant_documents_go_straight_to_generate() -> None:
    with scripted_rag(relevant=True) as record:
        state = run()

    assert record["rewrites"] == 0
    assert record["web_searches"] == 0
    assert len(record["retriever"].queries) == 1
    assert state["answer_source"] == "corpus"
    assert state["generation"] == "scripted text"


def test_nothing_relevant_rewrites_exactly_max_retries_times_then_searches_the_web() -> (
    None
):
    web = [{"url": "https://a.example", "content": "From the web."}]
    with scripted_rag(relevant=False, web_results=web) as record:
        state = run()

    assert MAX_RETRIES == 2
    assert record["rewrites"] == MAX_RETRIES
    # The first retrieval plus one per rewrite, then the loop stops.
    assert len(record["retriever"].queries) == MAX_RETRIES + 1
    assert record["web_searches"] == 1
    assert state["retries"] == MAX_RETRIES
    assert state["answer_source"] == "web"


def test_the_web_having_nothing_ends_with_the_no_answer_reply() -> None:
    with scripted_rag(relevant=False, web_results=[]) as record:
        state = run()

    assert record["web_searches"] == 1
    assert state["answer_source"] == "none"
    assert state["generation"] == rag_node.NO_ANSWER


def test_rewritten_queries_replace_the_search_query_for_the_next_retrieval() -> None:
    with scripted_rag(relevant=False) as record:
        run("What is X?")

    assert record["retriever"].queries == [
        "What is X?",
        "scripted text",
        "scripted text",
    ]
