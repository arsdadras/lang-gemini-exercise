"""Memory lifecycle around the P5 assistant's conversations: consolidate, review, undo, forget.

The assistant only reads memory; ``MemorySessions`` runs the consolidator (its single writer,
ADR-0012) and keeps the bookkeeping durable in the store, so nothing is lost when the app exits:

- ``(user, "threads")``: each conversation thread and how many of its messages were consolidated;
- ``(user, "memory_reviews")``: consolidation runs whose proposal the user hasn't reviewed yet.

A consolidation covers only the messages after the thread's watermark. It starts when a
conversation ends, and also mid-conversation once the unconsolidated part grows long, so a
long thread never becomes one huge transcript.
"""

import time
import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any

from langchain_core.messages import BaseMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.base import BaseStore

from agentlab.configs.personal_assistant_config import (
    DEFAULT_ASSISTANT_THREAD_ID,
    DEFAULT_USER_ID,
)
from agentlab.middlewares.memory_approval_middleware import HISTORY_KIND
from agentlab.nodes.memory_consolidation_node import format_transcript
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.schemas.output.memory_consolidation_output_schema import MemoryEdit
from agentlab.utils.memory_backend_util import MEMORIES_NAMESPACE_KIND
from agentlab.utils.run_with_hitl_util import resume_pending_with_hitl

THREADS_KIND = "threads"
REVIEWS_KIND = "memory_reviews"
_SESSION_NAMESPACE = ("app", "personal_assistant")


def load_session(store: BaseStore) -> tuple[str, str]:
    """The P5 app's last active user and thread, or the defaults on first run."""
    item = store.get(_SESSION_NAMESPACE, "last")
    if item is None:
        return DEFAULT_USER_ID, DEFAULT_ASSISTANT_THREAD_ID
    return item.value["user_id"], item.value["thread_id"]


def save_session(store: BaseStore, user_id: str, thread_id: str) -> None:
    store.put(_SESSION_NAMESPACE, "last", {"user_id": user_id, "thread_id": thread_id})


def _config(thread_id: str) -> dict[str, Any]:
    return {"configurable": {"thread_id": thread_id}}


