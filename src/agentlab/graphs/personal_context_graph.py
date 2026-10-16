"""Graph assembly for the P5 personal context workflow: load_context -> pack_result -> END."""

from typing import Any, NewType

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.base import BaseStore

PersonalContextGraph = NewType("PersonalContextGraph", CompiledStateGraph)

from agentlab.configs.personal_assistant_config import ASSISTANT_STORE_DB_PATH
from agentlab.data.sqlite_db_data import get_sqlite_store
from agentlab.schemas.input.personal_context_input_schema import PersonalContextInput
from agentlab.schemas.output.personal_context_output_schema import (
    PersonalContextReport,
)
from agentlab.schemas.state.personal_context_state import PersonalContextState
from agentlab.tools.user_context_tool import read_user_context
from agentlab.workflows.specialist_workflow import ResultNode, SpecialistSpec

DEFAULT_PERSONAL_CONTEXT_DESCRIPTION = (
    "Reads a user's long-term memory profile, facts, preferences, and active skills "
    "with secret redaction."
)

PERSONAL_CONTEXT_SPEC = SpecialistSpec[PersonalContextInput, PersonalContextReport](
    name="personal_context",
    description=DEFAULT_PERSONAL_CONTEXT_DESCRIPTION,
    input_schema=PersonalContextInput,
    report_schema=PersonalContextReport,
)


def _default_personal_context_store() -> BaseStore:
    return get_sqlite_store(ASSISTANT_STORE_DB_PATH)


def build_personal_context_graph(
    store: BaseStore | Any = None,
    *,
    checkpointer: BaseCheckpointSaver | None = None,
) -> PersonalContextGraph:
    """Build and compile the unified Personal Context graph ending in ``pack_result``."""
    resolved_store = store if store is not None else _default_personal_context_store()

    def _load_context_step(state: PersonalContextState) -> dict[str, Any]:
        res = read_user_context(resolved_store, state["user_id"])
        return {
            "report": res.output,
            "problems": [res.reason] if res.reason else [],
            "provenance": res.provenance,
        }

    graph = StateGraph(PersonalContextState)
    graph.add_node("load_context", _load_context_step)
    graph.add_node("pack_result", ResultNode(PERSONAL_CONTEXT_SPEC))
    graph.add_edge(START, "load_context")
    graph.add_edge("load_context", "pack_result")
    graph.add_edge("pack_result", END)

    compiled = graph.compile(checkpointer=checkpointer)
    return PersonalContextGraph(compiled)
