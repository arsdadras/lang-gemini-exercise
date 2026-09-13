"""Code review subagent: exposes the compiled P3 review pipeline to DeepAgents coordinators."""

import uuid
from typing import Any

from deepagents import CompiledSubAgent
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable, RunnableLambda

from agentlab.data.sqlite_db_data import get_sqlite_checkpointer
from agentlab.graphs.code_review_parentgraph import build_code_review_graph
from agentlab.utils.get_text_util import get_text

DEFAULT_CODE_REVIEW_NAME = "code_review_subagent"
DEFAULT_CODE_REVIEW_DESCRIPTION = (
    "Analyzes and reviews source code, identifies bugs, security vulnerabilities, "
    "and performance flaws, generates and executes pytest test suites in an isolated "
    "sandbox, and outputs refactored code."
)


def _format_report(result: dict[str, Any]) -> str:
    """Render the pipeline's final state as a report for the coordinator."""
    parts: list[str] = []
    review = result.get("review")
    if review:
        parts.append(f"### Code Review Summary (Score: {review.score}/10)")
        parts.append(review.summary)
        if review.issues:
            parts.append("\n**Key Issues Found:**")
            for issue in review.issues:
                location = f"Line {issue.line_number}: " if issue.line_number is not None else ""
                parts.append(f"- [{issue.severity.upper()}] {location}{issue.description}")

    tests = result.get("tests")
    if tests:
        execution = result.get("test_execution")
        status = "PASSED" if execution and execution.passed else "FAILED / PENDING"
        parts.append(f"\n### Test Suite Status: {status} ({len(tests.test_cases)} test cases)")

    refactored = result.get("applied_code") or (review.refactored_code if review else None)
    if refactored:
        parts.append(f"\n### Suggested Refactored Code:\n```python\n{refactored}\n```")

    return "\n".join(parts) if parts else "Code review completed with no output."


def make_code_review_subagent(
    graph: Runnable | None = None,
    *,
    name: str = DEFAULT_CODE_REVIEW_NAME,
    description: str = DEFAULT_CODE_REVIEW_DESCRIPTION,
) -> CompiledSubAgent:
    """Wrap the compiled review pipeline as a ``CompiledSubAgent``.

    Defaults to ``build_code_review_graph`` on the shared SQLite checkpointer.
    The last coordinator message is reviewed as Python source; each delegation
    runs on a fresh thread.
    """
    review_graph = (
        graph if graph is not None else build_code_review_graph(checkpointer=get_sqlite_checkpointer())
    )

    def run(state: dict[str, Any]) -> dict[str, Any]:
        config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        result = review_graph.invoke(
            {"code": get_text(state["messages"][-1]), "language": "python", "file_path": None},
            config=config,
        )
        return {"messages": [AIMessage(content=_format_report(result))]}

    return {"name": name, "description": description, "runnable": RunnableLambda(run)}
