"""CLI entry point for the P3 Code Review & Test Generation agent with Human-In-The-Loop (HITL)."""

import contextlib
import io
import sys
from pathlib import Path

from dotenv import load_dotenv
from langgraph.types import Command

from data.sqlite_db_data import get_sqlite_checkpointer
from graphs.code_review_parentgraph import build_code_review_graph
from output_schemas.code_review_output_schema import (
    ReviewResult,
    TestExecutionResult,
    TestSuite,
)
from utils.session_util import resolve_session

load_dotenv()

if hasattr(sys.stdout, "reconfigure"):
    with contextlib.suppress(AttributeError, io.UnsupportedOperation):
        sys.stdout.reconfigure(encoding="utf-8")

# Demo snippet used when no file path is provided via CLI
_SAMPLE_CODE = """
def calculate_discount(price: float, discount_percent: float) -> float:
    if discount_percent > 100:
        return 0.0
    discount_amount = price * (discount_percent / 100)
    return price - discount_amount
""".strip()


def _print_review_report(review: ReviewResult) -> None:
    """Format and print structured review findings."""
    print("\n" + "=" * 60)
    print(f"📋 CODE REVIEW REPORT  (Quality Score: {review.score}/10)")
    print("=" * 60)
    print(f"\nSummary:\n{review.summary}\n")

    if review.issues:
        print("Identified Issues:")
        for i, issue in enumerate(review.issues, 1):
            line_str = (
                f" [Line {issue.line_number}]" if issue.line_number is not None else ""
            )
            print(f"  {i}. [{issue.severity.upper()}]{line_str} ({issue.category})")
            print(f"     Description: {issue.description}")
            print(f"     Suggestion:  {issue.suggestion}\n")
    else:
        print("No critical issues found.")

    if review.refactored_code:
        print("Suggested Refactoring:\n")
        print(review.refactored_code)
        print()


def _print_test_report(tests: TestSuite, execution: TestExecutionResult | None) -> None:
    """Format and print generated test suite and execution status."""
    print("\n" + "=" * 60)
    print(f"🧪 GENERATED TEST SUITE  (Framework: {tests.framework})")
    print("=" * 60)
    print(f"Planned Test Cases ({len(tests.test_cases)}):")
    for tc in tests.test_cases:
        print(f"  - {tc.name} ({tc.target_function}): {tc.description}")

    print("\nTest Code:\n")
    print(tests.test_code)

    if execution:
        print("\n" + "-" * 60)
        status_icon = "✅" if execution.passed else "❌"
        print(
            f"{status_icon} Sandbox Execution Status: {execution.status.upper()} (Exit Code: {execution.exit_code})"
        )
        print("-" * 60)
        print(execution.output)

    print("=" * 60 + "\n")


def _print_applied_code_report(
    applied_code: str | None, refactor_approved: bool
) -> None:
    """Format and print the final applied code output."""
    print("\n" + "=" * 60)
    decision_text = (
        "APPROVED (Refactored Version)"
        if refactor_approved
        else "ORIGINAL (Refactor Rejected / Skipped)"
    )
    print(f"📦 FINAL APPLIED CODE  [{decision_text}]")
    print("=" * 60)
    if applied_code:
        print(applied_code)
    print("=" * 60 + "\n")


