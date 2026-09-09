"""Unit tests for src/core infrastructure: AgentManifest, AgentRegistry, and as_subagent."""

import pytest

from core.decorators import as_subagent
from core.manifest import AgentManifest
from core.registry import AgentRegistry


def test_agent_manifest_creation():
    """Verify AgentManifest schema and default values."""
    manifest = AgentManifest(
        name="test_worker",
        display_name="Test Worker",
        description="A worker agent for automated testing.",
        agent_type="pure",
        model_tier="low",
        tools=["mock_tool"],
    )
    assert manifest.name == "test_worker"
    assert manifest.display_name == "Test Worker"
    assert manifest.agent_type == "pure"
    assert manifest.model_tier == "low"
    assert manifest.tools == ["mock_tool"]
    assert manifest.subagent_names == []


def test_agent_registry_register_and_get():
    """Verify factory registration and lazy instantiation."""
    reg = AgentRegistry()
    manifest = AgentManifest(
        name="greeter",
        display_name="Greeter",
        description="Greets users",
    )

    @reg.register("greeter", manifest=manifest)
    def make_greeter(greeting: str = "Hello"):
        return {"type": "greeter", "greeting": greeting}

    assert "greeter" in reg.list_agents()
    assert reg.get_manifest("greeter") == manifest

    agent_instance = reg.get("greeter", greeting="Salam")
    assert agent_instance == {"type": "greeter", "greeting": "Salam"}


def test_agent_registry_duplicate_raises():
    """Verify registering duplicate agent names raises ValueError."""
    reg = AgentRegistry()

    @reg.register("worker")
    def worker1():
        return 1

    with pytest.raises(ValueError, match="already registered"):

        @reg.register("worker")
        def worker2():
            return 2


def test_agent_registry_not_found_raises():
    """Verify getting an unknown agent raises KeyError."""
    reg = AgentRegistry()
    with pytest.raises(KeyError, match="not found"):
        reg.get("non_existent_agent")


def test_as_subagent_decorator():
    """Verify as_subagent wraps a function into a DeepAgents-compatible CompiledSubAgent."""
    manifest = AgentManifest(
        name="echo_subagent",
        display_name="Echo Subagent",
        description="Echoes back the input task.",
    )

    @as_subagent(manifest)
    def run_echo(state: dict) -> dict:
        messages = state.get("messages", [])
        return {"messages": messages}

    assert isinstance(run_echo, dict)
    assert run_echo["name"] == "echo_subagent"
    assert (
        run_echo["description"] == "Echo Subagent"
        or run_echo["description"] == manifest.description
    )
    assert hasattr(run_echo["runnable"], "invoke")

    output = run_echo["runnable"].invoke({"messages": ["ping"]})
    assert output == {"messages": ["ping"]}
