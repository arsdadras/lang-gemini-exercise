"""Structured output of the P5 memory consolidator: line-level edits, not rewritten files."""

from typing import Literal

from pydantic import BaseModel, Field


class MemoryEdit(BaseModel):
    """One change to one memory file. Code decides how it lands in the file."""

    kind: Literal["add", "replace", "remove"]
    path: str = Field(description="Full path under /memories/, e.g. /memories/user_profile.md.")
    section: str = Field(
        default="",
        description="add: the heading to add under, e.g. '## Preferences'. Empty for a new file.",
    )
    old: str = Field(default="", description="replace/remove: one existing line, copied exactly.")
    new: str = Field(
        default="",
        description="add/replace: the new line. For add to a file that doesn't exist, its full content.",
    )
    reason: str = Field(description="What the user said that shows this change.")

    def describe(self) -> str:
        if self.kind == "add":
            return f"{self.path}: + {self.new}"
        if self.kind == "replace":
            return f"{self.path}: {self.old} -> {self.new}"
        return f"{self.path}: - {self.old}"


class MemoryEdits(BaseModel):
    """The edits a finished conversation makes to memory; empty when nothing changes."""

    edits: list[MemoryEdit] = Field(default_factory=list)



"""Graph state for the P5 memory consolidator."""

import operator
from typing import Annotated, Any, TypedDict


class MemoryConsolidationState(TypedDict, total=False):
    transcript: str
    """The finished conversation, as plain text (see ``format_transcript``)."""
    edits: list[dict[str, Any]]
    """Proposed ``MemoryEdit``s as plain dicts, kept in the checkpoint until the user reviews."""
    cursor: int
    """Index of the next edit to apply."""
    outcomes: Annotated[list[str], operator.add]
    """One line per edit: applied, skipped, blocked, or rejected."""


"""Node functions for the P5 memory consolidator.

``consolidate`` asks the model for line-level edits. ``apply_next_edit`` applies one edit per
run, through the memory gate: the model proposes, code decides what the edit does to the file.
"""

from collections.abc import Callable, Sequence
from typing import Any

from deepagents.backends.protocol import EditResult, WriteResult
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.runnables import Runnable
from langgraph.runtime import Runtime

from agentlab.configs.personal_assistant_config import (
    CONSOLIDATOR_PROVIDER,
    CONSOLIDATOR_TIER,
    MEMORIES_ROUTE_PREFIX,
)
from agentlab.middlewares.memory_approval_middleware import GatedMemoryBackend
from agentlab.models import llm_model
from agentlab.prompts.nodes.memory_consolidation_prompt import (
    MEMORY_CONSOLIDATION_PROMPT,
)
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.schemas.output.memory_consolidation_output_schema import (
    MemoryEdit,
    MemoryEdits,
)
from agentlab.schemas.state.memory_consolidation_state import MemoryConsolidationState
from agentlab.utils.get_text_util import get_text
from agentlab.utils.memory_backend_util import user_memory_namespace

NO_MEMORY = "(no memory files yet)"


def format_transcript(messages: Sequence[BaseMessage]) -> str:
    """The user's and the assistant's words only: tool calls and results are left out."""
    lines = []
    for message in messages:
        text = get_text(message).strip()
        if not text:
            continue
        if isinstance(message, HumanMessage):
            lines.append(f"User: {text}")
        elif isinstance(message, AIMessage):
            lines.append(f"Assistant: {text}")
    return "\n\n".join(lines)


def _stored_text(value: dict[str, Any]) -> str:
    content = value.get("content", "")
    return "\n".join(content) if isinstance(content, list) else content


def _read_memory(runtime: Runtime[UserContext]) -> dict[str, str]:
    """Every memory file of the current user, keyed by full path."""
    items = runtime.store.search(user_memory_namespace(runtime), limit=1000)
    return {MEMORIES_ROUTE_PREFIX.rstrip("/") + item.key: _stored_text(item.value) for item in items}


def make_consolidate_node(model: Runnable | None = None) -> Callable[[MemoryConsolidationState, Runtime[UserContext]], dict]:
    chain = MEMORY_CONSOLIDATION_PROMPT | (
    model if model is not None
    else llm_model.chain(CONSOLIDATOR_TIER, provider=CONSOLIDATOR_PROVIDER, structured=MemoryEdits)
    )
    def consolidate(state: MemoryConsolidationState, runtime: Runtime[UserContext]) -> dict:
        files = _read_memory(runtime)
        memory = "\n\n".join(f'<file path="{path}">\n{text}\n</file>' for path, text in files.items())
        proposal = chain.invoke({"memory": memory or NO_MEMORY, "transcript": state.get("transcript")})

