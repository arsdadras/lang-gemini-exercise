"""P1 web-researcher agent — searches the web and returns a structured, cited
`ResearchReport`, delegating narrow sub-questions to `researcher_subagent`.
"""

from deepagents import create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver
from middlewares.hitl import search_approval
from middlewares.retry import retry_on_failure
from models import llm_model
from output_schemas.research import ResearchReport
from prompts.agents import build_web_researcher_prompt
from subagents import researcher_subagent
from tools.search import web_search

web_researcher_agent = create_deep_agent(
    model=llm_model.get("low"),
    system_prompt=build_web_researcher_prompt(),
    tools=[web_search],
    checkpointer=InMemorySaver(),
    response_format=ResearchReport,
    middleware=[retry_on_failure("low"), search_approval],
    subagents=[researcher_subagent],
)
