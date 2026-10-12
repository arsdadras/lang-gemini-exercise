"""Rung-3 macro-workflow (P5 + P1): personalized research brief (``personal_brief_workflow``)."""

import uuid

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.base import BaseStore

from agentlab.agents.researcher_agent import make_researcher_agent
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.schemas.output.research_output_schema import ResearchReport
from agentlab.tools.user_context_tool import (
    USER_CONTEXT_TOOL_NAME,
    make_user_context_tool,
)
from agentlab.utils.run_with_hitl_util import stream_with_hitl
from agentlab.utils.secret_redaction_util import personal_data_redaction
from agentlab.workflows.research_workflow import verify_research


def brief_request(topic: str) -> str:
    """Format a user's topic into a personalized research brief request."""
    return (
        f"Research this for me: {topic}\n\n"
        f"First call {USER_CONTEXT_TOOL_NAME} and tailor the report to my stored constraints, "
        "preferences, and goals; say in the summary which of them shaped it."
    )


def make_brief_researcher_agent(
    store: BaseStore,
    *,
    checkpointer: BaseCheckpointSaver | None = None,
) -> CompiledStateGraph:
    """Build the P1 researcher agent wired with P5's user-context tool and PII redaction."""
    return make_researcher_agent(
        checkpointer=checkpointer if checkpointer is not None else InMemorySaver(),
        extra_tools=[make_user_context_tool()],
        extra_middleware=personal_data_redaction(),
        store=store,
        context_schema=UserContext,
    )


def run_personal_brief(
    store: BaseStore,
    user_id: str,
    topic: str,
    *,
    checkpointer: BaseCheckpointSaver | None = None,
    assistant_prompt: str = "Approve this web_search call? [y/n]: ",
) -> ResearchReport | None:
    """Execute the personalized brief workflow (P5 context + P1 research + claim check)."""
    agent = make_brief_researcher_agent(store, checkpointer=checkpointer)
    config: RunnableConfig = {
        "configurable": {"thread_id": f"brief_{uuid.uuid4().hex[:6]}"}
    }
    stream_with_hitl(
        agent,
        {"messages": [HumanMessage(content=brief_request(topic))]},
        config,
        context=UserContext(user_id=user_id),
        assistant_prompt=assistant_prompt,
    )
    return verify_research(agent.get_state(config).values)
