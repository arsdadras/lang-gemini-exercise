"""RAG subagent: exposes the compiled P2 RAG graph to DeepAgents coordinators."""

import uuid
from typing import Any

from deepagents import CompiledSubAgent
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable, RunnableLambda

from agentlab.graphs.rag_graph import build_rag_graph
from agentlab.utils.get_text_util import get_text

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
    """Wrap a compiled RAG graph (default: ``build_rag_graph()``) as a ``CompiledSubAgent``.

    The adapter translates the coordinator's ``messages`` into the graph's
    task-shaped input and back, so the graph's own state stays free of chat
    concerns. Each delegation is an independent query and gets a fresh thread.
    """
    rag_graph = graph if graph is not None else build_rag_graph()

    def run(state: dict[str, Any]) -> dict[str, Any]:
        question = get_text(state["messages"][-1])
        config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        result = rag_graph.invoke({"question": question}, config=config)
        return {"messages": [AIMessage(content=result["generation"])]}

    return {"name": name, "description": description, "runnable": RunnableLambda(run)}
