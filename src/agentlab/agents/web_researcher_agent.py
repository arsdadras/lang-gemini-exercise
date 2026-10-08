"""P1 researcher: searches its sources, reads, and returns a ``ResearchDraft`` of cited claims.

The draft is checked against the documents the agent's source tools returned
(``subagents.research_subagent.verify_research``) before it becomes a ``ResearchReport``.

Its sources (R1 topic 3): the web (``web_search`` and ``read_page``), research papers
(``academic_search``, when Exa's key is set), and documents (``search_documents``): this
project's own docs and code through P2's index, or the ``.txt`` and ``.md`` files the caller
gives in ``options.documents``. In the research graph a router picks each sub-question's sources, and
``SourceRouteMiddleware`` limits the run to their tools.

A plain ``create_agent``, not a deep agent: every tool the researcher has is one its budgets,
approval gate, and claim check must cover. A deep agent would add filesystem tools it never uses
(its general-purpose subagent is off everywhere, ``utils/deep_agent_util.py``).
"""

from collections.abc import Sequence
from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware, ToolCallLimitMiddleware
from langchain_core.tools import BaseTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.base import BaseStore

from agentlab.configs.paths_config import checkpoint_db_path
from agentlab.configs.research_config import CORPUS_RESULTS, DEPTH_BUDGETS
from agentlab.data.sqlite_db_data import get_sqlite_checkpointer
from agentlab.middlewares.fallback_middleware import make_model_fallback
from agentlab.middlewares.hitl_middleware import hitl_for
from agentlab.middlewares.source_route_middleware import SourceRouteMiddleware
from agentlab.models import llm_model
from agentlab.prompts.agents_prompt import build_web_researcher_prompt
from agentlab.retrieval.documents_retrieval import build_document_retriever
from agentlab.retrieval.index_retrieval import get_retriever
from agentlab.schemas.input.research_input_schema import ResearchOptions
from agentlab.schemas.output.research_output_schema import ResearchDraft
from agentlab.tools.academic_search_tool import (
    ACADEMIC_SEARCH_TOOL_NAME,
    make_academic_search_tool,
)
from agentlab.tools.documents_search_tool import (
    DOCUMENTS_SEARCH_TOOL_NAME,
    make_documents_search_tool,
)
from agentlab.tools.read_page_tool import READ_PAGE_TOOL_NAME, make_read_page_tool
from agentlab.tools.research_source_tool import documents_description, research_sources
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
    prompt, and the domain, recency, and source filters on the tools; a blocked call tells the
    agent to write its report from what it has. ``options.sources`` and what this environment can
    serve (``research_sources``) decide which source tools the agent has. Each search tool gets the
    search budget of its own, and the outbound searches (web and academic) wait for approval;
    the documents are this project's own or the caller's, so searching them asks no one. Broad
    topics are split by ``run_research``'s planner, one run per sub-question, instead of the
    ``researcher`` subagent: a subagent's documents never reach this run's messages, so the claim
    check could support none of its claims.

    A composing workflow can add tools and middleware (for example P5's user context tool
    with personal-data redaction), with the ``store`` and ``context_schema`` they need.
    """
    options = options or ResearchOptions()
    budget = DEPTH_BUDGETS[options.depth]
    sources, _ = research_sources(options)
    documents = documents_description(options)
    tools: list[BaseTool] = []
    if "web" in sources:
        tools += [
            make_web_search_tool(
                include_domains=options.include_domains,
                exclude_domains=options.exclude_domains,
                time_range=options.recency,
                topic=options.source_type,
            ),
            make_read_page_tool(options.include_domains, options.exclude_domains),
        ]
    if "academic" in sources:
        tools.append(
            make_academic_search_tool(options.include_domains, options.exclude_domains)
        )
    if "documents" in sources:
        paths = list(options.documents)
        tools.append(
            make_documents_search_tool(
                (lambda: build_document_retriever(paths, CORPUS_RESULTS))
                if paths
                else (lambda: get_retriever(CORPUS_RESULTS)),
                documents,
            )
        )
    names = {tool.name for tool in tools}
    searches = [
        name
        for name in (
            WEB_SEARCH_TOOL_NAME,
            ACADEMIC_SEARCH_TOOL_NAME,
            DOCUMENTS_SEARCH_TOOL_NAME,
        )
        if name in names
    ]
    approvals = [name for name in searches if name != DOCUMENTS_SEARCH_TOOL_NAME]
    limits = [
        ToolCallLimitMiddleware(
            tool_name=name, run_limit=budget.searches, exit_behavior="continue"
        )
        for name in searches
    ]
    if READ_PAGE_TOOL_NAME in names:
        limits.append(
            ToolCallLimitMiddleware(
                tool_name=READ_PAGE_TOOL_NAME,
                run_limit=budget.reads,
                exit_behavior="continue",
            )
        )
    return create_agent(
        model=llm_model.get(tier),
        system_prompt=build_web_researcher_prompt(
            searches=budget.searches,
            reads=budget.reads,
            claims=budget.claims,
            language=options.language,
            output=options.output,
            sources=sources,
            documents=documents,
        ),
        tools=[*tools, *extra_tools],
        checkpointer=checkpointer
        if checkpointer is not None
        else get_sqlite_checkpointer(checkpoint_db_path("research")),
        response_format=ResearchDraft,
        middleware=[
            *make_model_fallback(tier),
            SourceRouteMiddleware(),
            *([hitl_for(approvals)] if approvals else []),
            *limits,
            *extra_middleware,
        ],
        store=store,
        context_schema=context_schema,
    )
