"""R1 topic 3: the researcher's sources, the router that picks them, and their provenance."""

from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import pytest
import requests
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from agentlab.agents import researcher_agent
from agentlab.agents.researcher_agent import make_researcher_agent
from agentlab.middlewares.source_route_middleware import SourceRouteMiddleware
from agentlab.nodes import claim_check_node
from agentlab.nodes.claim_check_node import check_claims
from agentlab.nodes.research_node import fan_out
from agentlab.nodes.source_route_node import (
    QUESTION_SET,
    SKIP_THRESHOLD,
    make_route_node,
    route_sources,
)
from agentlab.schemas.input.research_input_schema import ResearchOptions
from agentlab.schemas.output.research_output_schema import (
    Citation,
    DraftClaim,
    Evidence,
    ResearchDraft,
    SourceDocument,
)
from agentlab.subagents.research_subagent import run_research
from agentlab.tools import research_source_tool
from agentlab.tools.academic_search_tool import make_academic_search_tool
from agentlab.tools.corpus_search_tool import make_corpus_search_tool
from agentlab.tools.research_source_tool import documents_read, research_sources
from tests.fakes import ScriptedToolModel, done, tool_turn

PAPER = "https://arxiv.org/abs/2309.15217"
PAGE = "https://docs.example.com/eval"


def sources_available(monkeypatch: pytest.MonkeyPatch, *names: str) -> None:
    monkeypatch.setattr(research_source_tool, "available_sources", lambda: list(names))


# --- the router -----------------------------------------------------------------------------


def answers(**choices: tuple[str, float]) -> Any:
    """A decider response: per question key, the chosen label and its probability."""
    return SimpleNamespace(
        choices={
            key: SimpleNamespace(choice=label, probabilities={label: probability})
            for key, (label, probability) in choices.items()
        }
    )


class Recorder:
    """A decider stand-in that records each request and returns a fixed response."""

    def __init__(self, response: Any) -> None:
        self.response = response
        self.calls: list[tuple[Any, dict[str, Any], str]] = []

    def __call__(
        self, state: Any, questions: dict[str, Any], *, question_set: str
    ) -> Any:
        self.calls.append((state, questions, question_set))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


def test_every_sub_question_and_source_is_one_question_in_one_request() -> None:
    decide = Recorder(
        answers(
            q1_web=("yes", 0.9),
            q1_academic=("yes", 0.8),
            q2_web=("yes", 0.9),
            q2_academic=("no", 0.9),
        )
    )

    routes = route_sources(
        ["How is RAG evaluated in papers?", "What does RAGAS cost?"],
        ["web", "academic"],
        decide=decide,
    )

    assert routes == {
        "How is RAG evaluated in papers?": ["web", "academic"],
        "What does RAGAS cost?": ["web"],
    }
    [(state, questions, question_set)] = decide.calls
    assert question_set == QUESTION_SET
    assert set(questions) == {"q1_web", "q1_academic", "q2_web", "q2_academic"}
    # Each batched question names the sub-question it is about.
    assert "What does RAGAS cost?" in questions["q2_academic"].instructions
    assert "What does RAGAS cost?" in state


def test_only_a_sure_no_skips_a_source_and_unclear_keeps_it() -> None:
    unsure = SKIP_THRESHOLD - 0.1
    decide = Recorder(
        answers(
            q1_web=("yes", 0.9),
            q1_academic=("no", unsure),
            q1_corpus=("unclear", 0.7),
        )
    )

    routes = route_sources(["Q"], ["web", "academic", "corpus"], decide=decide)

    assert routes == {"Q": ["web", "academic", "corpus"]}


def test_a_question_no_source_fits_gets_the_web() -> None:
    decide = Recorder(
        answers(q1_web=("no", 0.9), q1_academic=("no", 0.95), q1_corpus=("no", 0.9))
    )

    assert route_sources(["Q"], ["web", "academic", "corpus"], decide=decide) == {
        "Q": ["web"]
    }


