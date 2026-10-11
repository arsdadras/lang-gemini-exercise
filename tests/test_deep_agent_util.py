"""No deep agent gets DeepAgents' default general-purpose subagent, whatever its provider."""

from typing import Any

import pytest
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from agentlab.utils.deep_agent_util import create_deep_agent


def tool_names(agent: Any) -> set[str]:
    return set(agent.nodes["tools"].bound.tools_by_name)


@pytest.mark.parametrize(
    "model",
    [
        ChatOpenAI(model="gpt-x", api_key="test-key", base_url="http://127.0.0.1:9/v1"),
        ChatGoogleGenerativeAI(model="gemini-x", google_api_key="test-key"),
        ChatOllama(model="qwen-x"),
    ],
    ids=["openai", "google_genai", "ollama"],
)
def test_an_agent_without_subagents_has_no_task_tool(model: Any) -> None:
    agent = create_deep_agent(model=model)

    assert "task" not in tool_names(agent)
    assert "read_file" in tool_names(agent)  # the rest of the deep agent is still there


def test_named_subagents_still_get_the_task_tool() -> None:
    model = ChatOpenAI(
        model="gpt-x", api_key="test-key", base_url="http://127.0.0.1:9/v1"
    )
    agent = create_deep_agent(
        model=model,
        subagents=[
            {
                "name": "reviewer",
                "description": "Reviews code.",
                "system_prompt": "Review.",
            }
        ],
    )

    assert "task" in tool_names(agent)
