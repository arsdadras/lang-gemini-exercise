"""P1 web-researcher agent — searches the web and returns a structured, cited
`ResearchReport`, delegating narrow sub-questions to `researcher_subagent`.
"""

from langgraph.checkpoint.memory import InMemorySaver
from deepagents import create_deep_agent
from models import llm_model
from subagents import researcher_subagent
from prompts.agents import build_web_researcher_prompt
from output_schemas.research import ResearchReport
from middlewares.retry import retry_on_failure
from middlewares.hitl import search_approval
from tools.search import web_search

web_researcher_agent = create_deep_agent(
    model=llm_model.get("lite"),
    system_prompt=build_web_researcher_prompt(),
    tools=[web_search],
    checkpointer=InMemorySaver(),
    response_format=ResearchReport,
    middleware=[retry_on_failure, search_approval],
    subagents=[researcher_subagent],
)
