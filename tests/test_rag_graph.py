"""The real P2 RAG graph's routing, run with a scripted grader and rewriter (no real model)."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from unittest.mock import patch

from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from agentlab.configs.rag_config import MAX_RETRIES
from agentlab.graphs.rag_graph import build_rag_graph
from agentlab.nodes import rag_node
from agentlab.schemas.output.rag_output_schema import GradeDocument, GradeHallucination

CORPUS_DOC = Document(page_content="The corpus says X.", metadata={"source": "a.md"})
CONFIG: Any = {"configurable": {"thread_id": "rag-routing"}}


class ScriptedRetriever:
    """Returns the same candidate document for every query and records the queries."""

    def __init__(self) -> None:
        self.queries: list[str] = []

    def invoke(self, query: str) -> list[Document]:
        self.queries.append(query)
        return [CORPUS_DOC]


@contextmanager
def scripted_rag(
    *, relevant: bool, web_results: list[dict] | None = None
) -> Iterator[dict]:
    """Patch the graph's external edges: retriever, web search, and every model chain.

    ``relevant`` is the grader's verdict for every document. The record counts what ran.
    """
    retriever = ScriptedRetriever()
    record: dict = {"retriever": retriever, "rewrites": 0, "web_searches": 0}

    def chain(tier: str, structured: type | None = None) -> RunnableLambda:
        if structured is GradeDocument:
            return RunnableLambda(
                lambda _: GradeDocument(binary_score="yes" if relevant else "no"),
            )
        if structured is GradeHallucination:
            return RunnableLambda(lambda _: GradeHallucination(binary_score="yes"))
        return RunnableLambda(lambda _: AIMessage(content="scripted text"))

    def rewrite(state: dict) -> dict:
        record["rewrites"] += 1
        return real_rewrite(state)

    def web_search(*_: Any, **__: Any) -> dict:
        record["web_searches"] += 1
        return {"results": web_results or []}

    real_rewrite = rag_node.query_rewrite_node
    with (
        patch.object(rag_node, "get_retriever", return_value=retriever),
        patch.object(rag_node.llm_model, "chain", side_effect=chain),
        patch.object(rag_node, "make_web_search_tool") as tool,
        patch("agentlab.graphs.rag_graph.query_rewrite_node", rewrite),
    ):
        tool.return_value.invoke.side_effect = web_search
        yield record


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
