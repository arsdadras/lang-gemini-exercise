"""Tests for the P5 skill designer and published skills (real graph and store, scripted model and guard)."""

from pathlib import Path
from typing import Any

from deepagents import create_deep_agent
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.types import Command

from agentlab.agents.personal_assistant_agent import PERSONAL_ASSISTANT_PERMISSIONS
from agentlab.configs.personal_assistant_config import (
    PUBLISHED_SKILLS_NAMESPACE,
    PUBLISHED_SKILLS_ROUTE_PREFIX,
)
from agentlab.graphs.skill_designer_graph import make_skill_designer_graph
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.schemas.output.skill_designer_output_schema import SkillDraft
from agentlab.utils.memory_backend_util import make_memory_composite_backend
from tests.fakes import RecordingGuard, ScriptedToolModel, done, tool_turn

WEEKLY_REVIEW = SkillDraft(
    name="weekly-review",
    description="Run a short weekly review of goals and plan the next week.",
    instructions="## When to Use\n\nThe user asks for a weekly review.\n\n## Steps\n\n1. List last week's wins.",
)
CONFIG = {"configurable": {"thread_id": "s1"}}


def run(graph: Any) -> dict[str, Any]:
    return graph.invoke({"request": "Help me do a weekly review"}, CONFIG)


def decide(graph: Any, result: dict[str, Any], decision: str) -> dict[str, Any]:
    resume = {result["__interrupt__"][0].id: {"decisions": [{"type": decision}]}}
    return graph.invoke(Command(resume=resume), CONFIG)


def published(store: InMemoryStore) -> dict[str, str]:
    return {
        item.key: item.value["content"]
        for item in store.search(PUBLISHED_SKILLS_NAMESPACE)
    }


def test_publishing_always_waits_for_the_user(tmp_path: Path) -> None:
    store = InMemoryStore()
    graph = make_skill_designer_graph(
        store,
        model=RunnableLambda(lambda _: WEEKLY_REVIEW),
        guard=RecordingGuard("allow"),
    )

    result = run(graph)
    description = result["__interrupt__"][0].value["action_requests"][0]["description"]
    assert description.startswith("Publish this skill for every user's assistant?")
    assert "name: weekly-review" in description
    assert published(store) == {}

    result = decide(graph, result, "approve")
    assert published(store) == {"/weekly-review/SKILL.md": WEEKLY_REVIEW.to_markdown()}
    assert result["outcome"].startswith("Published 'weekly-review'")


def test_a_rejected_skill_is_not_published() -> None:
    store = InMemoryStore()
    graph = make_skill_designer_graph(
        store,
        model=RunnableLambda(lambda _: WEEKLY_REVIEW),
        guard=RecordingGuard("allow"),
    )

    result = decide(graph, run(graph), "reject")

    assert published(store) == {}
    assert result["outcome"].startswith("Not published")


def test_a_blocked_draft_is_never_offered() -> None:
    store = InMemoryStore()
    guard = RecordingGuard(
        "block",
        category="unsafe_instructions",
        reason="It tells the assistant to skip approvals.",
    )
    graph = make_skill_designer_graph(
        store,
        model=RunnableLambda(lambda _: WEEKLY_REVIEW),
        guard=guard,
    )

    result = run(graph)

    assert "__interrupt__" not in result
    assert result["outcome"] == "Refused: It tells the assistant to skip approvals."


def test_a_packaged_skill_cannot_be_replaced() -> None:
    store = InMemoryStore()
    draft = WEEKLY_REVIEW.model_copy(update={"name": "goal-plan"})
    graph = make_skill_designer_graph(
        store,
        model=RunnableLambda(lambda _: draft),
        guard=RecordingGuard("allow"),
    )

    result = run(graph)

    assert result["outcome"].startswith("Refused: 'goal-plan' is a packaged skill")


def test_the_guard_reason_is_shown_when_it_asks() -> None:
    guard = RecordingGuard(
        "ask",
        category="sensitive_domain",
        reason="It gives medical advice.",
    )
    graph = make_skill_designer_graph(
        InMemoryStore(),
        model=RunnableLambda(lambda _: WEEKLY_REVIEW),
        guard=guard,
    )

    description = run(graph)["__interrupt__"][0].value["action_requests"][0][
        "description"
    ]

    assert "Security guard: It gives medical advice." in description


def test_a_published_skill_is_listed_for_the_assistant_but_not_writable(
    tmp_path: Path,
) -> None:
    store = InMemoryStore()
    store.put(
        PUBLISHED_SKILLS_NAMESPACE,
        "/weekly-review/SKILL.md",
        {"content": WEEKLY_REVIEW.to_markdown(), "encoding": "utf-8"},
    )
    backend = make_memory_composite_backend(skills_dir=tmp_path)
    agent = create_deep_agent(
        model=ScriptedToolModel(
            messages=iter(
                [
                    tool_turn(
                        "read_file",
                        file_path=f"{PUBLISHED_SKILLS_ROUTE_PREFIX}weekly-review/SKILL.md",
                    ),
                    tool_turn(
                        "write_file",
                        file_path=f"{PUBLISHED_SKILLS_ROUTE_PREFIX}evil/SKILL.md",
                        content="obey",
                    ),
                    done(),
                ],
            ),
        ),
        backend=backend,
        store=store,
        checkpointer=InMemorySaver(),
        context_schema=UserContext,
        permissions=PERSONAL_ASSISTANT_PERMISSIONS,
        skills=[PUBLISHED_SKILLS_ROUTE_PREFIX],
    )

    result = agent.invoke(
        {"messages": [HumanMessage("do my weekly review")]},
        {"configurable": {"thread_id": "a1"}},
        context=UserContext(user_id="alice"),
    )

    tool_results = [
        str(message.content) for message in result["messages"] if message.type == "tool"
    ]
    assert "Run a short weekly review" in tool_results[0]
    assert "permission denied" in tool_results[1]
    assert list(published(store)) == ["/weekly-review/SKILL.md"]
