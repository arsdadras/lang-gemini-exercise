"""P5 domain workflow & specialist: ``PersonalContextWorkflow``, ``run_personal_context``, and ``PERSONAL_CONTEXT_SPECIALIST``."""

from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.base import BaseStore

from agentlab.configs.personal_assistant_config import ASSISTANT_STORE_DB_PATH
from agentlab.data.sqlite_db_data import get_sqlite_store
from agentlab.schemas.input.personal_context_input_schema import PersonalContextInput
from agentlab.schemas.output.personal_context_output_schema import (
    PersonalContextReport,
)
from agentlab.schemas.output.specialist_output_schema import SpecialistResult
from agentlab.tools.user_context_tool import (
    read_user_context,
    render_personal_context,
)
from agentlab.workflows.specialist_workflow import (
    SpecialistSpec,
    Workflow,
    WorkflowOverallState,
)

DEFAULT_PERSONAL_CONTEXT_DESCRIPTION = (
    "Reads a user's long-term memory profile, facts, preferences, and active skills "
    "with secret redaction."
)


def _default_personal_context_store() -> BaseStore:
    return get_sqlite_store(ASSISTANT_STORE_DB_PATH)


class PersonalContextWorkflowState(WorkflowOverallState[PersonalContextReport]):
    """Overall state for the Personal Context workflow graph."""

    user_id: str


class PersonalContextWorkflow(Workflow[PersonalContextInput, PersonalContextReport]):
    """Active Rung-2 Personal Context domain workflow wrapping user store."""

    spec = SpecialistSpec(
        name="personal_context",
        description=DEFAULT_PERSONAL_CONTEXT_DESCRIPTION,
        input_schema=PersonalContextInput,
        report_schema=PersonalContextReport,
    )

    def __init__(
        self,
        store: BaseStore | Any = None,
    ) -> None:
        self._store = store

    @property
    def store(self) -> BaseStore:
        if self._store is None:
            self._store = _default_personal_context_store()
        return self._store

    def render(self, report: PersonalContextReport) -> str:
        return render_personal_context(report)

    def build_graph(self) -> CompiledStateGraph:
        def _load_context_step(state: PersonalContextWorkflowState) -> dict[str, Any]:
            res = read_user_context(self.store, state["user_id"])
            return {
                "report": res.output,
                "problems": [res.reason] if res.reason else [],
                "provenance": res.provenance,
            }

        graph = StateGraph(PersonalContextWorkflowState)
        graph.add_node("load_context", _load_context_step)
        graph.add_node("pack_result", self.pack_node)
        graph.add_edge(START, "load_context")
        graph.add_edge("load_context", "pack_result")
        graph.add_edge("pack_result", END)
        return graph.compile()


def run_personal_context(
    store: BaseStore | Any,
    user_id: str,
) -> SpecialistResult[PersonalContextReport]:
    """Load ``user_id``'s stored context from ``store`` as a ``SpecialistResult[PersonalContextReport]``."""
    return PersonalContextWorkflow(store).run(user_id=user_id)


def make_personal_context_specialist(
    engine: BaseStore | Any = None,
) -> PersonalContextWorkflow:
    """Create a Personal Context Workflow bound to a store or lazy default."""
    return PersonalContextWorkflow(engine)


PERSONAL_CONTEXT_SPECIALIST = PersonalContextWorkflow()
personal_context_workflow = PERSONAL_CONTEXT_SPECIALIST
