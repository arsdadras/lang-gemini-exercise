"""P3 domain workflow & specialist: ``CodeReviewWorkflow``, ``run_code_review``, and ``CODE_REVIEW_SPECIALIST``."""

from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agentlab.configs.paths_config import DELEGATIONS_APP, checkpoint_db_path
from agentlab.data.sqlite_db_data import get_sqlite_checkpointer
from agentlab.graphs.code_review_parentgraph import (
    CodeReviewGraph,
    build_code_review_graph,
)
from agentlab.schemas.input.code_review_input_schema import CodeReviewInput
from agentlab.schemas.output.code_review_output_schema import CodeReviewReport
from agentlab.schemas.output.specialist_output_schema import SpecialistResult
from agentlab.utils.subagent_util import new_delegation_config, pending_approvals
from agentlab.workflows.specialist_workflow import (
    SpecialistSpec,
    Workflow,
    WorkflowOverallState,
)

DEFAULT_CODE_REVIEW_DESCRIPTION = (
    "Analyzes and reviews source code, identifies bugs, security vulnerabilities, "
    "and performance flaws, generates and executes pytest test suites in an isolated "
    "sandbox, and outputs refactored code."
)


def _default_code_review_graph() -> CompiledStateGraph:
    return build_code_review_graph(
        checkpointer=get_sqlite_checkpointer(checkpoint_db_path(DELEGATIONS_APP))
    )


def render_outcome(outcome: CodeReviewReport) -> str:
    """The pipeline's findings as a short report for a model caller."""
    review = outcome.review
    parts = [f"### Code Review Summary (Score: {review.score}/10)", review.summary]
    if review.issues:
        parts.append("\n**Key Issues Found:**")
        for issue in review.issues:
            location = (
                f"Line {issue.line_number}: " if issue.line_number is not None else ""
            )
            parts.append(f"- [{issue.severity.upper()}] {location}{issue.description}")
    if outcome.tests:
        execution = outcome.test_run
        result = (
            "PASSED"
            if execution and execution.passed
            else (execution.status.upper() if execution else "NOT RUN")
        )
        parts.append(
            f"\n### Tests: {result} ({len(outcome.tests.test_cases)} test cases)",
        )
    refactored = outcome.applied_code or review.refactored_code
    if refactored:
        label = "Applied" if outcome.applied_code else "Suggested (not applied)"
        parts.append(f"\n### {label} Refactored Code:\n```python\n{refactored}\n```")
    return "\n".join(parts)


class CodeReviewWorkflowState(WorkflowOverallState[CodeReviewReport]):
    """Overall state for the Code Review workflow graph."""

    code: str
    language: str


class CodeReviewWorkflow(Workflow[CodeReviewInput, CodeReviewReport]):
    """Active Rung-2 Code Review domain workflow wrapping ``CodeReviewGraph``."""

    spec = SpecialistSpec(
        name="code_review",
        description=DEFAULT_CODE_REVIEW_DESCRIPTION,
        input_schema=CodeReviewInput,
        report_schema=CodeReviewReport,
    )

    def __init__(
        self,
        graph: CodeReviewGraph | CompiledStateGraph | Any = None,
    ) -> None:
        self._graph = graph

    @property
    def review_graph(self) -> CompiledStateGraph:
        if self._graph is None:
            self._graph = _default_code_review_graph()
        return self._graph

    def render(self, report: CodeReviewReport) -> str:
        return render_outcome(report)

    def build_graph(self) -> CompiledStateGraph:
        def _review_step(state: CodeReviewWorkflowState) -> dict[str, Any]:
            sub_state = self.review_graph.invoke(
                {
                    "code": state["code"],
                    "language": state.get("language", "python"),
                    "file_path": None,
                },
                config=new_delegation_config(),
            )
            review = sub_state.get("review")
            if review is None:
                err = sub_state.get("error") or "No review was produced."
                return {"report": None, "problems": [err]}

            outcome = CodeReviewReport(
                review=review,
                tests=sub_state.get("tests"),
                test_run=sub_state.get("test_run"),
                applied_code=sub_state.get("applied_code"),
            )
            problems = []
            if waiting := pending_approvals(sub_state):
                problems.append(
                    f"The suggested refactor waits for approval ({waiting}); it wasn't applied."
                )
            elif outcome.test_run is None or outcome.test_run.status in (
                "error",
                "timed_out",
            ):
                problems.append("The generated tests didn't run to completion.")
            return {"report": outcome, "problems": problems}

        graph = StateGraph(CodeReviewWorkflowState)
        graph.add_node("review_step", _review_step)
        graph.add_node("pack_result", self.pack_node)
        graph.add_edge(START, "review_step")
        graph.add_edge("review_step", "pack_result")
        graph.add_edge("pack_result", END)
        return graph.compile()


def run_code_review(
    graph: CodeReviewGraph | CompiledStateGraph | Any,
    code: str,
    *,
    language: str = "python",
) -> SpecialistResult[CodeReviewReport]:
    """Review ``code`` with the P3 pipeline on a fresh thread, as a specialist envelope."""
    return CodeReviewWorkflow(graph).run(code=code, language=language)


def make_code_review_specialist(
    engine: CodeReviewGraph | CompiledStateGraph | Any = None,
) -> CodeReviewWorkflow:
    """Create a Code Review Workflow bound to an engine or lazy default."""
    return CodeReviewWorkflow(engine)


CODE_REVIEW_SPECIALIST = CodeReviewWorkflow()
code_review_workflow = CODE_REVIEW_SPECIALIST
