"""RAG subagent — wraps the compiled P2 RAG graph for delegation from other
DeepAgents systems."""

import uuid

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from graphs.rag import build_rag_graph

_rag_graph = build_rag_graph()

def _run_rag_subagent(state: dict) -> dict:
    question = state["messages"][-1].content
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    result = _rag_graph.invoke({"question": question}, config=config)
    return {"messages": [AIMessage(content=result["generation"])]}


rag_subagent = {
    "name": "rag_subagent",
    "description": (
        """Answers questions using the indexed document corpus, 
        falling back to a live web search when nothing relevant is found locally."""
    ),
    "runnable": RunnableLambda(_run_rag_subagent)
}