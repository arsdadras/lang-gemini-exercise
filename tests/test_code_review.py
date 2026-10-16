from typing import Any
from unittest.mock import patch

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
    review = code_review_schemas.CodeReview(
        summary="Found 1 critical bug",
        score=4,
        issues=[issue],
    )
    suite = code_review_schemas.TestSuite(
        test_code="def test_bounds(): assert True",
        test_cases=[
            code_review_schemas.TestCase(
                name="test_bounds",
                description="bounds",
                target_function="get_item",
            ),
        ],
    )

    assert review.issues[0].severity == "critical"
    assert suite.framework == "pytest"


def test_graph_routing() -> None:
    with_refactor = code_review_schemas.CodeReview(
        summary="ok",
        score=8,
        refactored_code="def foo(): pass",
    )
    without_refactor = code_review_schemas.CodeReview(summary="ok", score=10)
    passed = code_review_schemas.TestRun(
        status="passed",
        passed=True,
        exit_code=0,
        output="OK",
    )
    failed = code_review_schemas.TestRun(
        status="failed",
        passed=False,
        exit_code=1,
        output="Error",
    )

    assert route_after_reviewer({"error": "Fatal error"}) == "__end__"
    assert route_after_reviewer({"error": None}) == "test_generator"

    assert route_after_test_gen({"error": "Failed", "review": None}) == "__end__"
    assert (
        route_after_test_gen({"error": None, "review": with_refactor})
        == "refactor_gate"
    )
    assert (
        route_after_test_gen({"error": None, "review": without_refactor}) == "__end__"
    )

    assert route_after_execution({"test_run": passed, "test_retries": 0}) == "__end__"
    assert route_after_execution({"test_run": failed, "test_retries": 1}) == "fix_tests"
    assert route_after_execution({"test_run": failed, "test_retries": 2}) == "__end__"
    override = {"configurable": {"max_test_retries": 5}}
    assert (
        route_after_execution(
            {"test_run": failed, "test_retries": 2},
            config=override,
        )
        == "fix_tests"
    )

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


def test_sandbox_tests_cannot_read_process_secrets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AGENTLAB_FAKE_SECRET", "leaked")
    test_code = "import os\ndef test_env():\n    assert os.getenv('AGENTLAB_FAKE_SECRET') is None\n"

    assert run_tests_in_sandbox(code="", test_code=test_code).passed


def test_sqlite_checkpointer_and_time_travel() -> None:
    with SqliteSaver.from_conn_string(":memory:") as saver:
        graph = build_code_review_graph(checkpointer=saver)
        config = {"configurable": {"thread_id": "empty_thread"}}
        assert graph.get_state(config).values == {}
        assert inspect_state_history(graph, thread_id="empty_thread") == []


def test_time_travel_inspect_history_and_fork() -> None:
    from langchain_core.messages import HumanMessage
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.graph import END, START, MessagesState, StateGraph

    from agentlab.utils.time_travel_util import fork_from_checkpoint

    builder = StateGraph(MessagesState)
    builder.add_node("step1", lambda s: {"messages": [HumanMessage("step 1")]})
    builder.add_node("step2", lambda s: {"messages": [HumanMessage("step 2")]})
    builder.add_edge(START, "step1")
    builder.add_edge("step1", "step2")
    builder.add_edge("step2", END)

    saver = InMemorySaver()
    app = builder.compile(checkpointer=saver)
    config = {"configurable": {"thread_id": "history_thread"}}
    app.invoke({"messages": []}, config=config)

    history = inspect_state_history(app, thread_id="history_thread")
    assert len(history) >= 2
    assert history[0]["step"] <= history[-1]["step"]
    assert "messages" in history[-1]["state_keys"]

    # Fork from earlier checkpoint
    first_checkpoint_id = history[0]["checkpoint_id"]
    forked = fork_from_checkpoint(
        app,
        thread_id="history_thread",
        checkpoint_id=first_checkpoint_id,
    )
    assert forked is not None


