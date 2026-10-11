"""CLI for the P3 code review pipeline: ``lab-code-review [file] [session-mode]``.

Streams review, test generation, and sandbox results, pauses at the refactor
approval gate (``interrupt()``), and resumes with ``Command(resume=...)``.
Without a file it reviews a small demo snippet; with only a session mode it
inspects (or resumes) that recorded session.
"""

import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.types import Command

from agentlab.configs.paths_config import checkpoint_db_path
from agentlab.data.sqlite_db_data import get_sqlite_checkpointer
from agentlab.graphs.code_review_parentgraph import (
    CodeReviewGraph,
    build_code_review_graph,
)
from agentlab.schemas.output.code_review_output_schema import (
    CodeReview,
    TestRun,
    TestSuite,
)
from agentlab.utils.console_util import configure_utf8_stdout
from agentlab.utils.session_util import resolve_session

DEFAULT_THREAD_ID = "cli_review_session"
_RULE = "=" * 60
_SAMPLE_CODE = """
def calculate_discount(price: float, discount_percent: float) -> float:
    if discount_percent > 100:
        return 0.0
    discount_amount = price * (discount_percent / 100)
    return price - discount_amount
""".strip()


def _make_graph(checkpointer: BaseCheckpointSaver | None) -> CodeReviewGraph:
    return build_code_review_graph(
        checkpointer=checkpointer
        if checkpointer is not None
        else get_sqlite_checkpointer(checkpoint_db_path("code_review")),
    )


def _print_review(review: CodeReview) -> None:
    print(f"\n{_RULE}\nCODE REVIEW REPORT (quality score: {review.score}/10)\n{_RULE}")
    print(f"\nSummary:\n{review.summary}\n")
    if not review.issues:
        print("No issues found.")
    for number, issue in enumerate(review.issues, 1):
        line = f" [line {issue.line_number}]" if issue.line_number is not None else ""
        print(f"  {number}. [{issue.severity.upper()}]{line} ({issue.category})")
        print(f"     Description: {issue.description}")
        print(f"     Suggestion:  {issue.suggestion}\n")
    if review.refactored_code:
        print(f"Suggested refactoring:\n\n{review.refactored_code}\n")


def _print_tests(tests: TestSuite, execution: TestRun | None) -> None:
    print(f"\n{_RULE}\nGENERATED TEST SUITE (framework: {tests.framework})\n{_RULE}")
    print(f"Planned test cases ({len(tests.test_cases)}):")
    for case in tests.test_cases:
        print(f"  - {case.name} ({case.target_function}): {case.description}")
    print(f"\nTest code:\n\n{tests.test_code}")
    if execution:
        print(f"\n{'-' * 60}")
        print(
            f"Sandbox run: {execution.status.upper()} (exit code {execution.exit_code})",
        )
        print(f"{'-' * 60}\n{execution.output}")


def _stream_pipeline(
    graph: CodeReviewGraph,
    inputs: dict[str, Any],
    config: RunnableConfig,
) -> bool:
    """Stream node updates; return ``False`` if a stage reported a fatal error."""
    for update in graph.stream(inputs, config=config, stream_mode="updates"):
        for node_name, delta in update.items():
            if not delta:
                continue
            if delta.get("error"):
                print(f"\n[Failed] {node_name}: {delta['error']}")
                return False
            if review := delta.get("review"):
                print(
                    f"  [ok] Review finished: score {review.score}/10, {len(review.issues)} issue(s)",
                )
            if tests := delta.get("tests"):
                print(
                    f"  [ok] Test suite generated: {len(tests.test_cases)} test case(s)",
                )
            if execution := delta.get("test_run"):
                print(
                    f"  [ok] Sandbox run: {'PASSED' if execution.passed else 'FAILED'}",
                )
            if "test_retries" in delta:
                print(f"  [retry] Self-correction attempt {delta['test_retries']}")
    return True


def _run_refactor_gate(graph: CodeReviewGraph, config: RunnableConfig) -> bool:
    """If the graph is paused at the refactor gate, ask the human and resume."""
    snapshot = graph.get_state(config)
    if not snapshot.next:
        return False

    payload = snapshot.tasks[0].interrupts[0].value
    print(
        f"\n{'!' * 60}\nHUMAN APPROVAL REQUIRED: {payload.get('action_required', 'approval').upper()}",
    )
    print("!" * 60)
    if payload.get("summary"):
        print(f"\nReview summary:\n{payload['summary']}")
    if payload.get("refactored_code"):
        print(f"\nSuggested refactored code:\n{payload['refactored_code']}\n")

    answer = input("\nApply this refactored code? [y/N]: ").strip().lower()
    decision = "approve" if answer in {"y", "yes"} else "reject"
    print(f"  Resuming with decision: {decision.upper()}")
    for _ in graph.stream(
        Command(resume=decision),
        config=config,
        stream_mode="updates",
    ):
        pass
    return decision == "approve"


def run_code_review(
    graph: CodeReviewGraph,
    config: RunnableConfig,
    *,
    code: str | None,
    file_path: str | None,
) -> None:
    """Review ``code`` (or, when ``None``, inspect/resume the session) and print the results."""
    if code is not None and not graph.get_state(config).next:
        print(f"\nStarting code review pipeline for: {file_path}")
        inputs = {"code": code, "language": "python", "file_path": file_path}
        if not _stream_pipeline(graph, inputs, config):
            return

    approved = _run_refactor_gate(graph, config)
    final = graph.get_state(config).values
    if not final.get("review"):
        print("[Notice] This session has no recorded review.")
        return

    _print_review(final["review"])
    if final.get("tests"):
        _print_tests(final["tests"], final.get("test_run"))
    applied = final.get("applied_code")
    label = (
        "APPROVED (refactored version)"
        if approved or applied
        else "ORIGINAL (refactor rejected or skipped)"
    )
    print(
        f"\n{_RULE}\nFINAL CODE [{label}]\n{_RULE}\n{applied or final.get('code', '')}\n{_RULE}",
    )


def main() -> None:
    """Parse ``[file] [session-mode]`` in any order and run the review."""
    load_dotenv()
    configure_utf8_stdout()

    target: Path | None = None
    session_arg: str | None = None
    for arg in sys.argv[1:]:
        if target is None and Path(arg).is_file():
            target = Path(arg)
        elif session_arg is None:
            session_arg = arg

    session = resolve_session(
        session_arg,
        default_thread_id=DEFAULT_THREAD_ID,
        agent_factory=_make_graph,
        app_name="code_review",
        cli_command_hint="uv run lab-code-review [file] step[<index>]",
    )

    if target is not None:
        run_code_review(
            session.agent,
            session.config,
            code=target.read_text(encoding="utf-8"),
            file_path=str(target),
        )
    elif session_arg and session_arg.lower() not in {"new", "secret"}:
        run_code_review(session.agent, session.config, code=None, file_path=None)
    else:
        print("No file argument provided. Reviewing the demo snippet.")
        run_code_review(
            session.agent,
            session.config,
            code=_SAMPLE_CODE,
            file_path="demo_calc.py",
        )


if __name__ == "__main__":
    main()
