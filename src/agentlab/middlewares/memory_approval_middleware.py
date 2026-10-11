"""Memory write governance for the P5 assistant: one gate, inside the memory storage.

Every change under ``/memories/`` goes through ``GatedMemoryBackend``. The assistant and all of
its subagents share that storage, so no tool call or delegation can go around it. For each
write, edit, or delete it asks ``MemoryGate`` for one verdict, built in order:

1. code rules: overwriting a stored file, an edit that drops text, or deleting asks;
2. secret detectors: a secret in the new content blocks;
3. the security guard on the new content, which can only make the verdict stricter.

``allow`` stores the change, ``block`` refuses it with an error the model reads, and ``ask``
pauses the run with a standard HITL request (the shape ``HumanInTheLoopMiddleware`` sends, so
the CLI approval loop and HITL-aware UIs handle it unchanged).

On resume LangGraph runs the tool again from the start, so the gate is asked twice. The
guard's verdict is cached in the user's store: a model that changed its mind between pause and
resume could otherwise void the human's decision.

Before any change that replaces or removes text, the file's previous content is saved to the
user's history, so every change can be undone. That is also what lets a correction the user
explicitly asked for (``requested=True``) skip the approval: it stays recoverable.
"""

import hashlib
import json
import time
from typing import Any

from deepagents.backends import StoreBackend
from deepagents.backends.protocol import DeleteResult, EditResult, WriteResult
from langchain.agents.middleware.human_in_the_loop import (
    ActionRequest,
    DecisionType,
    HITLRequest,
    ReviewConfig,
)
from langgraph.store.base import BaseStore
from langgraph.types import interrupt

from agentlab.configs.personal_assistant_config import MEMORIES_ROUTE_PREFIX
from agentlab.middlewares.security_guard_middleware import SecurityGuard
from agentlab.schemas.output.middlewares_output_schema import GuardVerdict
from agentlab.utils.secret_redaction_util import redact_secrets

# The CLI approval loop offers approve or reject-with-reason; "edit" is in the backlog.
MEMORY_APPROVAL_DECISIONS: list[DecisionType] = ["approve", "reject"]
VERDICT_CACHE_KIND = "memory_verdicts"
HISTORY_KIND = "memory_history"
REJECTION_PREFIX = "The user rejected this memory change"

ALLOW = GuardVerdict(decision="allow", category="none", reason="Adds to memory.")
_OVERWRITE = GuardVerdict(
    decision="ask",
    category="destructive",
    reason="Overwrite a stored memory file (its current content is replaced).",
)
_DESTRUCTIVE_EDIT = GuardVerdict(
    decision="ask",
    category="destructive",
    reason="Change or remove text in stored memory.",
)
_DELETE = GuardVerdict(
    decision="ask",
    category="destructive",
    reason="Delete stored memory.",
)
_REQUESTED = GuardVerdict(
    decision="allow",
    category="requested",
    reason="A correction the user asked for; the previous version is kept.",
)
_SECRET = GuardVerdict(
    decision="block",
    category="credential",
    reason="The content contains a secret, and secrets are never stored.",
)
_STRICTNESS = {"allow": 0, "ask": 1, "block": 2}


def _keeps_every_line(old: str, new: str) -> bool:
    """Whether each line of ``old`` is still in ``new``, in the same order.

    New lines may be inserted anywhere in between. ``line in remaining`` advances the
    shared iterator past the match, so a later line can't match an earlier position.
    """
    remaining = iter(new.splitlines())
    return all(line in remaining for line in old.splitlines())


def _edit_removes_text(old: str, new: str) -> bool:
    """An edit is additive only when nothing it replaces is lost.

    That holds when the new text contains the old text whole (appending), or keeps
    every old line in order (inserting lines, e.g. a bullet in the middle of a section).
    """
    if not old:
        return True
    return not (old in new or _keeps_every_line(old, new))


def _stricter(code: GuardVerdict, guard: GuardVerdict) -> GuardVerdict:
    if code.decision == guard.decision == "ask":
        return GuardVerdict(
            decision="ask",
            category=guard.category,
            reason=f"{code.reason} {guard.reason}",
        )
    return max((code, guard), key=lambda verdict: _STRICTNESS[verdict.decision])


class MemoryGate:
    """The decision point: one verdict for each change under ``/memories/``."""

    def __init__(self, guard: SecurityGuard) -> None:
        self._guard = guard

    def write(
        self,
        path: str,
        content: str,
        *,
        exists: bool,
        store: BaseStore,
        user_id: str,
    ) -> GuardVerdict:
        if exists:
            return self._judge(
                _OVERWRITE,
                f"overwrite existing file {path}",
                content,
                store,
                user_id,
            )
        return self._judge(ALLOW, f"create new file {path}", content, store, user_id)

    def edit(
        self,
        path: str,
        old_string: str,
        new_string: str,
        *,
        store: BaseStore,
        user_id: str,
        requested: bool = False,
    ) -> GuardVerdict:
        """``requested``: the user explicitly asked for this change, so it needs no approval of its own."""
        if _edit_removes_text(old_string, new_string):
            code = _REQUESTED if requested else _DESTRUCTIVE_EDIT
            return self._judge(
                code,
                f"replace text in existing file {path}",
                new_string,
                store,
                user_id,
            )
        return self._judge(
            ALLOW,
            f"append to existing file {path}",
            new_string,
            store,
            user_id,
        )

    def delete(self) -> GuardVerdict:
        """A delete adds no content to judge, so the code rule alone decides."""
        return _DELETE

    def _judge(
        self,
        code: GuardVerdict,
        action: str,
        content: str,
        store: BaseStore,
        user_id: str,
    ) -> GuardVerdict:
        """Detectors first (a secret blocks outright), then the guard; the stricter verdict wins."""
        if redact_secrets(content)[1]:
            return _SECRET
        return _stricter(code, self._cached_guard(action, content, store, user_id))

    def _cached_guard(
        self,
        action: str,
        content: str,
        store: BaseStore,
        user_id: str,
    ) -> GuardVerdict:
        namespace = (user_id, VERDICT_CACHE_KIND)
        key = hashlib.sha256(json.dumps([action, content]).encode()).hexdigest()
        if (cached := store.get(namespace, key)) is not None:
            return GuardVerdict.model_validate(cached.value)
        verdict = self._guard(action, content)
        store.put(namespace, key, verdict.model_dump())
        return verdict


