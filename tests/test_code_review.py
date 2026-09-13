"""Tests for the P3 code review pipeline: schemas, routing, subgraphs, sandbox, persistence."""

import pytest
from langgraph.checkpoint.sqlite import SqliteSaver

from agentlab.graphs.code_review_parentgraph import (
    build_code_review_graph,
    route_after_reviewer,
    route_after_test_gen,
)
from agentlab.graphs.refactor_subgraph import (
    build_refactor_subgraph,
    route_after_approval,
)
from agentlab.graphs.reviewer_subgraph import build_reviewer_subgraph
from agentlab.graphs.test_gen_subgraph import (
    build_test_gen_subgraph,
    route_after_execution,
)
from agentlab.schemas.output import code_review_output_schema as code_review_schemas
from agentlab.subagents.code_review_subagent import make_code_review_subagent
from agentlab.utils.sandbox_util import run_tests_in_sandbox
from agentlab.utils.time_travel_util import inspect_state_history


def test_code_review_schemas() -> None:
    issue = code_review_schemas.CodeIssue(
        line_number=5,
        severity="critical",
        category="bug",
        description="Index out of range",
        suggestion="Add bounds check",
    )
    review = code_review_schemas.ReviewResult(summary="Found 1 critical bug", score=4, issues=[issue])
    suite = code_review_schemas.TestSuite(
        test_code="def test_bounds(): assert True",
        test_cases=[code_review_schemas.TestCase(name="test_bounds", description="bounds", target_function="get_item")],
    )

    assert review.issues[0].severity == "critical"
    assert suite.framework == "pytest"


def test_graph_routing() -> None:
    with_refactor = code_review_schemas.ReviewResult(summary="ok", score=8, refactored_code="def foo(): pass")
    without_refactor = code_review_schemas.ReviewResult(summary="ok", score=10)
    passed = code_review_schemas.TestExecutionResult(status="passed", passed=True, exit_code=0, output="OK")
    failed = code_review_schemas.TestExecutionResult(status="failed", passed=False, exit_code=1, output="Error")

    assert route_after_reviewer({"error": "Fatal error"}) == "__end__"
    assert route_after_reviewer({"error": None}) == "test_generator"

    assert route_after_test_gen({"error": "Failed", "review": None}) == "__end__"
    assert route_after_test_gen({"error": None, "review": with_refactor}) == "refactor_gate"
    assert route_after_test_gen({"error": None, "review": without_refactor}) == "__end__"

    assert route_after_execution({"test_execution": passed, "test_retries": 0}) == "__end__"
    assert route_after_execution({"test_execution": failed, "test_retries": 1}) == "fix_tests"
    assert route_after_execution({"test_execution": failed, "test_retries": 2}) == "__end__"
    override = {"configurable": {"max_test_retries": 5}}
    assert route_after_execution({"test_execution": failed, "test_retries": 2}, config=override) == "fix_tests"

    assert route_after_approval({"refactor_decision": "approve"}) == "apply_refactor"
    assert route_after_approval({"refactor_decision": "reject"}) == "__end__"


def test_subgraphs_compile() -> None:
    for graph in (
        build_reviewer_subgraph(),
        build_test_gen_subgraph(),
        build_refactor_subgraph(),
        build_code_review_graph(),
    ):
        assert graph is not None


def test_sandbox_runs_passing_and_failing_tests() -> None:
    source = "def is_even(n: int) -> bool:\n    return n % 2 == 0\n"
    template = "from tested_module import is_even\ndef test_even():\n    assert is_even({n}) is True\n"

    passing = run_tests_in_sandbox(code=source, test_code=template.format(n=4))
    failing = run_tests_in_sandbox(code=source, test_code=template.format(n=3))

    assert (passing.passed, passing.status, passing.exit_code) == (True, "passed", 0)
    assert (failing.passed, failing.status) == (False, "failed")


def test_sandbox_tests_cannot_read_process_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENTLAB_FAKE_SECRET", "leaked")
    test_code = "import os\ndef test_env():\n    assert os.getenv('AGENTLAB_FAKE_SECRET') is None\n"

    assert run_tests_in_sandbox(code="", test_code=test_code).passed


def test_sqlite_checkpointer_and_time_travel() -> None:
    with SqliteSaver.from_conn_string(":memory:") as saver:
        graph = build_code_review_graph(checkpointer=saver)
        config = {"configurable": {"thread_id": "empty_thread"}}
        assert graph.get_state(config).values == {}
        assert inspect_state_history(graph, thread_id="empty_thread") == []


def test_code_review_subagent_spec() -> None:
    spec = make_code_review_subagent(graph=build_code_review_graph())

    assert spec["name"] == "code_review_subagent"
    assert spec["description"]
    assert callable(spec["runnable"].invoke)