def test_code_review_subagent_spec() -> None:
    spec = make_code_review_subagent(graph=build_code_review_graph())

    assert spec["name"] == "code_review_subagent"
    assert spec["description"]
    assert callable(spec["runnable"].invoke)


def test_execute_tests_node_runs_against_refactored_code_when_present() -> None:
    from agentlab.nodes.code_review_node import execute_tests_node

    buggy = "def add(a: int, b: int) -> int:\n    return a - b\n"
    fixed = "def add(a: int, b: int) -> int:\n    return a + b\n"
    suite = code_review_schemas.TestSuite(
        test_code="from tested_module import add\ndef test_add():\n    assert add(2, 3) == 5\n",
        test_cases=[],
    )
    with_refactor = execute_tests_node(
        {
            "code": buggy,
            "review": code_review_schemas.CodeReview(
                summary="fix", score=5, refactored_code=fixed
            ),
            "tests": suite,
        }
    )
    without_refactor = execute_tests_node(
        {
            "code": buggy,
            "review": code_review_schemas.CodeReview(summary="no fix", score=5),
            "tests": suite,
        }
    )

    assert with_refactor["test_run"].passed is True
    assert without_refactor["test_run"].passed is False


def test_prune_checkpoints_keeps_latest_per_thread(
    tmp_path: pytest.TempPathFactory,
) -> None:
    from pathlib import Path

    from agentlab.data.sqlite_db_data import get_sqlite_checkpointer, prune_checkpoints
    from agentlab.graphs.reviewer_subgraph import build_reviewer_subgraph

    db_path = Path(str(tmp_path)) / "checkpoints.db"
    saver = get_sqlite_checkpointer(db_path)
    try:
        graph = build_reviewer_subgraph()
        config = {"configurable": {"thread_id": "t1", "checkpoint_ns": ""}}
        for step in range(4):
            saver.put(
                {
                    "configurable": {
                        "thread_id": "t1",
                        "checkpoint_ns": "",
                        "checkpoint_id": f"cp-{step:03d}",
                    }
                },
                {
                    "v": 1,
                    "id": f"cp-{step:03d}",
                    "ts": f"2026-10-11T00:00:0{step}Z",
                    "channel_values": {},
                    "channel_versions": {},
                    "versions_seen": {},
                    "pending_sends": [],
                },
                {"source": "input", "step": step, "writes": {}, "parents": {}},
                {},
            )
        deleted = prune_checkpoints(db_path, keep_latest=2)
        remaining = list(saver.list(config))
    finally:
        saver.conn.close()

    assert graph is not None
    assert deleted == 2
    assert [item.checkpoint["id"] for item in remaining] == ["cp-003", "cp-002"]


def test_format_review_summary_variations() -> None:
    from agentlab.nodes.code_review_node import _format_review_summary

    assert _format_review_summary(None) == "No prior review findings available."

    empty_review = code_review_schemas.CodeReview(
        summary="No issues found.",
        score=10,
        issues=[],
    )
    formatted_empty = _format_review_summary(empty_review)
    assert "Overall Quality Score: 10/10" in formatted_empty
    assert "Summary: No issues found." in formatted_empty
    assert "Identified Issues" not in formatted_empty
    assert "Refactored Code Version" not in formatted_empty

    detailed_review = code_review_schemas.CodeReview(
        summary="Found 2 issues.",
        score=6,
        issues=[
            code_review_schemas.CodeIssue(
                line_number=12,
                severity="warning",
                category="performance",
                description="Quadratic loop",
                suggestion="Use a set",
            ),
            code_review_schemas.CodeIssue(
                line_number=None,
                severity="critical",
                category="security",
                description="Hardcoded credential",
                suggestion="Use environment variable",
            ),
        ],
        refactored_code="def fast_and_secure(): pass",
    )
    formatted_detailed = _format_review_summary(detailed_review)
    assert "Line 12: Quadratic loop" in formatted_detailed
    assert "[CRITICAL] (security) Hardcoded credential" in formatted_detailed
    assert "def fast_and_secure(): pass" in formatted_detailed


