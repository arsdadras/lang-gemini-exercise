"""Graph assembly for the P5 skill designer: draft -> check -> publish (after human approval)."""

from langchain_core.runnables import Runnable
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.base import BaseStore

from agentlab.middlewares.security_guard_middleware import (
    SecurityGuard,
    make_security_guard,
)
from agentlab.nodes.skill_designer_node import (
    make_check_node,
    make_draft_node,
    make_publish_node,
    route_after_check,
)
from agentlab.prompts.middlewares_prompt import SKILL_PUBLISH_POLICY
from agentlab.schemas.state.skill_designer_state import SkillDesignerState


def make_skill_designer_graph(
    store: BaseStore,
    *,
    checkpointer: BaseCheckpointSaver | None = None,
    model: Runnable | None = None,
    guard: SecurityGuard | None = None,
) -> CompiledStateGraph:
    """Compile the skill designer, the only writer to the shared skill library.

    Args:
        store: The long-term store holding published skills.
        checkpointer: Keeps the run while it waits for approval; defaults to in-memory.
        model: Structured-output model for the draft; defaults to the ``medium`` tier.
        guard: Security guard for drafts; defaults to the skill publishing policy.
    """
    graph = StateGraph(SkillDesignerState)
    graph.add_node("draft", make_draft_node(model))
    graph.add_node("check", make_check_node(guard if guard is not None else make_security_guard(SKILL_PUBLISH_POLICY)))
    graph.add_node("publish", make_publish_node())
    graph.add_edge(START, "draft")
    graph.add_edge("draft", "check")
    graph.add_conditional_edges("check", route_after_check, {"publish": "publish", "__end__": END})
    graph.add_edge("publish", END)
    return graph.compile(checkpointer=checkpointer if checkpointer is not None else InMemorySaver(), store=store)