def test_without_the_web_a_question_no_source_fits_keeps_every_source() -> None:
    decide = Recorder(answers(q1_academic=("no", 0.95), q1_corpus=("no", 0.95)))

    assert route_sources(["Q"], ["academic", "corpus"], decide=decide) == {
        "Q": ["academic", "corpus"]
    }


def test_one_available_source_asks_nothing() -> None:
    decide = Recorder(RuntimeError("never called"))

    assert route_sources(["Q1", "Q2"], ["web"], decide=decide) == {
        "Q1": ["web"],
        "Q2": ["web"],
    }
    assert decide.calls == []


def test_a_decider_outage_keeps_every_source() -> None:
    decide = Recorder(requests.ConnectionError("down"))

    assert route_sources(["Q"], ["web", "academic"], decide=decide) == {
        "Q": ["web", "academic"]
    }


def test_a_decider_bug_is_not_swallowed() -> None:
    with pytest.raises(KeyError):
        route_sources(["Q"], ["web", "academic"], decide=Recorder(KeyError("bug")))


def test_requested_sources_this_environment_cannot_serve_are_reported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sources_available(monkeypatch, "web", "corpus")
    route = make_route_node(Recorder(RuntimeError("never called")))

    update = route(
        {
            "topic": "t",
            "options": ResearchOptions(sources=["academic", "corpus"]),
            "questions": ["Q"],
        }
    )

    assert update["routes"] == {"Q": ["corpus"]}
    assert update["problems"] == ["Not available here, so not searched: academic."]


