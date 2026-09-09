"""RAG subagent — wraps the compiled P2 RAG graph for delegation from DeepAgents multi-agent coordinators."""

import uuid
from typing import Any

from deepagents import CompiledSubAgent
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable, RunnableLambda

from utils.get_text_util import get_text

DEFAULT_RAG_SUBAGENT_NAME = "rag_subagent"
DEFAULT_RAG_SUBAGENT_DESCRIPTION = (
    "Answers questions using the indexed document corpus, falling back "
    "to a live web search when nothing relevant is found locally."
)


def make_rag_subagent(
    graph: Runnable | None = None,
    *,
    name: str = DEFAULT_RAG_SUBAGENT_NAME,
    description: str = DEFAULT_RAG_SUBAGENT_DESCRIPTION,
) -> CompiledSubAgent:
    """Factory creating a coordinator-compatible RAG subagent via Dependency Injection.

    Args:
        graph: Pre-compiled RAG StateGraph runnable (defaults to build_rag_graph()).
        name: Subagent tool name exposed to the coordinator LLM.
        description: Delegation instructions helping the coordinator route RAG queries.

    Returns:
        CompiledSubAgent TypedDict ready for registration with create_deep_agent(subagents=[...]).
    """
    if graph is None:
        from graphs.rag_graph import build_rag_graph

        graph = build_rag_graph()

    def _run_rag_subagent(state: dict[str, Any]) -> dict[str, Any]:
        """Adapter closure: invokes the injected RAG graph and returns formatted AIMessage."""
        question = get_text(state["messages"][-1])
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        result = graph.invoke({"question": question}, config=config)
        return {
            "messages": [AIMessage(content=result["generation"])],
            "thread_id": thread_id,
        }

    return {
        "name": name,
        "description": description,
        "runnable": RunnableLambda(_run_rag_subagent),
    }


# Backward-compatible default instance
rag_subagent: CompiledSubAgent = make_rag_subagent()
