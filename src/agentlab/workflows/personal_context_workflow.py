"""P5 domain workflow & specialist: ``PersonalContextWorkflow``, ``run_personal_context``, and ``PERSONAL_CONTEXT_SPECIALIST``."""

from typing import Any

from langgraph.graph.state import CompiledStateGraph
from langgraph.store.base import BaseStore

from agentlab.graphs.personal_context_graph import (
    DEFAULT_PERSONAL_CONTEXT_DESCRIPTION,
    PERSONAL_CONTEXT_SPEC,
    PersonalContextGraph,
    build_personal_context_graph,
)
from agentlab.schemas.input.personal_context_input_schema import PersonalContextInput
from agentlab.schemas.output.personal_context_output_schema import (
    PersonalContextReport,
)
from agentlab.schemas.output.specialist_output_schema import SpecialistResult
from agentlab.tools.user_context_tool import render_personal_context
from agentlab.workflows.specialist_workflow import Workflow

__all__ = [
    "DEFAULT_PERSONAL_CONTEXT_DESCRIPTION",
    "PERSONAL_CONTEXT_SPECIALIST",
    "PersonalContextWorkflow",
    "build_personal_context_graph",
    "make_personal_context_specialist",
    "personal_context_workflow",
    "render_personal_context",
    "run_personal_context",
]


class PersonalContextWorkflow(Workflow[PersonalContextInput, PersonalContextReport]):
    """Active Rung-2 Personal Context domain workflow wrapping ``PersonalContextGraph`` as a Runnable facade."""

    spec = PERSONAL_CONTEXT_SPEC

    def __init__(
        self,
        graph: PersonalContextGraph | CompiledStateGraph | Any | None = None,
        *,
        store: BaseStore | Any = None,
    ) -> None:
        super().__init__(graph)
        self._store = store

    @property
    def store(self) -> BaseStore | Any:
        return self._store

    def build_default_graph(self) -> CompiledStateGraph:
        return build_personal_context_graph(store=self._store)

    def render(self, report: PersonalContextReport) -> str:
        return render_personal_context(report)


def run_personal_context(
    store: BaseStore | Any,
    user_id: str,
) -> SpecialistResult[PersonalContextReport]:
    """Load ``user_id``'s stored context from ``store`` as a ``SpecialistResult[PersonalContextReport]``."""
    if getattr(store, "_is_personal_context_graph", False):
        workflow = PersonalContextWorkflow(graph=store)
    else:
        workflow = PersonalContextWorkflow(store=store)
    return workflow.invoke(user_id)["result"]


def make_personal_context_specialist(
    engine: BaseStore | Any = None,
) -> PersonalContextWorkflow:
    """Create a Personal Context Workflow bound to a store or lazy default."""
    if getattr(engine, "_is_personal_context_graph", False):
        return PersonalContextWorkflow(graph=engine)
    return PersonalContextWorkflow(store=engine)


PERSONAL_CONTEXT_SPECIALIST = PersonalContextWorkflow()
personal_context_workflow = PERSONAL_CONTEXT_SPECIALIST
