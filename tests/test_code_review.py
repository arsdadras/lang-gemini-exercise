"""Unit tests for P3 Code Review & Test Generation components and Subgraphs."""

from graphs.code_review_graph import (
    build_code_review_graph,
    route_after_reviewer,
    route_after_test_gen,
)
from graphs.refactor_subgraph import build_refactor_subgraph, route_after_approval
from graphs.reviewer_subgraph import build_reviewer_subgraph
from graphs.test_gen_subgraph import build_test_gen_subgraph, route_after_execution
from output_schemas.code_review_output_schema import (
    CodeIssue,
    ReviewResult,
    TestCase,
    TestExecutionResult,
    TestSuite,
)
from utils.sandbox import run_tests_in_sandbox


def test_code_review_schemas():
    """Verify instantiation and validation of P3 schemas."""
    issue = CodeIssue(
        line_number=5,
        severity="critical",
        category="bug",
        description="Index out of range",
        suggestion="Add bounds check",
    )
    assert issue.severity == "critical"

    review = ReviewResult(
        summary="Found 1 critical bug",
        score=4,
        issues=[issue],
        refactored_code="def safe(): pass",
    )
    assert review.score == 4
    assert len(review.issues) == 1

    tc = TestCase(
        name="test_bounds",
        description="Verify list bounds check",
        target_function="get_item",
    )
    suite = TestSuite(
        framework="pytest",
        test_code="def test_bounds(): assert True",
        test_cases=[tc],
    )
    assert suite.framework == "pytest"


def test_graph_routing():
    """Verify conditional edges logic across subgraphs and parent pipeline."""
    # Parent routing after reviewer
    assert route_after_reviewer({"error": "Fatal error"}) == "__end__"
    assert route_after_reviewer({"error": None}) == "test_generator"

    # Parent routing after test gen
    review_with_refactor = ReviewResult(summary="ok", score=8, refactored_code="def foo(): pass")
    review_no_refactor = ReviewResult(summary="ok", score=10, refactored_code=None)
    assert route_after_test_gen({"error": "Failed test gen", "review": None}) == "__end__"
    assert route_after_test_gen({"error": None, "review": review_with_refactor}) == "refactor_gate"
    assert route_after_test_gen({"error": None, "review": review_no_refactor}) == "__end__"

    # TestGen Subgraph routing (Self-Correction loop)
    pass_exec = TestExecutionResult(status="passed", passed=True, exit_code=0, output="OK")
    fail_exec = TestExecutionResult(status="failed", passed=False, exit_code=1, output="Error")

    assert route_after_execution({"test_execution": pass_exec, "test_retries": 0}) == "__end__"
    assert route_after_execution({"test_execution": fail_exec, "test_retries": 0}) == "fix_tests"
    assert route_after_execution({"test_execution": fail_exec, "test_retries": 1}) == "fix_tests"
    assert route_after_execution({"test_execution": fail_exec, "test_retries": 2}) == "__end__"

    # Runtime override via configurable
    config_5 = {"configurable": {"max_test_retries": 5}}
    assert route_after_execution({"test_execution": fail_exec, "test_retries": 2}, config=config_5) == "fix_tests"
    assert route_after_execution({"test_execution": fail_exec, "test_retries": 5}, config=config_5) == "__end__"

    # Refactor Subgraph routing (HITL)
    assert route_after_approval({"refactor_decision": "approve"}) == "apply_refactor"
    assert route_after_approval({"refactor_decision": "yes"}) == "apply_refactor"
    assert route_after_approval({"refactor_decision": "reject"}) == "__end__"
    assert route_after_approval({"refactor_decision": "skip"}) == "__end__"


def test_subgraphs_compilation():
    """Verify that all 3 subgraphs and parent graph compile cleanly."""
    rev_graph = build_reviewer_subgraph()
    assert rev_graph is not None

    test_graph = build_test_gen_subgraph()
    assert test_graph is not None

    ref_graph = build_refactor_subgraph()
    assert ref_graph is not None

    parent_graph = build_code_review_graph()
    assert parent_graph is not None


def test_sandbox_execution():
    """Verify local subprocess sandbox execution for passing and failing test code."""
    source_code = "def is_even(n: int) -> bool:\n    return n % 2 == 0\n"

    # 1. Passing test (default sandbox_type="local")
    pass_test = "from tested_module import is_even\ndef test_even():\n    assert is_even(4) is True\n"
    res_pass = run_tests_in_sandbox(code=source_code, test_code=pass_test, sandbox_type="local")
    assert res_pass.passed is True
    assert res_pass.status == "passed"
    assert res_pass.exit_code == 0

    # 2. Failing test
    fail_test = "from tested_module import is_even\ndef test_even():\n    assert is_even(3) is True\n"
    res_fail = run_tests_in_sandbox(code=source_code, test_code=fail_test)
    assert res_fail.passed is False
    assert res_fail.status == "failed"
    assert res_fail.exit_code != 0

    # 3. Deferred / Unimplemented backend test
    res_cloud = run_tests_in_sandbox(code=source_code, test_code=pass_test, sandbox_type="cloud")
    assert res_cloud.status == "error"
    assert "P4" in res_cloud.output


def test_sqlite_checkpointer():
    """Verify that build_code_review_graph compiles and saves checkpoints via SqliteSaver."""
    from langgraph.checkpoint.sqlite import SqliteSaver

    with SqliteSaver.from_conn_string(":memory:") as saver:
        graph = build_code_review_graph(checkpointer=saver)
        assert graph is not None
        config = {"configurable": {"thread_id": "test_sqlite_session"}}
        state_snap = graph.get_state(config)
        assert state_snap.values == {}


def test_subagent_schema():
    """Verify that code_review_subagent is properly registered and conformant to DeepAgents schema."""
    from subagents import code_review_subagent

    assert code_review_subagent["name"] == "code_review_subagent"
    assert "description" in code_review_subagent
    assert "runnable" in code_review_subagent
    assert callable(code_review_subagent["runnable"].invoke)


def test_time_travel_utilities():
    """Verify time-travel history inspection and fork mechanisms."""
    from langgraph.checkpoint.sqlite import SqliteSaver
    from utils.time_travel import inspect_state_history

    with SqliteSaver.from_conn_string(":memory:") as saver:
        graph = build_code_review_graph(checkpointer=saver)
        history = inspect_state_history(graph, thread_id="empty_thread")
        assert isinstance(history, list)
        assert len(history) == 0