class MemorySessions:
    """Consolidate finished conversation segments in the background; review them later.

    ``start`` and ``queue`` never block the chat. ``review`` runs in the main loop before the
    user's next message: it shows what a finished run proposed and asks for the changes that
    need approval. ``resume`` restarts, after an app restart, the runs that didn't finish.
    """

    def __init__(
        self,
        store: BaseStore,
        assistant: CompiledStateGraph,
        consolidator: CompiledStateGraph,
        *,
        long_thread_chars: int,
    ) -> None:
        self._store = store
        self._assistant = assistant
        self._consolidator = consolidator
        self._long_thread_chars = long_thread_chars
        # One worker: consolidations of the same memory run one after another, never at once.
        self._executor = ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="memory-consolidation",
        )
        self._running: dict[str, Future] = {}

    # --- threads and their unconsolidated messages -----------------------------------------

    def _messages(self, thread_id: str) -> list[BaseMessage]:
        return self._assistant.get_state(_config(thread_id)).values.get("messages", [])

    def _watermark(self, user_id: str, thread_id: str) -> int:
        item = self._store.get((user_id, THREADS_KIND), thread_id)
        return item.value["consolidated"] if item else 0

    def track(self, user_id: str, thread_id: str) -> None:
        """Record that ``thread_id`` belongs to ``user_id`` (for review, resume, and forget)."""
        if self._store.get((user_id, THREADS_KIND), thread_id) is None:
            self._store.put(
                (user_id, THREADS_KIND),
                thread_id,
                {"consolidated": 0, "created_at": time.time()},
            )

    def _take_segment(self, user_id: str, thread_id: str) -> str:
        """The unconsolidated part of the thread as a transcript; moves the watermark past it."""
        messages = self._messages(thread_id)
        start = self._watermark(user_id, thread_id)
        transcript = format_transcript(messages[start:])
        record = self._store.get((user_id, THREADS_KIND), thread_id)
        created = record.value["created_at"] if record else time.time()
        self._store.put(
            (user_id, THREADS_KIND),
            thread_id,
            {"consolidated": len(messages), "created_at": created},
        )
        return transcript

    # --- starting consolidation ------------------------------------------------------------

    def start(self, user_id: str, thread_id: str) -> None:
        """Consolidate the thread's unconsolidated messages in the background."""
        transcript = self._take_segment(user_id, thread_id)
        if transcript:
            run_id = f"consolidate_{thread_id}_{uuid.uuid4().hex[:6]}"
            self._store.put(
                (user_id, REVIEWS_KIND),
                run_id,
                {"source_thread": thread_id, "created_at": time.time()},
            )
            self._submit(user_id, run_id, {"transcript": transcript})

    def start_if_long(self, user_id: str, thread_id: str) -> bool:
        """Start a mid-conversation consolidation once the unconsolidated part is long."""
        messages = self._messages(thread_id)
        pending = format_transcript(messages[self._watermark(user_id, thread_id) :])
        if len(pending) < self._long_thread_chars:
            return False
        self.start(user_id, thread_id)
        return True

    def queue(self, user_id: str, thread_id: str) -> None:
        """On exit: remember the thread still needs consolidating; ``resume`` starts it next time."""
        if format_transcript(
            self._messages(thread_id)[self._watermark(user_id, thread_id) :],
        ):
            key = f"queued_{thread_id}"
            self._store.put(
                (user_id, REVIEWS_KIND),
                key,
                {"queued_thread": thread_id, "created_at": time.time()},
            )

    def _submit(
        self,
        user_id: str,
        run_id: str,
        payload: dict[str, Any] | None,
    ) -> None:
        self._running[run_id] = self._executor.submit(
            self._consolidator.invoke,
            payload,
            _config(run_id),
            context=UserContext(user_id=user_id),
        )

    def resume(self, user_id: str) -> None:
        """After a restart: start queued threads and continue runs that stopped mid-way."""
        for item in self._store.search((user_id, REVIEWS_KIND), limit=1000):
            if item.key in self._running:
                continue
            if "queued_thread" in item.value:
                self._store.delete((user_id, REVIEWS_KIND), item.key)
                self.start(user_id, item.value["queued_thread"])
                continue
            snapshot = self._consolidator.get_state(_config(item.key))
            if "edits" in snapshot.values:
                continue  # finished; review() presents it
            if snapshot.next:
                self._submit(
                    user_id,
                    item.key,
                    None,
                )  # continue from the last checkpoint
            else:
                self._store.delete(
                    (user_id, REVIEWS_KIND),
                    item.key,
                )  # nothing was recorded

    # --- review --------------------------------------------------------------------------

    def review(self, user_id: str) -> None:
        """Show every finished proposal of ``user_id`` and ask for the changes that need approval."""
        for item in self._store.search((user_id, REVIEWS_KIND), limit=1000):
            run_id = item.key
            future = self._running.get(run_id)
            if "queued_thread" in item.value or (
                future is not None and not future.done()
            ):
                continue
            if future is not None:
                self._running.pop(run_id)
                if (error := future.exception()) is not None:
                    print(
                        f"\n[Memory] Could not review a conversation ({error}); memory is unchanged.",
                    )
                    self._store.delete((user_id, REVIEWS_KIND), run_id)
                    continue
            values = self._consolidator.get_state(_config(run_id)).values
            if "edits" not in values:
                continue  # not finished; resume() continues it
            self._present(
                user_id,
                run_id,
                [MemoryEdit.model_validate(edit) for edit in values["edits"]],
            )
            self._store.delete((user_id, REVIEWS_KIND), run_id)
            if self._consolidator.checkpointer:
                # The run's checkpoints hold a copy of the transcript; drop them once reviewed.
                self._consolidator.checkpointer.delete_thread(run_id)

    def _present(self, user_id: str, run_id: str, edits: list[MemoryEdit]) -> None:
        if not edits:
            return
        snapshot = self._consolidator.get_state(_config(run_id))
        if snapshot.next and not any(task.interrupts for task in snapshot.tasks):
            # Stopped between edits (the app exited mid-way): apply the rest first.
            self._consolidator.invoke(
                None,
                _config(run_id),
                context=UserContext(user_id=user_id),
            )
        print("\n[Memory] From an earlier conversation:")
        for edit in edits:
            print(f"  - {edit.describe()}  ({edit.reason})")
        values = resume_pending_with_hitl(
            self._consolidator,
            _config(run_id),
            context=UserContext(user_id=user_id),
            assistant_prompt="Save this memory change? [y/n]: ",
        )
        for outcome in values.get("outcomes", []):
            print(f"[Memory] {outcome}")

    def close(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)


# --- history, undo, forget -------------------------------------------------------------------


def memory_history(store: BaseStore, user_id: str) -> list[Any]:
    """Saved previous versions of the user's memory files, newest first."""
    items = store.search((user_id, HISTORY_KIND), limit=1000)
    return sorted(items, key=lambda item: item.value["saved_at"], reverse=True)


def undo_last_change(store: BaseStore, user_id: str) -> str | None:
    """Restore the most recently replaced version of a memory file; returns its path.

    The user's own command, so it writes the store directly instead of passing the gate, which
    governs what models write.
    """
    history = memory_history(store, user_id)
    if not history:
        return None
    latest = history[0]
    key = latest.key.rsplit("@", 1)[0]
    store.put(
        (user_id, MEMORIES_NAMESPACE_KIND),
        key,
        {"content": latest.value["content"], "encoding": "utf-8"},
    )
    store.delete((user_id, HISTORY_KIND), latest.key)
    return latest.value["path"]


def forget_user(
    store: BaseStore,
    checkpointer: BaseCheckpointSaver,
    user_id: str,
) -> int:
    """Delete everything kept about ``user_id``: memory, history, bookkeeping, and conversations.

    ``checkpointer`` must hold both the assistant's and the consolidator's threads (the app
    gives both graphs the same one). Returns how many conversation threads were deleted.
    """
    threads = [item.key for item in store.search((user_id, THREADS_KIND), limit=10_000)]
    runs = [item.key for item in store.search((user_id, REVIEWS_KIND), limit=10_000)]
    for thread_id in threads + runs:
        checkpointer.delete_thread(thread_id)
    for namespace in store.list_namespaces(prefix=(user_id,)):
        for item in store.search(namespace, limit=10_000):
            store.delete(namespace, item.key)
    return len(threads)
