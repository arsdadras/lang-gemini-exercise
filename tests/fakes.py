"""Scripted fakes for running real LangGraph/DeepAgents graphs without a real model."""

import uuid
from typing import Any

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from agentlab.schemas.output.middlewares_output_schema import GuardVerdict


class ScriptedToolModel(GenericFakeChatModel):
    """Fake chat model that accepts tool binding, as the agent loop requires."""

    def bind_tools(self, tools: Any, **kwargs: Any) -> "ScriptedToolModel":
        return self


def tool_turn(name: str, **args: Any) -> AIMessage:
    """A model reply that calls one tool."""
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": uuid.uuid4().hex}])


def done() -> AIMessage:
    """A final model reply.

    A fresh message each time: LangGraph merges messages by id, so reusing one
    instance would overwrite the earlier reply instead of appending a new one.
    """
    return AIMessage(content="Done.")


class RecordingGuard:
    """Scripted security guard: returns its decisions in turn (repeating the last) and records calls."""

    def __init__(self, *decisions: str, category: str = "test", reason: str = "Scripted verdict.") -> None:
        self.verdicts = [GuardVerdict(decision=decision, category=category, reason=reason) for decision in decisions]
        self.calls: list[tuple[str, str]] = []

    def __call__(self, action: str, content: str) -> GuardVerdict:
        self.calls.append((action, content))
        return self.verdicts[min(len(self.calls), len(self.verdicts)) - 1]
