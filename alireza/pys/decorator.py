from typing import Any, Callable
from functools import wraps

from deepagents import create_deep_agent
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field


from agents import web_researcher_agent
from graphs import rag_graph, code_review_parentgraph
from models import llm_model


# ============================================================
# 1. MANIFEST
# ============================================================

class AgentManifest(BaseModel):
    name: str = Field(..., description="Unique slug for the agent")
    display_name: str
    description: str = Field(
        ...,
        description="Exposed to Supervisor LLM for delegation"
    )
    agent_type: str = "pure"
    model_tier: str = "medium"
    tools: list[str] = Field(default_factory=list)
    subagent_names: list[str] = Field(default_factory=list)


# ============================================================
# 2. COMPILED SUBAGENT
# ============================================================

def as_subagent(manifest: AgentManifest):

    def decorator(function: Callable[..., Any]):

        @wraps(function)
        def wrapper(state: dict[str, Any]) -> dict[str, Any]:

            result = function(state)

            return result

        return {
            "name": manifest.name,
            "description": manifest.description,
            "runnable": RunnableLambda(wrapper),
        }

    return decorator






researcher_manifest = AgentManifest(
    name="researcher",
    display_name="Researcher",
    description="Researches topics using web search and provides reliable findings.",
    agent_type="pure",
    model_tier="medium",
    tools=["tavily_search"],
)


@as_subagent(researcher_manifest)
def run_researcher(state: dict[str, Any]) -> dict[str, Any]:

    task = state["messages"][-1].content

    result = web_researcher_agent.invoke(
        {
            "messages": [
                HumanMessage(content=task)
            ]
        }
    )

    return {
        "messages": [
            result["messages"][-1]
        ]
    }




rag_manifest = AgentManifest(
    name="rag",
    display_name="RAG Agent",
    description="Answers questions using the knowledge base with retrieval and self-correction.",
    agent_type="pure",
    model_tier="medium",
    tools=[],
)


@as_subagent(rag_manifest)
def run_rag(state: dict[str, Any]) -> dict[str, Any]:

    task = state["messages"][-1].content

    result = rag_graph.invoke(
        {
            "question": task,
        }
    )

    return {
        "messages": [
            AIMessage(content=result["answer"])
        ]
    }



code_review_manifest = AgentManifest(
    name="code_reviewer",
    display_name="Code Reviewer",
    description="Reviews code, identifies problems, and suggests improvements.",
    agent_type="pure",
    model_tier="medium",
    tools=[],
)


@as_subagent(code_review_manifest)
def run_code_reviewer(state: dict[str, Any]) -> dict[str, Any]:

    task = state["messages"][-1].content

    result = code_review_parentgraph.invoke(
        {
            "request": task,
        }
    )

    return {
        "messages": [
            AIMessage(content=result["final_review"])
        ]
    }




interpreter_manifest = AgentManifest(
    name="interpreter",
    display_name="Python Interpreter",
    description="Executes Python code, works with files, and generates artifacts.",
    agent_type="pure",
    model_tier="medium",
    tools=["python", "filesystem"],
)


@as_subagent(interpreter_manifest)
def run_interpreter(state: dict[str, Any]) -> dict[str, Any]:

    task = state["messages"][-1].content

    result = interpreter_agent.invoke(
        {
            "messages": [
                HumanMessage(content=task)
            ]
        }
    )

    return {
        "messages": [
            result["messages"][-1]
        ]
    }



personal_assistant_manifest = AgentManifest(
    name="personal_assistant",
    display_name="Personal Assistant",
    description="Helps the user with personal tasks, memory, and persistent information.",
    agent_type="pure",
    model_tier="medium",
    tools=[],
)


@as_subagent(personal_assistant_manifest)
def run_personal_assistant(state: dict[str, Any]) -> dict[str, Any]:

    task = state["messages"][-1].content

    result = personal_assistant_agent.invoke(
        {
            "messages": [
                HumanMessage(content=task)
            ]
        }
    )

    return {
        "messages": [
            result["messages"][-1]
        ]
    }



subagents = [
    run_researcher,
    run_rag,
    run_code_reviewer,
    run_interpreter,
    run_personal_assistant,
]


agent = create_deep_agent(
    model=llm_model(tier="medium"),
    subagents=subagents,
)