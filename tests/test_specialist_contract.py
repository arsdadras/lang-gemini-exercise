"""Tests for the specialist contract: the envelope and each specialist's boundary.

The boundaries run against scripted stand-ins for the specialists' graphs and agents, whose
final states mirror what the real ones return (verified live in R0).
"""

from pathlib import Path
from typing import Any
from unittest.mock import patch

import httpx
import pytest
from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from langgraph.store.memory import InMemoryStore
from langgraph.types import Interrupt

from agentlab.nodes import code_review_node, rag_node
from agentlab.schemas.output import code_review_output_schema as review_schemas
from agentlab.schemas.output.research_output_schema import ResearchReport
from agentlab.schemas.output.specialist_output_schema import (
    Provenance,
    SideEffect,
    SpecialistResult,
)
from agentlab.subagents.code_review_subagent import run_code_review
from agentlab.subagents.interpreter_subagent import run_interpreter
from agentlab.subagents.rag_subagent import run_rag
from agentlab.subagents.research_subagent import run_research
from agentlab.tools.user_context_tool import read_user_context
from agentlab.tools.web_search_tool import WebSearchError
from agentlab.utils.subagent_util import pending_approvals


class Returns:
    """A graph or agent stand-in: ``invoke`` returns a fixed final state and records its input."""

    def __init__(self, state: dict[str, Any], effect: Any = None) -> None:
        self.state = state
        self.effect = effect
        self.inputs: list[Any] = []

    def invoke(
        self,
        payload: Any,
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.inputs.append(payload)
        if self.effect:
            self.effect()
        return self.state


class Raises:
    """A graph or agent stand-in whose ``invoke`` raises ``error``, after an optional side effect."""

    def __init__(self, error: Exception, effect: Any = None) -> None:
        self.error = error
        self.effect = effect

    def invoke(
        self, payload: Any, config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        if self.effect:
            self.effect()
        raise self.error


def rejected(status: int) -> httpx.HTTPStatusError:
    """A real HTTP error with ``status``, as a provider SDK's transport raises it."""
    request = httpx.Request("POST", "https://api.example/v1")
    response = httpx.Response(status, request=request)
    return httpx.HTTPStatusError(f"HTTP {status}", request=request, response=response)


def approval_interrupt(name: str) -> Interrupt:
    return Interrupt(
        value={"action_requests": [{"name": name, "args": {}, "description": ""}]},
        id="i1",
    )


# --- the envelope -------------------------------------------------------------------------


def test_the_envelope_puts_status_sources_and_changes_before_the_answer() -> None:
    result = SpecialistResult[str](
        specialist="rag",
        status="partial",
        reason="Answered from the web.",
        output="The answer.",
        provenance=[Provenance(kind="web", ref="https://a.example", title="A")],
        side_effects=[SideEffect(action="created", target="artifacts/x.csv")],
    )

    assert result.to_text() == (
        "[rag] status: partial (Answered from the web.)\nSources: web: A\nChanged: created artifacts/x.csv\n\nThe answer."
    )


def test_the_output_type_is_validated() -> None:
    report = ResearchReport(
        topic="t",
        summary="s",
        claims=[],
        citations=[],
        confidence=0.5,
    )

    result = SpecialistResult[ResearchReport].model_validate(
        {"specialist": "research", "status": "ok", "output": report.model_dump()},
    )

    assert isinstance(result.output, ResearchReport)


def test_pending_approvals_names_what_a_paused_run_waits_for() -> None:
    assert (
        pending_approvals({"__interrupt__": [approval_interrupt("web_search")]})
        == "web_search"
    )
    assert pending_approvals(
        {
            "__interrupt__": [
                Interrupt(value={"action_required": "Refactor Approval"}, id="i"),
            ],
        },
    ) == ("Refactor Approval")
    assert pending_approvals({"messages": []}) == ""


# --- P2 -------------------------------------------------------------------------------------

CORPUS_DOC = Document(
    page_content="...",
    metadata={"source": "src/agentlab/graphs/rag_graph.py"},
)


def test_rag_from_the_corpus_is_ok_with_file_sources() -> None:
    graph = Returns(
        {
            "generation": "It retrieves.",
            "answer_source": "corpus",
            "documents": [CORPUS_DOC, CORPUS_DOC],
        },
    )

    result = run_rag(graph, "What does the RAG graph do?")

    assert (result.status, result.output) == ("ok", "It retrieves.")
    assert result.provenance == [
        Provenance(kind="corpus", ref="src/agentlab/graphs/rag_graph.py"),
    ]
    assert graph.inputs[0]["retries"] == 0


def test_rag_from_the_web_is_partial_and_says_so() -> None:
    web = Document(page_content="...", metadata={"source": "https://pmc.example/mg"})
    result = run_rag(
        Returns(
            {
                "generation": "In neuroscience...",
                "answer_source": "web",
                "documents": [web],
            },
        ),
        "q",
    )

    assert result.status == "partial" and "answered from the web" in result.reason
    assert result.provenance == [Provenance(kind="web", ref="https://pmc.example/mg")]


def test_rag_without_a_supported_answer_fails_without_output() -> None:
    unverified = run_rag(
        Returns(
            {"generation": rag_node.UNVERIFIED_ANSWER, "answer_source": "unverified"},
        ),
        "q",
    )
    nothing = run_rag(
        Returns({"generation": rag_node.NO_ANSWER, "answer_source": "none"}),
        "q",
    )

    assert (unverified.status, unverified.output) == ("failed", None)
    assert (nothing.status, nothing.output) == ("failed", None)


def test_the_web_search_keeps_its_urls_and_the_answer_records_its_source() -> None:
    results = {"results": [{"url": "https://a.example", "content": "A"}]}
    with patch.object(rag_node, "make_web_search_tool") as tool:
        tool.return_value.invoke.return_value = results
        searched = rag_node.web_search_node({"question": "q"})
    with patch.object(
        rag_node.llm_model,
        "chain",
        return_value=lambda _: AIMessage(content="From A."),
    ):
        answered = rag_node.generate_from_web_node({"question": "q", **searched})

    assert [document.metadata["source"] for document in searched["documents"]] == [
        "https://a.example",
    ]
    assert answered == {"generation": "From A.", "answer_source": "web"}


def test_a_web_search_outage_is_raised_not_reported_as_no_results() -> None:
    outage = {"error": ValueError("Error 503: Service Unavailable")}
    with patch.object(rag_node, "make_web_search_tool") as tool:
        tool.return_value.invoke.return_value = outage
        with pytest.raises(WebSearchError) as raised:
            rag_node.web_search_node({"question": "q"})

    assert raised.value.status_code == 503


def test_rag_fails_on_an_outage_but_raises_a_bug() -> None:
    down = httpx.ConnectError("connection refused")

    result = run_rag(Raises(down), "q")

    assert (result.status, result.output) == ("failed", None)
    assert result.reason.startswith("An external service was unavailable")
    with pytest.raises(KeyError):
        run_rag(Raises(KeyError("generation")), "q")


# --- P1 -------------------------------------------------------------------------------------


def test_research_stopped_at_an_approval_is_partial_without_output() -> None:
    result = run_research(
        Returns({"messages": [], "__interrupt__": [approval_interrupt("web_search")]}),
        "topic",
    )

    assert result.status == "partial"
    assert (
        result.reason == "Stopped before finishing: waiting for approval of web_search."
    )
    assert result.output is None


def test_research_without_a_report_fails() -> None:
    assert run_research(Returns({"messages": []}), "topic").status == "failed"


def test_research_fails_when_every_provider_is_down() -> None:
    result = run_research(Raises(rejected(503)), "topic")

    assert result.status == "failed" and "unavailable" in result.reason


# --- P3 -------------------------------------------------------------------------------------

REVIEW = review_schemas.ReviewResult(
    summary="Buggy.",
    score=3,
    issues=[],
    refactored_code="def f(): ...",
)
TESTS = review_schemas.TestSuite(test_code="def test_f(): ...")
RAN = review_schemas.TestExecutionResult(
    status="failed",
    passed=False,
    exit_code=1,
    output="1 failed",
)


def test_a_review_with_failing_tests_is_still_ok() -> None:
    result = run_code_review(
        Returns({"review": REVIEW, "tests": TESTS, "test_execution": RAN}),
        "code",
    )

    assert result.status == "ok"
    assert result.output.test_execution == RAN


def test_a_refactor_waiting_for_approval_is_no_longer_swallowed() -> None:
    interrupt = Interrupt(value={"action_required": "Refactor Approval"}, id="i")
    state = {
        "review": REVIEW,
        "tests": TESTS,
        "test_execution": RAN,
        "__interrupt__": [interrupt],
    }

    result = run_code_review(Returns(state), "code")

    assert result.status == "partial"
    assert "refactor waits for approval (Refactor Approval)" in result.reason
    assert result.output.applied_code is None


def test_tests_that_did_not_run_make_the_review_partial() -> None:
    timed_out = review_schemas.TestExecutionResult(
        status="timed_out",
        passed=False,
        exit_code=-1,
        output="",
    )

    assert (
        run_code_review(
            Returns({"review": REVIEW, "tests": TESTS, "test_execution": timed_out}),
            "c",
        ).status
        == "partial"
    )
    assert run_code_review(Returns({"review": REVIEW}), "c").status == "partial"


def test_a_review_that_never_happened_fails_with_the_pipeline_error() -> None:
    result = run_code_review(Returns({"error": "LLM unavailable"}), "code")

    assert (result.status, result.reason) == ("failed", "LLM unavailable")


def test_a_review_node_reports_an_external_failure_and_raises_a_bug() -> None:
    def failing(error: Exception) -> Any:
        def invoke(_: Any) -> Any:
            raise error

        return invoke

    state = {"code": "x = 1"}
    with patch.object(
        code_review_node.llm_model, "chain", return_value=failing(rejected(401))
    ):
        update = code_review_node.review_code_node(state)
    with (
        patch.object(
            code_review_node.llm_model, "chain", return_value=failing(TypeError("bug"))
        ),
        pytest.raises(TypeError),
    ):
        code_review_node.review_code_node(state)

    assert update["error"].startswith(
        "Review node failed: An external service rejected"
    )


# --- P4 -------------------------------------------------------------------------------------


def test_files_the_interpreter_writes_become_side_effects(tmp_path: Path) -> None:
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "artifacts" / "old.txt").write_text("kept", encoding="utf-8")
    agent = Returns(
        {"messages": [AIMessage(content="Mean is 6.")]},
        effect=lambda: (tmp_path / "artifacts" / "mean.txt").write_text(
            "6.0",
            encoding="utf-8",
        ),
    )

    result = run_interpreter(agent, "compute", sandbox_dir=tmp_path)

    assert (result.status, result.output) == ("ok", "Mean is 6.")
    assert [(effect.action, effect.target) for effect in result.side_effects] == [
        ("created", "artifacts/mean.txt"),
    ]


def test_an_artifact_changed_in_place_is_a_modified_side_effect(tmp_path: Path) -> None:
    (tmp_path / "artifacts").mkdir()
    report = tmp_path / "artifacts" / "report.md"
    report.write_text("v1", encoding="utf-8")
    agent = Returns(
        {"messages": [AIMessage(content="Updated.")]},
        effect=lambda: report.write_text("v2, longer", encoding="utf-8"),
    )

    result = run_interpreter(agent, "update the report", sandbox_dir=tmp_path)

    assert [(effect.action, effect.target) for effect in result.side_effects] == [
        ("modified", "artifacts/report.md"),
    ]


def test_an_interpreter_waiting_to_run_a_command_is_partial(tmp_path: Path) -> None:
    state = {
        "messages": [AIMessage(content="")],
        "__interrupt__": [approval_interrupt("execute")],
    }

    result = run_interpreter(Returns(state), "compute", sandbox_dir=tmp_path)

    assert result.status == "partial" and "execute" in result.reason


def test_files_written_before_a_failure_are_still_reported(tmp_path: Path) -> None:
    (tmp_path / "artifacts").mkdir()
    agent = Raises(
        httpx.ReadTimeout("model timed out"),
        effect=lambda: (tmp_path / "artifacts" / "half.csv").write_text(
            "a,b", encoding="utf-8"
        ),
    )

    result = run_interpreter(agent, "compute", sandbox_dir=tmp_path)

    assert result.status == "failed" and result.output is None
    assert [(effect.action, effect.target) for effect in result.side_effects] == [
        ("created", "artifacts/half.csv"),
    ]


# --- P5 -------------------------------------------------------------------------------------


def test_user_context_is_ok_even_when_empty_and_cites_memory_files() -> None:
    store = InMemoryStore()
    store.put(
        ("sara", "memories"),
        "/user_profile.md",
        {"content": "- Vegetarian", "encoding": "utf-8"},
    )

    sara, nobody = read_user_context(store, "sara"), read_user_context(store, "nobody")

    assert (sara.status, sara.output) == (
        "ok",
        {"/memories/user_profile.md": "- Vegetarian"},
    )
    assert sara.provenance == [
        Provenance(kind="memory", ref="/memories/user_profile.md"),
    ]
    assert (nobody.status, nobody.output) == ("ok", {})
