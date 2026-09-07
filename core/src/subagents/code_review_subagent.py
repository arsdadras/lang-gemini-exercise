"""Code Review Subagent — wraps the compiled P3 Code Review pipeline for delegation from DeepAgents multi-agent coordinators."""

import uuid
from typing import Any

from deepagents import CompiledSubAgent
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable, RunnableLambda
from utils.get_text_util import get_text

DEFAULT_CODE_REVIEW_NAME = "code_review_subagent"
DEFAULT_CODE_REVIEW_DESCRIPTION = (
    "Analyzes and reviews source code, identifies bugs, security vulnerabilities, "
    "and performance flaws, generates and executes pytest test suites in an isolated "
    "sandbox, and outputs refactored code."
)


def make_code_review_subagent(
    graph: Runnable | None = None,
    *,
    name: str = DEFAULT_CODE_REVIEW_NAME,
    description: str = DEFAULT_CODE_REVIEW_DESCRIPTION,
) -> CompiledSubAgent:
    """Factory creating a coordinator-compatible Code Review subagent via Dependency Injection.

    Args:
        graph: Pre-compiled Code Review StateGraph runnable (defaults to build_code_review_graph with sqlite checkpointer).
        name: Subagent tool name exposed to the coordinator LLM.
        description: Delegation instructions helping the coordinator route code review tasks.

    Returns:
        CompiledSubAgent TypedDict ready for registration with create_deep_agent(subagents=[...]).
    """
    if graph is None:
        from data.sqlite_db_data import get_sqlite_checkpointer
        from graphs.code_review_parentgraph import build_code_review_graph

        graph = build_code_review_graph(checkpointer=get_sqlite_checkpointer())

    def _run_code_review_subagent(state: dict[str, Any]) -> dict[str, Any]:
        """Adapter closure: invokes the injected graph and formats structured code review deliverables."""
        input_text = get_text(state["messages"][-1])
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # 1. Invoke pipeline of 3-subgraph
        result = graph.invoke(
            {
                "code": input_text,
                "language": "python",
                "file_path": None,
            },
            config=config,
        )

        # 2. Format structured output for Coordinator
        parts: list[str] = []
        review = result.get("review")
        if review:
            parts.append(f"### Code Review Summary (Score: {review.score}/10)")
            parts.append(review.summary)
            if review.issues:
                parts.append("\n**Key Issues Found:**")
                for issue in review.issues:
                    loc = f"Line {issue.line_number}: " if issue.line_number is not None else ""
                    parts.append(f"- [{issue.severity.upper()}] {loc}{issue.description}")

        tests = result.get("tests")
        execution = result.get("test_execution")
        if tests:
            status_str = "PASSED" if (execution and execution.passed) else "FAILED / PENDING"
            parts.append(f"\n### Test Suite Status: {status_str} ({len(tests.test_cases)} test cases)")

        refactored_code = result.get("applied_code") or (review.refactored_code if review else None)
        if refactored_code:
            parts.append(f"\n### Suggested Refactored Code:\n```python\n{refactored_code}\n```")

        output_content = "\n".join(parts) if parts else "Code review completed with no output."
        return {
            "messages": [AIMessage(content=output_content)],
            "thread_id": thread_id,
        }

    return {
        "name": name,
        "description": description,
        "runnable": RunnableLambda(_run_code_review_subagent),
    }


# Backward-compatible default instance
code_review_subagent: CompiledSubAgent = make_code_review_subagent()