def test_review_code_node_happy_path_and_failure() -> None:
    import httpx
    from langchain_core.runnables import RunnableLambda

    from agentlab.nodes.code_review_node import review_code_node

    expected_review = code_review_schemas.CodeReview(summary="Nice", score=9)

    with patch(
        "agentlab.nodes.code_review_node.llm_model.chain",
        return_value=RunnableLambda(lambda _: expected_review),
    ):
        result = review_code_node({"code": "def foo(): pass"})
        assert result["review"] == expected_review
        assert result["error"] is None

    # Transient error is caught and converted to state error
    with patch(
        "agentlab.nodes.code_review_node.llm_model.chain",
        return_value=RunnableLambda(
            lambda _: (_ for _ in ()).throw(httpx.ConnectError("Gateway down"))
        ),
    ):
        err_result = review_code_node({"code": "def foo(): pass"})
        assert "Review node failed:" in err_result["error"]

    # Non-transient bug is re-raised
    with (
        patch(
            "agentlab.nodes.code_review_node.llm_model.chain",
            return_value=RunnableLambda(
                lambda _: (_ for _ in ()).throw(ValueError("Internal logic error"))
            ),
        ),
        pytest.raises(ValueError, match="Internal logic error"),
    ):
        review_code_node({"code": "def foo(): pass"})


def test_generate_tests_node_happy_path_and_failure() -> None:
    import httpx
    from langchain_core.runnables import RunnableLambda

    from agentlab.nodes.code_review_node import generate_tests_node

    expected_suite = code_review_schemas.TestSuite(
        test_code="def test_ok(): assert True",
        test_cases=[],
    )

    with patch(
        "agentlab.nodes.code_review_node.llm_model.chain",
        return_value=RunnableLambda(lambda _: expected_suite),
    ):
        result = generate_tests_node(
            {
                "code": "def bar(): pass",
                "review": code_review_schemas.CodeReview(summary="ok", score=8),
                "language": "python",
            }
        )
        assert result["tests"] == expected_suite
        assert result["error"] is None

    with patch(
        "agentlab.nodes.code_review_node.llm_model.chain",
        return_value=RunnableLambda(
            lambda _: (_ for _ in ()).throw(httpx.ConnectError("Network timeout"))
        ),
    ):
        err_result = generate_tests_node({"code": "def bar(): pass"})
        assert "Test generation node failed:" in err_result["error"]

    with (
        patch(
            "agentlab.nodes.code_review_node.llm_model.chain",
            return_value=RunnableLambda(
                lambda _: (_ for _ in ()).throw(TypeError("Unexpected type bug"))
            ),
        ),
        pytest.raises(TypeError, match="Unexpected type bug"),
    ):
        generate_tests_node({"code": "def bar(): pass"})


def test_fix_tests_node_happy_path_and_failure() -> None:
    import httpx
    from langchain_core.runnables import RunnableLambda

    from agentlab.nodes.code_review_node import fix_tests_node

    fixed_suite = code_review_schemas.TestSuite(
        test_code="def test_fixed(): assert True",
        test_cases=[],
    )

    with patch(
        "agentlab.nodes.code_review_node.llm_model.chain",
        return_value=RunnableLambda(lambda _: fixed_suite),
    ):
        result = fix_tests_node(
            {
                "code": "def buggy(): pass",
                "tests": code_review_schemas.TestSuite(test_code="def test_bad(): ..."),
                "test_run": code_review_schemas.TestRun(
                    status="failed", passed=False, exit_code=1, output="AssertionError"
                ),
                "test_retries": 1,
            }
        )
        assert result["tests"] == fixed_suite
        assert result["test_retries"] == 2
        assert result["error"] is None

    with patch(
        "agentlab.nodes.code_review_node.llm_model.chain",
        return_value=RunnableLambda(
            lambda _: (_ for _ in ()).throw(httpx.ConnectError("Connection drop"))
        ),
    ):
        err_result = fix_tests_node({"code": "def buggy(): pass"})
        assert "Test fix node failed:" in err_result["error"]

    with (
        patch(
            "agentlab.nodes.code_review_node.llm_model.chain",
            return_value=RunnableLambda(
                lambda _: (_ for _ in ()).throw(KeyError("State key missing"))
            ),
        ),
        pytest.raises(KeyError),
    ):
        fix_tests_node({"code": "def buggy(): pass"})


