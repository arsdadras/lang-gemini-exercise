"""Tests for P5's context provider tool and the personal brief's data redaction (real graph, scripted model)."""

from typing import Any

from deepagents import create_deep_agent
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

from agentlab.apps.personal_brief_app import personal_data_redaction
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.tools.user_context_tool import NO_USER_CONTEXT, make_user_context_tool
from tests.fakes import done, tool_turn

SEEN: list[list[BaseMessage]] = []


class SeeingModel(GenericFakeChatModel):
    """Scripted model that records the messages it was shown in ``SEEN``."""

    def bind_tools(self, tools: Any, **kwargs: Any) -> "SeeingModel":
        return self

    def _generate(self, messages: list[BaseMessage], *args: Any, **kwargs: Any) -> Any:
        SEEN.append(list(messages))
        return super()._generate(messages, *args, **kwargs)


def make_store() -> InMemoryStore:
    store = InMemoryStore()
    profile = "- Name: Sara\n- Email: sara@example.com\n- Vegetarian\n- OpenAI key: sk-proj-" + "a1B2c3D4" * 4
    store.put(("sara", "memories"), "/user_profile.md", {"content": profile, "encoding": "utf-8"})
    store.put(("sara", "memories"), "/goals/walking.md", {"content": "# Goal: Walk daily", "encoding": "utf-8"})
    store.put(("bob", "memories"), "/user_profile.md", {"content": "- Name: Bob", "encoding": "utf-8"})
    return store


def ask(store: InMemoryStore, user_id: str, middleware: list[Any]) -> str:
    SEEN.clear()
    model = SeeingModel(messages=iter([tool_turn("get_user_context"), done()]))
    agent = create_deep_agent(
        model=model,
        tools=[make_user_context_tool()],
        middleware=middleware,
        store=store,
        checkpointer=InMemorySaver(),
        context_schema=UserContext,
    )
    result = agent.invoke(
        {"messages": [HumanMessage("brief me")]},
        {"configurable": {"thread_id": user_id}},
        context=UserContext(user_id=user_id),
    )
    return next(str(message.content) for message in result["messages"] if message.type == "tool")


def test_the_tool_returns_only_the_calling_users_memory_with_secrets_redacted() -> None:
    context = ask(make_store(), "sara", [])

    assert '<file path="/memories/user_profile.md">' in context and "# Goal: Walk daily" in context
    assert "Bob" not in context
    assert "sk-proj-" not in context and "[SECRET_DETECTED]" in context


def test_a_user_without_memory_gets_a_plain_answer() -> None:
    context = ask(make_store(), "nobody", [])

    assert context == NO_USER_CONTEXT


def test_the_brief_redacts_personal_data_before_the_research_model_sees_it() -> None:
    context = ask(make_store(), "sara", personal_data_redaction())

    assert "sara@example.com" not in context
    assert "sara@example.com" not in str(SEEN[-1])
    assert "Vegetarian" in context
