"""Node functions for the P5 memory consolidator.

``consolidate`` asks the model for line-level edits. ``apply_next_edit`` applies one edit per
run, through the memory gate: the model proposes, code decides what the edit does to the file.
"""

import hashlib
import time
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
from agentlab.middlewares.memory_approval_middleware import (
    REJECTION_PREFIX,
    GatedMemoryBackend,
)
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
NO_REJECTIONS = "(none)"
REJECTIONS_KIND = "memory_rejections"
# The consolidator sees the most recent rejections; older ones age out of its view.
MAX_REJECTIONS_SHOWN = 30


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


def _read_rejections(runtime: Runtime[UserContext]) -> list[str]:
    """Edits the user rejected before, newest first, so they aren't proposed again."""
    namespace = (user_memory_namespace(runtime)[0], REJECTIONS_KIND)
    items = runtime.store.search(namespace, limit=1000)
    items.sort(key=lambda item: item.value.get("rejected_at", 0), reverse=True)
    return [item.value["edit"] for item in items[:MAX_REJECTIONS_SHOWN]]


def _remember_rejection(runtime: Runtime[UserContext], edit: MemoryEdit) -> None:
    namespace = (user_memory_namespace(runtime)[0], REJECTIONS_KIND)
    key = hashlib.sha256(edit.describe().encode()).hexdigest()
    runtime.store.put(namespace, key, {"edit": edit.describe(), "rejected_at": time.time()})


def make_consolidate_node(
    model: Runnable | None = None,
) -> Callable[[MemoryConsolidationState, Runtime[UserContext]], dict]:
    """Build the node that compares the conversation with memory and proposes edits."""
    chain = MEMORY_CONSOLIDATION_PROMPT | (
        model
        if model is not None
        else llm_model.chain(CONSOLIDATOR_TIER, structured=MemoryEdits, provider=CONSOLIDATOR_PROVIDER)
    )

    def consolidate(state: MemoryConsolidationState, runtime: Runtime[UserContext]) -> dict:
        files = _read_memory(runtime)
        memory = "\n\n".join(f'<file path="{path}">\n{text}\n</file>' for path, text in files.items())
        rejected = "\n".join(f"- {edit}" for edit in _read_rejections(runtime)) or NO_REJECTIONS
        proposal = chain.invoke(
            {"memory": memory or NO_MEMORY, "rejected": rejected, "transcript": state["transcript"]}
        )
        # Additions first: they rarely need approval, so they land even if the user
        # never gets to the changes that do.
        edits = sorted(proposal.edits, key=lambda edit: edit.kind != "add")
        return {"edits": [edit.model_dump() for edit in edits], "cursor": 0}

    return consolidate


def _memory_key(path: str) -> str | None:
    """The storage key for a proposed path, or ``None`` if it isn't a memory file."""
    if not path.startswith(MEMORIES_ROUTE_PREFIX) or not path.endswith(".md") or ".." in path:
        return None
    return path[len(MEMORIES_ROUTE_PREFIX) - 1 :]


def _find_line(text: str, line: str) -> str | None:
    """The file's own spelling of ``line``, if it appears exactly once as a whole line."""
    matches = [candidate for candidate in text.splitlines() if candidate.strip() == line.strip()]
    return matches[0] if len(matches) == 1 else None


def _section(text: str, heading: str) -> str | None:
    """The heading line and the lines under it, up to the next heading, without trailing blanks."""
    heading_line = _find_line(text, heading)
    if heading_line is None:
        return None
    lines = text.splitlines()
    start = lines.index(heading_line)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("#")), len(lines))
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1
    return "\n".join(lines[start:end])


def _apply(edit: MemoryEdit, key: str, current: str | None, backend: GatedMemoryBackend) -> str:
    """Turn one edit into one gated write or edit, and say what happened."""
    result: WriteResult | EditResult
    if edit.kind == "add" and current is None:
        result = backend.write(key, edit.new.rstrip("\n") + "\n")
    elif edit.kind == "add":
        if _find_line(current, edit.new) is not None:
            return f"Skipped {edit.describe()} (already in memory)."
        section = _section(current, edit.section) if edit.section else None
        if section is not None:
            result = backend.edit(key, section, f"{section}\n{edit.new}")
        else:
            heading = f"\n{edit.section}\n" if edit.section else ""
            separator = "" if current.endswith("\n") else "\n"
            result = backend.edit(key, current, f"{current}{separator}{heading}{edit.new}\n")
    else:
        line = _find_line(current or "", edit.old)
        if line is None:
            return f"Skipped {edit.describe()} (that line is not in memory)."
        old = line if edit.kind == "replace" else (f"{line}\n" if f"{line}\n" in current else line)
        new = edit.new if edit.kind == "replace" else ""
        result = backend.edit(key, old, new, requested=edit.user_requested)
    if result.error:
        return f"Not applied {edit.describe()}: {result.error}"
    return f"Applied {edit.describe()}."


def make_apply_next_edit_node(
    backend: GatedMemoryBackend,
) -> Callable[[MemoryConsolidationState, Runtime[UserContext]], dict]:
    """Build the node that applies the edit at ``cursor``, then moves the cursor on.

    One edit per run, so a run holds at most one approval. A resumed run starts over from the
    top; with a single edit, it asks the same question again and nothing before it repeats.
    """

    def apply_next_edit(state: MemoryConsolidationState, runtime: Runtime[UserContext]) -> dict:
        edit = MemoryEdit.model_validate(state["edits"][state["cursor"]])
        key = _memory_key(edit.path)
        if key is None:
            outcome = f"Skipped {edit.path}: not a memory file."
        else:
            stored = runtime.store.get(user_memory_namespace(runtime), key)
            outcome = _apply(edit, key, _stored_text(stored.value) if stored else None, backend)
            if REJECTION_PREFIX in outcome:
                _remember_rejection(runtime, edit)
        return {"cursor": state["cursor"] + 1, "outcomes": [outcome]}

    return apply_next_edit