def test_approved_refactor_and_apply_refactor_nodes() -> None:
    from agentlab.nodes.code_review_node import (
        apply_refactor_node,
        approved_refactor_node,
    )

    # approved_refactor_node skips if no refactored_code
    assert approved_refactor_node({}) == {"refactor_decision": "skip"}
    assert approved_refactor_node(
        {"review": code_review_schemas.CodeReview(summary="ok", score=9)}
    ) == {"refactor_decision": "skip"}

    # approved_refactor_node asks human via interrupt when refactored_code is present
    with patch(
        "agentlab.nodes.code_review_node.interrupt",
        return_value="  Approve  ",
    ) as mock_interrupt:
        decision = approved_refactor_node(
            {
                "review": code_review_schemas.CodeReview(
                    summary="Improvement", score=8, refactored_code="def new(): pass"
                )
            }
        )
        mock_interrupt.assert_called_once()
        assert decision == {"refactor_decision": "approve"}

    # apply_refactor_node
    assert apply_refactor_node({"code": "orig"}) == {"applied_code": "orig"}
    assert apply_refactor_node(
        {
            "code": "orig",
            "review": code_review_schemas.CodeReview(
                summary="fix", score=8, refactored_code="new_code"
            ),
        }
    ) == {"applied_code": "new_code"}


def test_render_outcome_and_workflow_helpers() -> None:
    from agentlab.workflows.code_review_workflow import (
        CODE_REVIEW_SPECIALIST,
        _default_code_review_graph,
        render_outcome,
        run_code_review,
    )

    report = code_review_schemas.CodeReviewReport(
        review=code_review_schemas.CodeReview(
            summary="Needs improvement.",
            score=5,
            issues=[
                code_review_schemas.CodeIssue(
                    line_number=3,
                    severity="critical",
                    category="bug",
                    description="Null dereference",
                    suggestion="Add null check",
                ),
            ],
            refactored_code="def safe(): pass",
        ),
        tests=code_review_schemas.TestSuite(
            test_code="def test_safe(): pass",
            test_cases=[
                code_review_schemas.TestCase(
                    name="test_safe", description="safe", target_function="safe"
                )
            ],
        ),
        test_run=code_review_schemas.TestRun(
            status="passed", passed=True, exit_code=0, output="OK"
        ),
        applied_code="def safe(): pass",
    )
    rendered = render_outcome(report)
    assert "Score: 5/10" in rendered
    assert "[CRITICAL] Line 3: Null dereference" in rendered
    assert "Tests: PASSED (1 test cases)" in rendered
    assert "Applied Refactored Code:" in rendered

    # When refactor was only suggested (not applied)
    report_not_applied = code_review_schemas.CodeReviewReport(
        review=code_review_schemas.CodeReview(
            summary="Suggestions", score=7, refactored_code="def opt(): pass"
        ),
        tests=None,
        test_run=None,
        applied_code=None,
    )
    rendered_not_applied = render_outcome(report_not_applied)
    assert "Suggested (not applied) Refactored Code:" in rendered_not_applied

    # Specialist and default graph construction
    assert CODE_REVIEW_SPECIALIST.name == "code_review"
    assert callable(CODE_REVIEW_SPECIALIST.invoke)
    assert callable(CODE_REVIEW_SPECIALIST.stream)
    default_graph = _default_code_review_graph()

    assert default_graph is not None

    # run_code_review with transient error
    import httpx

    class FailingGraph:
        def invoke(self, *args: Any, **kwargs: Any) -> Any:
            raise httpx.ConnectError("Service offline")

    failed_result = run_code_review(FailingGraph(), "code")  # type: ignore[arg-type]
    assert failed_result.status == "failed"
    assert "Service offline" in failed_result.reason
