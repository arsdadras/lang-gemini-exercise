"""CLI entry point for the P3 Code Review & Test Generation agent."""

import sys
from pathlib import Path
from dotenv import load_dotenv

from graphs.code_review import build_code_review_graph
from output_schemas.code_review import ReviewResult, TestSuite, TestExecutionResult

load_dotenv()

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
    print(f"📋 CODE REVIEW REPORT  (Score: {review.score}/10)")
    print("=" * 60)
    print(f"\nSummary:\n{review.summary}\n")

    if review.issues:
        print("Identified Issues:")
        for i, issue in enumerate(review.issues, 1):
            line_str = f" [Line {issue.line_number}]" if issue.line_number is not None else ""
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
        print(f"{status_icon} Sandbox Execution Status: {execution.status.upper()} (Exit Code: {execution.exit_code})")
        print("-" * 60)
        print(execution.output)

    print("=" * 60 + "\n")


def run_code_review(
    code: str,
    language: str = "python",
    file_path: str | None = None,
) -> None:
    """Execute the Code Review graph with live streaming node updates."""
    graph = build_code_review_graph()
    config = {"configurable": {"thread_id": "cli_review_session"}}

    target_display = file_path if file_path else "<inline_code>"
    print(f"\n🔍 Starting code review pipeline for: {target_display}")

    review: ReviewResult | None = None
    tests: TestSuite | None = None
    execution: TestExecutionResult | None = None

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

            if node_name == "review_code":
                if delta.get("error"):
                    print(f"\n❌ Review failed: {delta['error']}")
                    return
                review = delta.get("review")
                if review:
                    print(f"  ✓ Review finished — Score: {review.score}/10 | Issues: {len(review.issues)}")

            elif node_name == "generate_tests":
                if delta.get("error"):
                    print(f"\n❌ Test generation failed: {delta['error']}")
                    return
                tests = delta.get("tests")
                if tests:
                    print(f"  ✓ Test generation finished — Test cases: {len(tests.test_cases)}")

            elif node_name == "execute_tests":
                execution = delta.get("test_execution")
                if execution:
                    status_text = "PASSED" if execution.passed else "FAILED"
                    print(f"  ✓ Sandbox execution finished — Status: {status_text}")

            elif node_name == "fix_tests":
                if delta.get("error"):
                    print(f"\n❌ Test fixing failed: {delta['error']}")
                    return
                tests = delta.get("tests")
                retries = delta.get("test_retries", 1)
                print(f"  🔄 Self-correction triggered (Attempt {retries}): Refactored failing test suite.")


    # Print final structured reports
    if review:
        _print_review_report(review)
    if tests:
        _print_test_report(tests, execution)


def main() -> None:
    """CLI handler."""
    if len(sys.argv) > 1:
        target_file = Path(sys.argv[1])
        if not target_file.exists():
            print(f"Error: Target file does not exist: {target_file}")
            sys.exit(1)
        code = target_file.read_text(encoding="utf-8")
        run_code_review(code=code, language="python", file_path=str(target_file))
    else:
        print("No file argument provided. Running demo sample...")
        run_code_review(code=_SAMPLE_CODE, language="python", file_path="demo_calc.py")


if __name__ == "__main__":
    main()
