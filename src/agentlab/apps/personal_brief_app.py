"""Mini-workflow P5 + P1, a personalized research brief: ``lab-brief [user_id]``.

P1 researches the topic; P5 supplies the user's stored context through a read-only tool, so the
brief fits their constraints and goals. Personal data in that context (emails, card numbers,
IPs) is redacted before the research model sees it, so it can't leak into web searches.
Defaults to the P5 app's last active user.
"""

import sys
import uuid

from dotenv import load_dotenv
from langchain.agents.middleware import PIIMiddleware
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from agentlab.agents.web_researcher_agent import make_web_researcher_agent
from agentlab.configs.personal_assistant_config import ASSISTANT_STORE_DB_PATH
from agentlab.data.sqlite_db_data import get_sqlite_store
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.schemas.output.research_output_schema import ResearchReport
from agentlab.tools.user_context_tool import (
    USER_CONTEXT_TOOL_NAME,
    make_user_context_tool,
)
from agentlab.utils.console_util import configure_utf8_stdout
from agentlab.utils.memory_session_util import load_session
from agentlab.utils.run_with_hitl_util import stream_with_hitl

# Personal data the user context may hold that must not reach the research model.
PERSONAL_DATA_TYPES = ("email", "credit_card", "ip")


def personal_data_redaction() -> list[PIIMiddleware]:
    """Redact personal data from tool results (the user context) before the model reads them."""
    return [
        PIIMiddleware(kind, strategy="redact", apply_to_input=False, apply_to_tool_results=True)
        for kind in PERSONAL_DATA_TYPES
    ]


def brief_request(topic: str) -> str:
    return (
        f"Research this for me: {topic}\n\n"
        f"First call {USER_CONTEXT_TOOL_NAME} and tailor the report to my stored constraints, "
        "preferences, and goals; say in the summary which of them shaped it."
    )


def main() -> None:
    """Research one topic for the user, tailored to their P5 memory."""
    load_dotenv()
    configure_utf8_stdout()
    store = get_sqlite_store(ASSISTANT_STORE_DB_PATH)
    user_id = sys.argv[1] if len(sys.argv) > 1 else load_session(store)[0]
    agent = make_web_researcher_agent(
        checkpointer=InMemorySaver(),
        extra_tools=[make_user_context_tool()],
        extra_middleware=personal_data_redaction(),
        store=store,
        context_schema=UserContext,
    )

    topic = input(f"[{user_id}] Topic to research: ").strip()
    if not topic:
        print("No topic given.")
        return
    config = {"configurable": {"thread_id": f"brief_{uuid.uuid4().hex[:6]}"}}
    stream_with_hitl(
        agent,
        {"messages": [HumanMessage(content=brief_request(topic))]},
        config,
        context=UserContext(user_id=user_id),
        assistant_prompt="Approve this web_search call? [y/n]: ",
    )
    report: ResearchReport | None = agent.get_state(config).values.get("structured_response")
    print(report.model_dump_json(indent=2) if report else "No report was produced.")


if __name__ == "__main__":
    main()
