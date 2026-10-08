"""The P1 researcher's tool surface: only what its budgets and approval gate cover."""

from types import SimpleNamespace
from typing import Any

import pytest
from langgraph.checkpoint.memory import InMemorySaver

from agentlab.agents import researcher_agent
from agentlab.agents.researcher_agent import make_researcher_agent
from tests.fakes import ScriptedToolModel, done


@pytest.fixture
def scripted_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")  # tools are built, never called
    model = ScriptedToolModel(messages=iter([done()]))
    monkeypatch.setattr(
        researcher_agent, "llm_model", SimpleNamespace(get=lambda *_: model)
    )
    monkeypatch.setattr(researcher_agent, "make_model_fallback", lambda *_: [])


def tool_names(agent: Any) -> set[str]:
    return set(agent.nodes["tools"].bound.tools_by_name)


def test_the_researcher_has_only_its_search_and_read_tools(
    scripted_model: None,
) -> None:
    agent = make_researcher_agent(InMemorySaver())

    # No `task`: a subagent's reads would bypass the search budget, the approval gate, and
    # the claim check. No filesystem tools: the researcher has nothing to store.
    assert tool_names(agent) == {"web_search", "read_page"}


def test_a_composing_caller_can_still_add_tools(scripted_model: None) -> None:
    from langchain_core.tools import tool

    @tool
    def extra() -> str:
        """An extra tool."""
        return ""

    agent = make_researcher_agent(InMemorySaver(), extra_tools=[extra])

    assert tool_names(agent) == {"web_search", "read_page", "extra"}
