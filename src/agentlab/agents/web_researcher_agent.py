"""P1 web researcher: searches the web and returns a structured, cited ``ResearchReport``."""

from collections.abc import Sequence
from typing import Any

from deepagents import create_deep_agent
from langchain.agents.middleware import AgentMiddleware
from langchain_core.tools import BaseTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.base import BaseStore

from agentlab.data.sqlite_db_data import get_sqlite_checkpointer
from agentlab.middlewares.fallback_middleware import make_model_fallback
from agentlab.middlewares.hitl_middleware import hitl_for
from agentlab.models import llm_model
from agentlab.prompts.agents_prompt import build_web_researcher_prompt
from agentlab.schemas.output.research_output_schema import ResearchReport
from agentlab.subagents.research_subagent import make_researcher_subagent
from agentlab.tools.web_search_tool import WEB_SEARCH_TOOL_NAME, make_web_search_tool


def make_web_researcher_agent(
    checkpointer: BaseCheckpointSaver | None = None,
    *,
    tier: str = "low",
    extra_tools: Sequence[BaseTool] = (),
    extra_middleware: Sequence[AgentMiddleware] = (),
    store: BaseStore | None = None,
    context_schema: type[Any] | None = None,
) -> CompiledStateGraph:
    """Build the researcher.

    Every ``web_search`` call pauses for human approval, which is why the agent
    always needs a checkpointer (defaults to the shared SQLite one). Narrow
    sub-questions can be delegated to the ``researcher`` subagent.

    A composing workflow can add tools and middleware (for example P5's user context tool
    with personal-data redaction), with the ``store`` and ``context_schema`` they need.
    """
    return create_deep_agent(
        model=llm_model.get(tier),
        system_prompt=build_web_researcher_prompt(),
        tools=[make_web_search_tool(), *extra_tools],
        checkpointer=checkpointer
        if checkpointer is not None
        else get_sqlite_checkpointer(),
        response_format=ResearchReport,
        middleware=[
            make_model_fallback(tier),
            hitl_for(WEB_SEARCH_TOOL_NAME),
            *extra_middleware,
        ],
        subagents=[make_researcher_subagent()],
        store=store,
        context_schema=context_schema,
    )