def test_research_sources_falls_back_to_the_web_when_nothing_requested_is_served(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sources_available(monkeypatch, "web")

    assert research_sources(ResearchOptions()) == (["web"], [])
    assert research_sources(ResearchOptions(sources=["academic"])) == (
        ["web"],
        ["academic"],
    )


def test_each_run_is_sent_with_its_own_sources() -> None:
    sends = fan_out({"questions": ["Q1", "Q2"], "routes": {"Q1": ["academic"]}})

    assert [send.arg["sources"] for send in sends] == [["academic"], ["web"]]


# --- the route, enforced in the agent -------------------------------------------------------


@tool
def web_search(query: str) -> str:
    """Search the web."""
    return "snippets"


@tool
def academic_search(query: str) -> str:
    """Search papers."""
    return "papers"


@tool
def get_user_context() -> str:
    """Not a source: a composing caller's tool."""
    return "context"


OFFERED: list[set[str]] = []
"""The tool names each model call was offered (a pydantic model can't hold it as a field)."""


class SeesTools(ScriptedToolModel):
    """A scripted model that records the tools it is offered."""

    def bind_tools(self, tools: Any, **kwargs: Any) -> "SeesTools":
        OFFERED.append({t.name for t in tools})
        return self


def routed_agent(*replies: AIMessage) -> Any:
    from langchain.agents import create_agent

    OFFERED.clear()
    return create_agent(
        model=SeesTools(messages=iter(replies)),
        tools=[web_search, academic_search, get_user_context],
        middleware=[SourceRouteMiddleware()],
        checkpointer=InMemorySaver(),
    )


def test_a_routed_run_is_offered_only_its_sources_tools_and_the_others() -> None:
    agent = routed_agent(done())

    agent.invoke(
        {"messages": [HumanMessage("Q")], "sources": ["academic"]},
        {"configurable": {"thread_id": "1"}},
    )

    assert OFFERED == [{"academic_search", "get_user_context"}]


def test_a_call_to_a_source_outside_the_route_is_refused() -> None:
    agent = routed_agent(tool_turn("web_search", query="q"), done())

    state = agent.invoke(
        {"messages": [HumanMessage("Q")], "sources": ["academic"]},
        {"configurable": {"thread_id": "1"}},
    )

    [result] = [m for m in state["messages"] if isinstance(m, ToolMessage)]
    assert result.status == "error" and "not one of the sources" in result.content


def test_a_run_without_a_route_keeps_every_tool() -> None:
    agent = routed_agent(done())

    agent.invoke(
        {"messages": [HumanMessage("Q")]}, {"configurable": {"thread_id": "1"}}
    )

    assert OFFERED == [{"web_search", "academic_search", "get_user_context"}]


# --- the source tools -----------------------------------------------------------------------


def exa_reply(*results: dict[str, Any], status: int = 200) -> Any:
    return SimpleNamespace(status_code=status, json=lambda: {"results": list(results)})


def call(tool_: Any, **args: Any) -> ToolMessage:
    return tool_.invoke(
        {"name": tool_.name, "args": args, "id": "1", "type": "tool_call"}
    )


def test_academic_search_returns_papers_as_academic_documents(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EXA_API_KEY", "k")
    reply = exa_reply(
        {"url": PAPER, "title": "RAGAS", "text": "We propose RAGAS."},
        {"url": "https://blocked.example/p", "title": "x", "text": "y"},
        {"url": "https://no-text.example/p", "title": "z"},
    )
    with patch("agentlab.tools.academic_search_tool.requests.post", return_value=reply):
        message = call(
            make_academic_search_tool(exclude_domains=["blocked.example"]), query="q"
        )

    assert "We propose RAGAS." in message.content
    documents = documents_read([message])
    assert list(documents) == [PAPER]
    assert documents[PAPER].kind == "academic" and documents[PAPER].title == "RAGAS"


def test_a_failed_academic_search_goes_back_to_the_model_as_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EXA_API_KEY", "k")
    with patch(
        "agentlab.tools.academic_search_tool.requests.post",
        return_value=exa_reply(status=429),
    ):
        message = call(make_academic_search_tool(), query="q")

    assert message.status == "error" and "429" in message.content
    assert documents_read([message]) == {}


def test_corpus_search_joins_chunks_by_file_and_opens_the_index_once() -> None:
    opened: list[int] = []

    class Retriever:
        def invoke(self, query: str) -> list[Document]:
            return [
                Document("Chunk one.", metadata={"source": "AGENTS.md"}),
                Document("Chunk two.", metadata={"source": "AGENTS.md"}),
                Document("Other.", metadata={"source": "README.md"}),
            ]

    def open_index() -> Retriever:
        opened.append(1)
        return Retriever()

    corpus = make_corpus_search_tool(open_index, "this project")  # type: ignore[arg-type]
    assert opened == []  # building the tool opens nothing
    call(corpus, query="a")
    documents = documents_read([call(corpus, query="b")])

    assert opened == [1]
    assert documents["corpus://AGENTS.md"].text == "Chunk one.\n...\nChunk two."
    assert {d.kind for d in documents.values()} == {"corpus"}


def test_a_missing_index_goes_back_to_the_model_as_text() -> None:
    def missing() -> Any:
        raise FileNotFoundError("Index not found. Build it first.")

    message = call(make_corpus_search_tool(missing, "this project"), query="q")

    assert message.status == "error" and "Build it first" in message.content


# --- provenance -----------------------------------------------------------------------------


def supports_everything(_page: str, questions: dict[str, Any], **_: Any) -> Any:
    choice = SimpleNamespace(choice="supports", probabilities={"supports": 0.95})
    return SimpleNamespace(choices={key: choice for key in questions})


def test_each_claim_and_source_carries_the_kind_of_its_documents() -> None:
    draft = ResearchDraft(
        topic="t",
        summary="s",
        claims=[
            DraftClaim(
                text="RAGAS scores faithfulness.",
                evidence=[Evidence(url=PAPER, passage="p")],
            ),
            DraftClaim(
                text="It runs in CI.", evidence=[Evidence(url=PAGE, passage="p")]
            ),
        ],
        citations=[
            Citation(title="paper", url=PAPER),
            Citation(title="docs", url=PAGE),
        ],
    )

    report = check_claims(
        draft,
        {
            PAPER: SourceDocument(url=PAPER, kind="academic", text="paper text"),
            PAGE: SourceDocument(url=PAGE, kind="web", text="page text"),
        },
        decide=supports_everything,
    )

    assert [c.source_kinds for c in report.claims] == [["academic"], ["web"]]
    assert report.citation_kinds == {PAPER: "academic", PAGE: "web"}


def test_the_envelope_names_each_sources_kind() -> None:
    from tests.test_research_options import read

    draft = ResearchDraft(
        topic="t",
        summary="s",
        claims=[DraftClaim(text="c", evidence=[Evidence(url=PAPER, passage="p")])],
        citations=[Citation(title="paper", url=PAPER)],
    )
    agent = SimpleNamespace(
        invoke=lambda *_a, **_k: {
            "messages": [read(PAPER, "paper text", kind="academic")],
            "structured_response": draft,
        }
    )
    with patch.object(
        claim_check_node, "decision_model", SimpleNamespace(decide=supports_everything)
    ):
        result = run_research(agent, "topic")

    assert [(p.kind, p.ref) for p in result.provenance] == [("academic", PAPER)]


# --- the agent's tools ----------------------------------------------------------------------


@pytest.fixture
def scripted_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")  # tools are built, never called
    model = ScriptedToolModel(messages=iter([done()]))
    monkeypatch.setattr(
        researcher_agent, "llm_model", SimpleNamespace(get=lambda *_: model)
    )
    monkeypatch.setattr(researcher_agent, "make_model_fallback", lambda *_: [])


def test_the_factory_builds_an_agent_whose_run_ends_with_a_draft(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The half of the ``Researcher`` contract a type can't hold: the run's structured output."""
    from agentlab.nodes.research_node import read_research_run

    reply = tool_turn("ResearchDraft", topic="t", summary="s", claims=[], citations=[])
    model = ScriptedToolModel(messages=iter([reply]))
    monkeypatch.setattr(
        researcher_agent, "llm_model", SimpleNamespace(get=lambda *_: model)
    )
    monkeypatch.setattr(researcher_agent, "make_model_fallback", lambda *_: [])
    sources_available(monkeypatch, "corpus")

    agent = make_researcher_agent(InMemorySaver())
    state = agent.invoke(
        {"messages": [HumanMessage("Q")]}, {"configurable": {"thread_id": "1"}}
    )

    assert isinstance(read_research_run(state).draft, ResearchDraft)


def tool_names(agent: Any) -> set[str]:
    return set(agent.nodes["tools"].bound.tools_by_name)


def test_the_agent_gets_every_available_sources_tools(
    scripted_model: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    sources_available(monkeypatch, "web", "academic", "corpus")

    agent = make_researcher_agent(InMemorySaver())

    assert tool_names(agent) == {
        "web_search",
        "read_page",
        "academic_search",
        "search_corpus",
    }


def test_outbound_searches_wait_for_approval_and_document_search_does_not(
    scripted_model: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    sources_available(monkeypatch, "web", "academic", "corpus")
    gated: list[list[str]] = []
    real = researcher_agent.hitl_for
    monkeypatch.setattr(
        researcher_agent,
        "hitl_for",
        lambda names, **kw: gated.append(list(names)) or real(names, **kw),
    )

    make_researcher_agent(InMemorySaver())

    assert gated == [["web_search", "academic_search"]]


def test_the_callers_sources_limit_the_agents_tools(
    scripted_model: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    sources_available(monkeypatch, "web", "academic", "corpus")

    agent = make_researcher_agent(
        InMemorySaver(), options=ResearchOptions(sources=["corpus"])
    )

    assert tool_names(agent) == {"search_corpus"}


def test_two_reads_of_one_file_keep_both_parts_and_one_copy_of_the_same() -> None:
    from agentlab.schemas.state.research_state import merge_documents
    from tests.test_research_options import read

    corpus = "corpus://AGENTS.md"
    documents = documents_read(
        [
            read(corpus, "Part one.", kind="corpus"),
            read(corpus, "Part two.", kind="corpus"),
            read(corpus, "Part one.", kind="corpus"),
        ]
    )

    assert documents[corpus].text == "Part one.\n...\nPart two."

    # Parallel runs that read different parts of one file: both parts reach the claim check.
    def doc(url: str, text: str) -> dict[str, SourceDocument]:
        return {url: SourceDocument(url=url, kind="corpus", text=text)}

    merged = merge_documents(doc(corpus, "Part one."), doc(corpus, "Part three."))
    assert merged[corpus].text == "Part one.\n...\nPart three."
    assert merge_documents(doc(PAGE, "Same."), doc(PAGE, "Same."))[PAGE].text == "Same."


# --- files the user gives a run as its corpus -----------------------------------------------


def test_given_files_become_the_corpus_source_and_the_router_is_told_what_they_are(
    tmp_path: Any,
) -> None:
    notes = tmp_path / "notes.md"
    notes.write_text("# Q3 plan", encoding="utf-8")
    options = ResearchOptions(corpus_files=[str(notes)])
    decide = Recorder(answers(q1_web=("no", 0.9), q1_corpus=("yes", 0.9)))

    update = make_route_node(decide)(
        {"topic": "t", "options": options, "questions": ["What is in the Q3 plan?"]}
    )

    assert research_sources(options) == (["web", "corpus"], [])
    assert update["routes"] == {"What is in the Q3 plan?": ["corpus"]}
    [(state, questions, _)] = decide.calls
    assert str(notes) in state and str(notes) in questions["q1_corpus"].criteria["yes"]


def test_only_existing_text_and_markdown_files_are_accepted(tmp_path: Any) -> None:
    from agentlab.retrieval.corpus_retrieval import check_corpus_files

    good = tmp_path / "a.txt"
    good.write_text("x", encoding="utf-8")

    assert check_corpus_files([str(good)]) == [good]
    with pytest.raises(
        ValueError, match=r"report\.pdf: only .*missing\.md: no such file"
    ):
        check_corpus_files([str(good), "report.pdf", str(tmp_path / "missing.md")])


def test_given_files_are_chunked_and_searched_in_memory(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    from langchain_core.embeddings import DeterministicFakeEmbedding

    from agentlab.retrieval import corpus_retrieval

    monkeypatch.setattr(
        corpus_retrieval,
        "make_embeddings",
        lambda: DeterministicFakeEmbedding(size=8),
    )
    notes = tmp_path / "notes.md"
    notes.write_text("The launch moved to May.", encoding="utf-8")

    retriever = corpus_retrieval.build_corpus_retriever([str(notes)], k=1)
    message = call(
        make_corpus_search_tool(lambda: retriever, "notes.md"), query="launch"
    )

    [document] = documents_read([message]).values()
    assert document.kind == "corpus" and "moved to May" in document.text
    assert document.url == f"corpus://{notes.as_posix()}"


def test_the_cli_takes_a_session_mode_and_corpus_files() -> None:
    from agentlab.apps.research_app import parse_args
    from agentlab.subagents.research_subagent import verify_research
    from tests.test_research_options import finished, supports_everything

    args = parse_args(["new", "--depth", "quick", "--corpus", "a.md", "b.txt"])

    assert (args.session, args.depth, args.corpus) == (
        "new",
        "quick",
        ["a.md", "b.txt"],
    )
    defaults = parse_args([])
    assert (defaults.depth, defaults.corpus) == ("standard", [])

    many = [f"c{i}" for i in range(10)]
    state = finished(PAGE, *many)
    with patch.object(
        claim_check_node,
        "decision_model",
        SimpleNamespace(decide=supports_everything),
    ):
        report = verify_research(state, options=ResearchOptions(depth="quick"))

    assert report is not None and len(report.claims) == 6
