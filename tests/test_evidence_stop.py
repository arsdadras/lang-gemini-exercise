"""R1 topic 4: the stop condition, ``evidence_enough@1``, inside the researcher's loop."""

from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import StructuredTool, tool
from langgraph.checkpoint.memory import InMemorySaver

from agentlab.middlewares.evidence_stop_middleware import (
    QUESTION_SET,
    STOP_NOTE,
    EvidenceStopMiddleware,
)
from agentlab.nodes.research_node import make_research_node
from agentlab.schemas.output.research_output_schema import ResearchDraft, SourceDocument
from agentlab.schemas.state.research_state import SubQuestionState
from agentlab.tools.research_source_tool import as_artifact
from tests.fakes import ScriptedToolModel, done, tool_turn
from tests.test_research_sources import Recorder, answers
from tests.test_specialist_contract import rejected

PAGE = "https://docs.example.com/py314"
SEEN: list[tuple[set[str], list[Any]]] = []
"""Per model call: the tool names offered and the messages sent."""


def _search(query: str) -> tuple[str, list[dict[str, Any]]]:
    document = SourceDocument(
        url=PAGE, kind="web", text="Python 3.14 shipped in October."
    )
    return f"{PAGE}\n\n{document.text}", as_artifact([document])


web_search = StructuredTool.from_function(
    _search,
    name="web_search",
    description="Search the web.",
    response_format="content_and_artifact",
)


class Sees(ScriptedToolModel):
    """A scripted model that records what each call is offered and sent."""

    def bind_tools(self, tools: Any, **kwargs: Any) -> "Sees":
        self._offered = {t.name for t in tools}
        return self

    def _generate(self, messages: Any, *args: Any, **kwargs: Any) -> Any:
        # A call with no tools binds none, so what was offered is read once, then cleared.
        SEEN.append((getattr(self, "_offered", set()), list(messages)))
        self._offered = set()
        return super()._generate(messages, *args, **kwargs)


@tool
def snippets(query: str) -> str:
    """A search that returns snippets only, no document."""
    return "snippets"


def run(decide: Any, *replies: Any) -> dict[str, Any]:
    SEEN.clear()
    agent = create_agent(
        model=Sees(messages=iter(replies)),
        tools=[web_search, snippets],
        middleware=[EvidenceStopMiddleware(decide=decide)],
        checkpointer=InMemorySaver(),
    )
    return agent.invoke(
        {"messages": [HumanMessage("When did Python 3.14 ship?")]},
        {"configurable": {"thread_id": "1"}},
    )


def test_enough_evidence_ends_the_search_in_code() -> None:
    decide = Recorder(answers(q=("yes", 0.9)))

    state = run(decide, tool_turn("web_search", query="py314"), done())

    assert state["evidence_enough"] is True
    [(judged, _, question_set)] = decide.calls
    assert question_set == QUESTION_SET and "Python 3.14 shipped" in judged
    offered_after, sent_after = SEEN[1]
    assert offered_after == {"snippets"}  # not a source tool, so never closed
    assert sent_after[-1].content == STOP_NOTE


def test_not_enough_keeps_the_search_open_and_says_so() -> None:
    decide = Recorder(answers(q=("no", 0.9)))

    state = run(decide, tool_turn("web_search", query="py314"), done())

    assert state["evidence_enough"] is False
    assert SEEN[1][0] == {"web_search", "snippets"}


def test_an_unsure_yes_is_not_enough() -> None:
    decide = Recorder(answers(q=("yes", 0.6)))

    state = run(decide, tool_turn("web_search", query="py314"), done())

    assert state["evidence_enough"] is False


def test_nothing_is_judged_before_a_document_arrives() -> None:
    decide = Recorder(answers(q=("yes", 0.9)))

    state = run(decide, done())

    assert decide.calls == [] and "evidence_enough" not in state


def test_a_tool_turn_without_documents_asks_nothing_new() -> None:
    decide = Recorder(answers(q=("no", 0.9)))

    run(
        decide,
        tool_turn("web_search", query="py314"),
        tool_turn("snippets", query="more"),
        done(),
    )

    assert len(decide.calls) == 1


def test_a_decider_outage_decides_nothing() -> None:
    decide = Recorder(rejected(503))

    state = run(decide, tool_turn("web_search", query="py314"), done())

    assert "evidence_enough" not in state and SEEN[1][0] == {"web_search", "snippets"}


def test_a_source_call_after_enough_is_refused() -> None:
    decide = Recorder(answers(q=("yes", 0.9)))

    state = run(
        decide,
        tool_turn("web_search", query="py314"),
        tool_turn("web_search", query="again"),
        done(),
    )

    refused = [m for m in state["messages"] if isinstance(m, ToolMessage)][-1]
    assert refused.status == "error" and "closed" in refused.content


class Returns:
    """An agent stand-in that returns a fixed final state."""

    def __init__(self, state: dict[str, Any]) -> None:
        self.state = state

    def invoke(self, *_: Any, **__: Any) -> dict[str, Any]:
        return self.state


def test_a_run_that_ends_without_enough_evidence_is_reported() -> None:
    draft = ResearchDraft(topic="t", summary="s", claims=[], citations=[])
    research = make_research_node(
        Returns(
            {"messages": [], "structured_response": draft, "evidence_enough": False}
        )
    )

    update = research(SubQuestionState(question="Q", sources=["web"], label="'Q': "))

    assert update["problems"] == [
        "'Q': The search budget ran out before the evidence was enough."
    ]
