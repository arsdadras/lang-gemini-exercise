"""P5 domain workflow & specialist: ``PersonalContextWorkflow``, ``run_personal_context``, and ``PERSONAL_CONTEXT_SPECIALIST``."""

from __future__ import annotations

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

    @classmethod
    def from_graph(
        cls,
        graph: PersonalContextGraph | CompiledStateGraph | Any,
    ) -> PersonalContextWorkflow:
        return cls(graph=graph)

    @classmethod
    def from_store(
        cls,
        store: BaseStore | Any,
    ) -> PersonalContextWorkflow:
        return cls(graph=build_personal_context_graph(store=store), store=store)

    def render(self, report: PersonalContextReport) -> str:
        return render_personal_context(report)


def run_personal_context(
    graph: PersonalContextGraph | CompiledStateGraph | Any,
    user_id: str,
) -> SpecialistResult[PersonalContextReport]:
    """Load ``user_id``'s stored context using the pre-composed personal context graph."""
    return PersonalContextWorkflow(graph=graph).invoke(user_id)["result"]


def make_personal_context_specialist(
    store: BaseStore | Any = None,
    *,
    graph: PersonalContextGraph | CompiledStateGraph | Any = None,
) -> PersonalContextWorkflow:
    """Create a Personal Context Workflow bound to a store, graph, or lazy default."""
    if graph is not None:
        return PersonalContextWorkflow.from_graph(graph)
    if store is not None:
        return PersonalContextWorkflow.from_store(store)
    return PersonalContextWorkflow()


PERSONAL_CONTEXT_SPECIALIST = make_personal_context_specialist()