def _enforce(verdict: GuardVerdict, tool_name: str, args: dict[str, Any]) -> str | None:
    """Apply a verdict: ``None`` to go ahead, or the error message the model reads instead."""
    if verdict.decision == "allow":
        return None
    if verdict.decision == "block":
        return f"Blocked: {verdict.reason}"
    request = HITLRequest(
        action_requests=[
            ActionRequest(
                name=tool_name,
                args=args,
                description=f"{verdict.reason}\n\nTool: {tool_name}\nArgs: {args}",
            ),
        ],
        review_configs=[
            ReviewConfig(
                action_name=tool_name,
                allowed_decisions=MEMORY_APPROVAL_DECISIONS,
            ),
        ],
    )
    decision = interrupt(request)["decisions"][0]
    if decision["type"] == "approve":
        return None
    reason = decision.get("message")
    return f"{REJECTION_PREFIX}{f': {reason}' if reason else ''}. Do not retry it another way."


class GatedMemoryBackend(StoreBackend):
    """The enforcement point: ``/memories/`` storage that applies the gate's verdict.

    ``CompositeBackend`` strips the route prefix, so a key arrives as ``/user_profile.md``; the
    gate and the approval prompt see the full ``/memories/user_profile.md``. The user id comes
    from the namespace factory, which already refuses a call without user identity.
    """

    def __init__(self, gate: MemoryGate, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._gate = gate

    def _full_path(self, key: str) -> str:
        return MEMORIES_ROUTE_PREFIX.rstrip("/") + key

    def _save_previous(self, key: str) -> None:
        """Keep the file's current content in the user's history before it is replaced or removed."""
        store, namespace = self._get_store(), self._get_namespace()
        if (stored := store.get(namespace, key)) is None:
            return
        content = self._convert_store_item_to_file_data(stored)["content"]
        entry = {
            "path": self._full_path(key),
            "content": content,
            "saved_at": time.time(),
        }
        store.put((namespace[0], HISTORY_KIND), f"{key}@{time.time_ns()}", entry)

    def _check_write(self, key: str, content: str) -> str | None:
        store, namespace, path = (
            self._get_store(),
            self._get_namespace(),
            self._full_path(key),
        )
        exists = store.get(namespace, key) is not None
        verdict = self._gate.write(
            path,
            content,
            exists=exists,
            store=store,
            user_id=namespace[0],
        )
        return _enforce(verdict, "write_file", {"file_path": path, "content": content})

    def _check_edit(
        self,
        key: str,
        old_string: str,
        new_string: str,
        requested: bool = False,
    ) -> str | None:
        store, namespace, path = (
            self._get_store(),
            self._get_namespace(),
            self._full_path(key),
        )
        verdict = self._gate.edit(
            path,
            old_string,
            new_string,
            store=store,
            user_id=namespace[0],
            requested=requested,
        )
        return _enforce(
            verdict,
            "edit_file",
            {"file_path": path, "old_string": old_string, "new_string": new_string},
        )

    def _check_delete(self, key: str) -> str | None:
        return _enforce(
            self._gate.delete(),
            "delete",
            {"file_path": self._full_path(key)},
        )

    def write(self, file_path: str, content: str) -> WriteResult:
        if refusal := self._check_write(file_path, content):
            return WriteResult(error=refusal)
        self._save_previous(file_path)
        return super().write(file_path, content)

    async def awrite(self, file_path: str, content: str) -> WriteResult:
        if refusal := self._check_write(file_path, content):
            return WriteResult(error=refusal)
        self._save_previous(file_path)
        return await super().awrite(file_path, content)

    def edit(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,
        *,
        requested: bool = False,
    ) -> EditResult:
        """``requested`` is for callers that know the user asked for this change (the consolidator)."""
        if refusal := self._check_edit(file_path, old_string, new_string, requested):
            return EditResult(error=refusal)
        if _edit_removes_text(old_string, new_string):
            self._save_previous(file_path)
        return super().edit(file_path, old_string, new_string, replace_all)

    async def aedit(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,
    ) -> EditResult:
        if refusal := self._check_edit(file_path, old_string, new_string):
            return EditResult(error=refusal)
        if _edit_removes_text(old_string, new_string):
            self._save_previous(file_path)
        return await super().aedit(file_path, old_string, new_string, replace_all)

    def delete(self, file_path: str) -> DeleteResult:
        if refusal := self._check_delete(file_path):
            return DeleteResult(error=refusal)
        self._save_previous(file_path)
        return super().delete(file_path)

    async def adelete(self, file_path: str) -> DeleteResult:
        if refusal := self._check_delete(file_path):
            return DeleteResult(error=refusal)
        self._save_previous(file_path)
        return await super().adelete(file_path)
