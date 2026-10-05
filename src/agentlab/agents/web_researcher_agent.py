"""P1 web researcher: searches, reads pages, and returns a ``ResearchDraft`` of cited claims.

The draft is checked against the pages the agent read (``subagents.research_subagent.verify_research``)
before it becomes a ``ResearchReport``.
"""

from collections.abc import Sequence
from typing import Any

from deepagents import create_deep_agent
from langchain.agents.middleware import AgentMiddleware, ToolCallLimitMiddleware
from langchain_core.tools import BaseTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.base import BaseStore

from agentlab.configs.paths_config import checkpoint_db_path
from agentlab.configs.research_config import DEPTH_BUDGETS
from agentlab.data.sqlite_db_data import get_sqlite_checkpointer
from agentlab.middlewares.fallback_middleware import make_model_fallback
from agentlab.middlewares.hitl_middleware import hitl_for
from agentlab.models import llm_model
from agentlab.prompts.agents_prompt import build_web_researcher_prompt
from agentlab.schemas.input.research_input_schema import ResearchOptions
from agentlab.schemas.output.research_output_schema import ResearchDraft
from agentlab.tools.read_page_tool import READ_PAGE_TOOL_NAME, make_read_page_tool
from agentlab.tools.web_search_tool import WEB_SEARCH_TOOL_NAME, make_web_search_tool


def make_web_researcher_agent(
    checkpointer: BaseCheckpointSaver | None = None,
    *,
    tier: str = "low",  # paid tier only: tool-calling loop, not opensource/free (ADR-0014)
    extra_tools: Sequence[BaseTool] = (),
    extra_middleware: Sequence[AgentMiddleware] = (),
    store: BaseStore | None = None,
    context_schema: type[Any] | None = None,
    options: ResearchOptions | None = None,
) -> CompiledStateGraph:
    """Build the researcher.

    Every ``web_search`` call pauses for human approval, which is why the agent
    always needs a checkpointer (defaults to the research app's SQLite one).

    ``options`` (R1 topic 2) set the run's search and read budgets, the claim cap in the
    prompt, and the domain, recency, and source filters on both tools; a blocked call tells the
    agent to write its report from what it has. Broad topics are split by ``run_research``'s
    planner, one run per sub-question, instead of the ``researcher`` subagent: a subagent's pages
    never reach this run's messages, so the claim check could support none of its claims.

    A composing workflow can add tools and middleware (for example P5's user context tool
    with personal-data redaction), with the ``store`` and ``context_schema`` they need.
    """
    options = options or ResearchOptions()
    budget = DEPTH_BUDGETS[options.depth]
    return create_deep_agent(
        model=llm_model.get(tier),
        system_prompt=build_web_researcher_prompt(
            searches=budget.searches,
            reads=budget.reads,
            claims=budget.claims,
            language=options.language,
            output=options.output,
        ),
        tools=[
            make_web_search_tool(
                include_domains=options.include_domains,
                exclude_domains=options.exclude_domains,
                time_range=options.recency,
                topic=options.source_type,
            ),
            make_read_page_tool(options.include_domains, options.exclude_domains),
            *extra_tools,
        ],
        checkpointer=checkpointer
        if checkpointer is not None
        else get_sqlite_checkpointer(checkpoint_db_path("research")),
        response_format=ResearchDraft,
        middleware=[
            make_model_fallback(tier),
            hitl_for(WEB_SEARCH_TOOL_NAME),
            ToolCallLimitMiddleware(
                tool_name=WEB_SEARCH_TOOL_NAME,
                run_limit=budget.searches,
                exit_behavior="continue",
            ),
            ToolCallLimitMiddleware(
                tool_name=READ_PAGE_TOOL_NAME,
                run_limit=budget.reads,
                exit_behavior="continue",
            ),
            *extra_middleware,
        ],
        store=store,
        context_schema=context_schema,
    )
