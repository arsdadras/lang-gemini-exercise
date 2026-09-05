"""Code Review Subagent — wraps the compiled P3 Code Review pipeline for delegation from DeepAgents multi-agent
coordinators."""

import uuid

from data.sqlite_db_data import get_sqlite_checkpointer
from graphs.code_review_parentgraph import build_code_review_graph
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from utils.get_text_util import get_text

_code_review_graph = build_code_review_graph(checkpointer=get_sqlite_checkpointer())


def _run_code_review_subagent(state: dict) -> dict:
  """Adapter function: converts incoming message to CodeReviewState and returns formatted AIMessage."""
  input_text = get_text(state["messages"][-1])
  thread_id = str(uuid.uuid4())
  config = {"configurable": {"thread_id": thread_id}}

  # 1. Invoke pipeline of 3-subgraph
  result = _code_review_graph.invoke(
      {
          "code": input_text,
          "language": "python",
          "file_path": None,
      },
      config=config,
  )

  # 2. make the structured data to proper text for Coordinator
  parts = []
  review = result.get("review")
  if review:
    parts.append(f"### Code Review Summary (Score: {review.score}/10)")
    parts.append(review.summary)
    if review.issues:
      parts.append("\n**Key Issues Found:**")
      for issue in review.issues:
        loc = (
            f"Line {issue.line_number}: "
            if issue.line_number is not None
            else ""
        )
        parts.append(f"- [{issue.severity.upper()}] {loc}{issue.description}")

  tests = result.get("tests")
  execution = result.get("test_execution")
  if tests:
    status_str = (
        "PASSED" if (execution and execution.passed) else "FAILED / PENDING"
    )
    parts.append(
        f"\n### Test Suite Status: {status_str} ({len(tests.test_cases)} test"
        " cases)"
    )
  refactored_code = result.get("applied_code") or (
      review.refactored_code if review else None
  )
  if refactored_code:
      parts.append(
          f"\n### Suggested Refactored Code:\n```python\n{refactored_code}\n```"
      )

  output_content = (
      "\n".join(parts) if parts else "Code review completed with no output."
  )
  return {
      "messages": [AIMessage(content=output_content)],
      "thread_id": thread_id
  }


# DeepAgents SubAgent Schema
code_review_subagent = {
    "name": "code_review_subagent",
    "description": (
        "Analyzes and reviews source code, identifies bugs, security"
        " vulnerabilities, and performance flaws, generates and executes"
        " pytest test suites in an isolated sandbox, and outputs refactored"
        " code."
    ),
    "runnable": RunnableLambda(_run_code_review_subagent),
}
