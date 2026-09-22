"""CLI for the P5 personal assistant: ``lab-assistant``.

Commands: ``/memory`` (preview the active user's stored memories), ``/more`` (show them in
full), ``/history`` (previous versions of changed memories), ``/undo`` (restore the latest
one), ``/forget`` (delete everything kept about the active user), ``/skills`` (list skills),
``/new_thread`` (same user, fresh conversation), ``/user <id>`` (switch user; memories are
isolated per user), ``/help``, ``quit``.

Memory, conversations, and pending reviews are durable (SQLite under ``out/state/``), and the
app resumes the last user and thread. When a conversation ends (``/new_thread``, ``/user``,
``quit``) or grows long, the memory consolidator reviews it in the background; its proposal is
shown before the user's next message, and changes that need approval are asked then.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import langsmith
import yaml
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.store.base import BaseStore

from agentlab.agents.personal_assistant_agent import make_personal_assistant_agent
from agentlab.configs.personal_assistant_config import (
    ASSISTANT_CHECKPOINT_DB_PATH,
    ASSISTANT_STORE_DB_PATH,
    DEFAULT_ASSISTANT_PROVIDER,
    DEFAULT_ASSISTANT_THREAD_ID,
    DEFAULT_ASSISTANT_TIER,
    DEFAULT_USER_ID,
    LONG_THREAD_CONSOLIDATION_CHARS,
    SKILLS_DIR,
)
from agentlab.data.sqlite_db_data import get_sqlite_checkpointer, get_sqlite_store
from agentlab.graphs.memory_consolidation_graph import make_memory_consolidation_graph
from agentlab.models import llm_model
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.utils.console_util import configure_utf8_stdout
from agentlab.utils.get_text_util import get_text
from agentlab.utils.memory_backend_util import MEMORIES_NAMESPACE_KIND
from agentlab.utils.memory_session_util import (
    MemorySessions,
    forget_user,
    memory_history,
    undo_last_change,
)
from agentlab.utils.run_with_hitl_util import stream_with_hitl
from agentlab.utils.secret_redaction_util import (
    make_trace_masking_client,
    redact_secrets,
)

_HELP = """Commands:
  /memory      preview stored memories for the active user
  /more        show stored memories in full
  /history     list previous versions of changed memories
  /undo        restore the most recent previous version
  /forget      delete everything kept about the active user
  /skills      list available procedural skills
  /new_thread  start a new conversation thread for the same user
  /user <id>   switch the active user (starts a new thread)
  /help        show this help
  quit         end the session"""
_PREVIEW_LINES = 10
_SESSION_NAMESPACE = ("app", "personal_assistant")


def _new_thread_id() -> str:
    return f"thread_{uuid.uuid4().hex[:6]}"


def load_session(store: BaseStore) -> tuple[str, str]:
    """The last active user and thread, or the defaults on first run."""
    item = store.get(_SESSION_NAMESPACE, "last")
    if item is None:
        return DEFAULT_USER_ID, DEFAULT_ASSISTANT_THREAD_ID
    return item.value["user_id"], item.value["thread_id"]


def save_session(store: BaseStore, user_id: str, thread_id: str) -> None:
    store.put(_SESSION_NAMESPACE, "last", {"user_id": user_id, "thread_id": thread_id})


def _read_frontmatter(skill_file: Path) -> dict[str, Any]:
    """Parse a SKILL.md YAML frontmatter block (``---`` delimited)."""
    text = skill_file.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    _, block, _ = text.split("---", 2)
    data = yaml.safe_load(block)
    return data if isinstance(data, dict) else {}


def sanitize_user_input(text: str) -> str:
    """Redact secrets from what the user typed, before anything records it.

    The graph checkpoints its input and the tracer sees it before any middleware runs, so
    this is the last point where a secret can be kept out of state, traces, and the model.
    """
    redacted, found = redact_secrets(text)
    if found:
        print(f"[Privacy] Removed {found} secret(s) before sending; secrets are never stored.")
    return redacted


def print_user_memories(store: BaseStore, user_id: str, *, max_lines: int | None = _PREVIEW_LINES) -> None:
    """Print the files stored in ``user_id``'s memory namespace.

    Args:
        store: The long-term memory store.
        user_id: Whose namespace to print.
        max_lines: Lines shown per file; ``None`` prints every line.
    """
    items = store.search((user_id, MEMORIES_NAMESPACE_KIND))
    if not items:
        print(f"  [Memory] No stored memories for user '{user_id}'.")
        return
    print(f"\n--- Stored memories for '{user_id}' ({len(items)} file(s)) ---")
    for item in items:
        value = item.value
        content = value.get("content", value) if isinstance(value, dict) else value
        if isinstance(content, list):  # file content stored as a list of lines
            content = "\n".join(str(line) for line in content)
        lines = str(content).strip().splitlines()
        shown = lines if max_lines is None else lines[:max_lines]
        print(f"\n* {item.key}")
        for line in shown:
            print(f"    {line}")
        if len(shown) < len(lines):
            print(f"    ... [{len(lines) - len(shown)} more lines, /more shows everything]")


def print_history(store: BaseStore, user_id: str, *, limit: int = 10) -> None:
    """Print the most recent previous versions of the user's memory files."""
    history = memory_history(store, user_id)
    if not history:
        print(f"  [Memory] No previous versions for user '{user_id}'.")
        return
    print(f"\n--- Previous versions for '{user_id}' (newest first; /undo restores the first) ---")
    for item in history[:limit]:
        saved = datetime.fromtimestamp(item.value["saved_at"]).astimezone().strftime("%Y-%m-%d %H:%M:%S")
        print(f"* {saved}  {item.value['path']}")


