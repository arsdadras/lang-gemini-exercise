"""Scripted fakes for running real LangGraph/DeepAgents graphs without a real model."""

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from unittest.mock import patch

from langchain_core.documents import Document
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from agentlab.nodes import rag_node
from agentlab.schemas.output.middlewares_output_schema import GuardVerdict
from agentlab.schemas.output.rag_output_schema import GradeDocument, GradeHallucination

CORPUS_DOC = Document(page_content="The corpus says X.", metadata={"source": "a.md"})


class ScriptedToolModel(GenericFakeChatModel):
    """Fake chat model that accepts tool binding, as the agent loop requires."""

    def bind_tools(self, tools: Any, **kwargs: Any) -> "ScriptedToolModel":
        return self


def tool_turn(name: str, **args: Any) -> AIMessage:
    """A model reply that calls one tool."""
    return AIMessage(
        content="",
        tool_calls=[{"name": name, "args": args, "id": uuid.uuid4().hex}],
    )


def done() -> AIMessage:
    """A final model reply.

    A fresh message each time: LangGraph merges messages by id, so reusing one
    instance would overwrite the earlier reply instead of appending a new one.
    """
    return AIMessage(content="Done.")


class RecordingGuard:
    """Scripted security guard: returns its decisions in turn (repeating the last) and records calls."""

    def __init__(
        self,
        *decisions: str,
        category: str = "test",
        reason: str = "Scripted verdict.",
    ) -> None:
        self.verdicts = [
            GuardVerdict(decision=decision, category=category, reason=reason)
            for decision in decisions
        ]
        self.calls: list[tuple[str, str]] = []

    def __call__(self, action: str, content: str) -> GuardVerdict:
        self.calls.append((action, content))
        return self.verdicts[min(len(self.calls), len(self.verdicts)) - 1]


class ScriptedRetriever:
    """Returns the same candidate document for every query and records the queries."""

    def __init__(self) -> None:
        self.queries: list[str] = []

    def invoke(self, query: str) -> list[Document]:
        self.queries.append(query)
        return [CORPUS_DOC]


@contextmanager
def scripted_rag(
    *,
    relevant: bool,
    web_results: list[dict] | None = None,
    web_tool: Any = None,
) -> Iterator[dict]:
    """Patch the graph's external edges: retriever, web search, and every model chain.

    ``relevant`` is the grader's verdict for every document. ``web_tool`` replaces the scripted
    web search (to point the real tool at a silent server). The record counts what ran.
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
        if web_tool is not None:
            tool.return_value = web_tool
        yield record


def scripted_decider(*responses: Any) -> RunnableLambda:
    """A decision backend that answers each request with the next scripted response.

    A response that is an exception is raised instead, so a test can script a decider failure.
    """
    queue = list(responses)

    def answer(_request: Any) -> Any:
        item = queue.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    return RunnableLambda(answer)
