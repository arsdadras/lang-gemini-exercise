"""Scripted fakes for running real LangGraph/DeepAgents graphs without a real model."""

import uuid
from typing import Any

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage


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