def run_code_review(
    code: str,
    language: str = "python",
    file_path: str | None = None,
    session_arg: str | None = None,
) -> None:
    """Execute the Code Review graph with live streaming and Human-In-The-Loop approval."""

    session = resolve_session(
        session_arg,
        default_thread_id="cli_review_session",
        agent_factory=lambda saver: build_code_review_graph(
            checkpointer=saver or get_sqlite_checkpointer()
        ),
        app_name="code_review",
        cli_command_hint="python src/apps/code_review_app.py [file] step[<index>]",
    )
    graph = session.agent
    config = session.config

    target_display = file_path if file_path else "<inline_code>"

    # Check if resuming an existing completed session without new code
    initial_state = graph.get_state(config)
    if initial_state.values.get("review") and not initial_state.next and not file_path:
        print(
            f"\n[Notice] Inspecting recorded review findings for thread: {session.thread_id}"
        )
        _print_review_report(initial_state.values["review"])
        if initial_state.values.get("tests"):
            _print_test_report(
                initial_state.values["tests"],
                initial_state.values.get("test_execution"),
            )
        _print_applied_code_report(
            initial_state.values.get("applied_code")
            or initial_state.values.get("code"),
            refactor_approved=bool(initial_state.values.get("applied_code")),
        )
        return

    print(f"\n🔍 Starting code review pipeline for: {target_display}")

    review: ReviewResult | None = None
    tests: TestSuite | None = None
    execution: TestExecutionResult | None = None

    # Step 1: Initial graph stream execution (if not already paused at interrupt)
    if not initial_state.next:
        for update in graph.stream(
            {
                "code": code,
                "language": language,
                "file_path": file_path,
            },
            config=config,
            stream_mode="updates",
        ):
            for node_name, delta in update.items():
                if not delta:
                    continue

                if node_name in ("reviewer", "review_code"):
                    if delta.get("error"):
                        print(f"\n❌ Review failed: {delta['error']}")
                        return
                    review = delta.get("review")
                    if review:
                        print(
                            f"  ✓ Review finished — Score: {review.score}/10 | Issues: {len(review.issues)}"
                        )

                elif node_name in ("test_generator", "generate_tests"):
                    if delta.get("error"):
                        print(f"\n❌ Test generation failed: {delta['error']}")
                        return
                    if delta.get("tests"):
                        tests = delta.get("tests")
                        print(
                            f"  ✓ Test generation finished — Test cases: {len(tests.test_cases)}"
                        )
                    if delta.get("test_execution"):
                        execution = delta.get("test_execution")
                        status_text = "PASSED" if execution.passed else "FAILED"
                        print(f"  ✓ Sandbox execution finished — Status: {status_text}")

                elif node_name == "execute_tests":
                    execution = delta.get("test_execution")
                    if execution:
                        status_text = "PASSED" if execution.passed else "FAILED"
                        print(f"  ✓ Sandbox execution finished — Status: {status_text}")

                elif node_name == "fix_tests":
                    if delta.get("error"):
                        print(f"\n❌ Test fixing failed: {delta['error']}")
                        return
                    retries = delta.get("test_retries", 1)
                    print(
                        f"  🔄 Self-correction triggered (Attempt {retries}): Refactored failing test suite."
                    )

    # Step 2: Human-In-The-Loop Check (Inspect if graph is paused on an interrupt)
    state_snapshot = graph.get_state(config)
    refactor_approved = False

    if state_snapshot.next:
        # Extract the exact payload sent by interrupt()
        interrupt_payload = state_snapshot.tasks[0].interrupts[0].value
        action_name = interrupt_payload.get("action_required", "Approval Required")
        summary_text = interrupt_payload.get("summary", "")
        refactored_code = interrupt_payload.get("refactored_code", "")

        print("\n" + "!" * 60)
        print(f"⏸️  HUMAN APPROVAL REQUIRED: {action_name.upper()}")
        print("!" * 60)
        if summary_text:
            print(f"\nReview Summary:\n{summary_text}")
        if refactored_code:
            print(f"\nSuggested Refactored Code:\n{refactored_code}\n")
        print("-" * 60)

        # Interactive human prompt
        user_input = (
            input("\nDo you want to approve and apply this refactored code? [y/N]: ")
            .strip()
            .lower()
        )
        decision = "approve" if user_input in ("y", "yes") else "reject"
        refactor_approved = decision == "approve"

        print(f"  ➡️ Resuming graph with decision: '{decision.upper()}' ...\n")

        # Step 3: Resume graph with Command(resume=decision)
        for update in graph.stream(
            Command(resume=decision),
            config=config,
            stream_mode="updates",
        ):
            for node_name, delta in update.items():
                if node_name == "apply_refactor":
                    print("  ✓ Refactored code successfully applied to final state.")

    # Step 4: Final State Inspection & Presentation
    final_state = graph.get_state(config).values
    final_applied_code = final_state.get("applied_code") or code
    final_review = final_state.get("review") or review
    final_tests = final_state.get("tests") or tests
    final_execution = final_state.get("test_execution") or execution

    if final_review:
        _print_review_report(final_review)
    if final_tests:
        _print_test_report(final_tests, final_execution)

    _print_applied_code_report(final_applied_code, refactor_approved)


def main() -> None:
    """CLI handler."""
    args = sys.argv[1:]
    if args and args[0].lower() in {"list", "history"}:
        resolve_session(
            "list", default_thread_id="cli_review_session", app_name="code_review"
        )
        return

    session_arg = None
    target_path = None
    for arg in args:
        if arg.lower() in {
            "new",
            "secret",
            "resume",
            "default",
        } or arg.lower().startswith("step"):
            session_arg = arg
        elif not target_path and Path(arg).exists():
            target_path = Path(arg)
        elif not session_arg:
            session_arg = arg

    if target_path:
        code = target_path.read_text(encoding="utf-8")
        run_code_review(
            code=code,
            language="python",
            file_path=str(target_path),
            session_arg=session_arg,
        )
    else:
        # Check if user passed a step/resume arg without a file to inspect an existing session
        if session_arg and session_arg.lower() not in {"new", "secret"}:
            run_code_review(
                code="", language="python", file_path=None, session_arg=session_arg
            )
        else:
            print("No file argument provided. Running demo sample...")
            run_code_review(
                code=_SAMPLE_CODE,
                language="python",
                file_path="demo_calc.py",
                session_arg=session_arg,
            )


if __name__ == "__main__":
    main()