def print_available_skills(skills_dir: Path = SKILLS_DIR) -> None:
    """Print the name and description of each packaged skill."""
    skill_files = sorted(skills_dir.glob("*/SKILL.md"))
    if not skill_files:
        print(f"  [Skills] No skills found under {skills_dir}")
        return
    print(f"\n--- Available skills ({len(skill_files)}) ---")
    for skill_file in skill_files:
        meta = _read_frontmatter(skill_file)
        print(f"* {meta.get('name', skill_file.parent.name)}: {meta.get('description', 'no description')}")


def main() -> None:
    """Run the assistant REPL."""
    load_dotenv()
    configure_utf8_stdout()
    langsmith.configure(client=make_trace_masking_client())

    store = get_sqlite_store(ASSISTANT_STORE_DB_PATH)
    checkpointer = get_sqlite_checkpointer(ASSISTANT_CHECKPOINT_DB_PATH)
    agent = make_personal_assistant_agent(store, checkpointer=checkpointer)
    consolidator = make_memory_consolidation_graph(store, checkpointer=checkpointer)
    sessions = MemorySessions(store, agent, consolidator, long_thread_chars=LONG_THREAD_CONSOLIDATION_CHARS)
    user_id, thread_id = load_session(store)
    spec = llm_model.spec(DEFAULT_ASSISTANT_TIER, DEFAULT_ASSISTANT_PROVIDER)

    print("=" * 65)
    print("[Personal Assistant] P5 Memory-Rich Assistant")
    print(f"Model: {spec.model} (tier {llm_model.resolve_tier(DEFAULT_ASSISTANT_TIER)})")
    print(f"Memory and conversations: SQLite under {ASSISTANT_STORE_DB_PATH.parent}")
    print("Memory updates: proposed after each conversation, saved with your OK (/undo reverts)")
    print("Privacy: secrets are removed before sending; traces mask secrets and emails")
    print(f"Resumed: user '{user_id}' on thread '{thread_id}' (/new_thread for a fresh one)")
    print(_HELP)
    print("=" * 65)
    sessions.resume(user_id)

    def switch(new_user: str, new_thread: str) -> None:
        nonlocal user_id, thread_id
        user_id, thread_id = new_user, new_thread
        save_session(store, user_id, thread_id)
        sessions.resume(user_id)

    while True:
        sessions.review(user_id)
        try:
            prompt = input(f"\n[{user_id}@{thread_id}]> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting session.")
            break
        if not prompt:
            continue

        command = prompt.lower()
        if command in {"quit", "exit", "q"}:
            break
        if command == "/help":
            print(_HELP)
            continue
        if command == "/memory":
            print_user_memories(store, user_id)
            continue
        if command == "/more":
            print_user_memories(store, user_id, max_lines=None)
            continue
        if command == "/history":
            print_history(store, user_id)
            continue
        if command == "/undo":
            restored = undo_last_change(store, user_id)
            print(f"[Memory] Restored the previous version of {restored}." if restored else "[Memory] Nothing to undo.")
            continue
        if command == "/forget":
            answer = input(f"Delete ALL memory and conversations of '{user_id}'? Type the user id to confirm: ")
            if answer.strip() != user_id:
                print("[Memory] Cancelled; nothing was deleted.")
                continue
            deleted = forget_user(store, checkpointer, user_id)
            print(f"[Memory] Forgot '{user_id}': memory, history, and {deleted} conversation(s) deleted.")
            switch(user_id, _new_thread_id())
            continue
        if command == "/skills":
            print_available_skills()
            continue
        if command == "/new_thread":
            sessions.start(user_id, thread_id)
            switch(user_id, _new_thread_id())
            print(f"[Thread] Now on '{thread_id}': conversation state is fresh, memories persist.")
            continue
        if command.startswith("/user"):
            new_user = prompt[len("/user") :].strip()
            if not new_user:
                print("Usage: /user <user_id>")
                continue
            sessions.start(user_id, thread_id)
            switch(new_user, _new_thread_id())
            print(f"[User] Active user is now '{user_id}' on thread '{thread_id}'.")
            continue

        sessions.track(user_id, thread_id)
        save_session(store, user_id, thread_id)
        result = stream_with_hitl(
            agent,
            {"messages": [HumanMessage(content=sanitize_user_input(prompt))]},
            {"configurable": {"thread_id": thread_id}},
            context=UserContext(user_id=user_id),
        )
        if result["last_message"]:
            print(f"\nAssistant: {get_text(result['last_message'])}")
        if sessions.start_if_long(user_id, thread_id):
            print("[Memory] This conversation is getting long; reviewing it so far in the background.")

    sessions.queue(user_id, thread_id)
    sessions.close()


if __name__ == "__main__":
    main()
