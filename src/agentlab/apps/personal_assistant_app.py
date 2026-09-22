"""CLI for the P5 personal assistant: ``lab-assistant``.

Commands: ``/memory`` (preview the active user's stored memories), ``/more`` (show them in
full), ``/skills`` (list packaged skills), ``/new_thread`` (same user, fresh conversation),
``/user <id>`` (switch user; memories are isolated per user), ``/help``, ``quit``.

When a conversation ends (``/new_thread`` or ``/user``), the memory consolidator reviews it in the
background. Its proposal waits until the user types their next message, is shown first, and
changes that need approval are asked then.
"""

import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import Any

import langsmith
import yaml
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore

from agentlab.agents.personal_assistant_agent import make_personal_assistant_agent
from agentlab.configs.personal_assistant_config import (
    DEFAULT_ASSISTANT_PROVIDER,
    DEFAULT_ASSISTANT_THREAD_ID,
    DEFAULT_ASSISTANT_TIER,
    DEFAULT_USER_ID,
    SKILLS_DIR,
)
from agentlab.graphs.memory_consolidation_graph import make_memory_consolidation_graph
from agentlab.models import llm_model
from agentlab.nodes.memory_consolidation_node import format_transcript
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.schemas.output.memory_consolidation_output_schema import MemoryEdit
from agentlab.utils.console_util import configure_utf8_stdout
from agentlab.utils.get_text_util import get_text
from agentlab.utils.memory_backend_util import MEMORIES_NAMESPACE_KIND
from agentlab.utils.run_with_hitl_util import resume_pending_with_hitl, stream_with_hitl
from agentlab.utils.secret_redaction_util import (
    make_trace_masking_client,
    redact_secrets,
)

_HELP = """Commands:
  /memory      preview stored memories for the active user
  /more        show stored memories in full
  /skills      list available procedural skills
  /new_thread  start a new conversation thread for the same user
  /user <id>   switch the active user (starts a new thread)
  /help        show this help
  quit         end the session"""
_PREVIEW_LINES = 10


class BackgroundConsolidation:
    """Consolidate each finished conversation in the background; the user reviews it later.

    ``start`` never blocks the chat. ``review`` runs in the main loop before the user's next
    message: it shows what a finished run proposed and asks for the changes that need approval.
    """

    def __init__(self, assistant: CompiledStateGraph, consolidator: CompiledStateGraph) -> None:
        self._assistant = assistant
        self._consolidator = consolidator
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="memory-consolidation")
        self._jobs: list[tuple[str, dict[str, Any], Future]] = []

    def start(self, user_id: str, thread_id: str) -> None:
        state = self._assistant.get_state({"configurable": {"thread_id": thread_id}})
        transcript = format_transcript(state.values.get("messages", []))
        if not transcript:
            return
        config = {"configurable": {"thread_id": f"consolidate_{thread_id}_{uuid.uuid4().hex[:6]}"}}
        future = self._executor.submit(
            self._consolidator.invoke, {"transcript": transcript}, config, context=UserContext(user_id=user_id)
        )
        self._jobs.append((user_id, config, future))

    def review(self, user_id: str) -> None:
        for job in [job for job in self._jobs if job[0] == user_id and job[2].done()]:
            self._jobs.remove(job)
            _, config, future = job
            if (error := future.exception()) is not None:
                print(f"\n[Memory] Could not review the last conversation ({error}); memory is unchanged.")
                continue
            edits = [MemoryEdit.model_validate(edit) for edit in self._consolidator.get_state(config).values["edits"]]
            if not edits:
                continue
            print("\n[Memory] From your last conversation:")
            for edit in edits:
                print(f"  - {edit.describe()}  ({edit.reason})")
            values = resume_pending_with_hitl(
                self._consolidator,
                config,
                context=UserContext(user_id=user_id),
                assistant_prompt="Save this memory change? [y/n]: ",
            )
            for outcome in values.get("outcomes", []):
                print(f"[Memory] {outcome}")

    def close(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)


def _new_thread_id() -> str:
    return f"thread_{uuid.uuid4().hex[:6]}"


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

    store = InMemoryStore()
    agent = make_personal_assistant_agent(store)
    consolidation = BackgroundConsolidation(agent, make_memory_consolidation_graph(store))
    user_id, thread_id = DEFAULT_USER_ID, DEFAULT_ASSISTANT_THREAD_ID
    spec = llm_model.spec(DEFAULT_ASSISTANT_TIER, DEFAULT_ASSISTANT_PROVIDER)

    print("=" * 65)
    print("[Personal Assistant] P5 Memory-Rich Assistant")
    print(f"Model: {spec.model} (tier {llm_model.resolve_tier(DEFAULT_ASSISTANT_TIER)})")
    print("Memory store: in-memory (cleared when this process exits)")
    print("Memory updates: proposed after each conversation (/new_thread, /user), saved with your OK")
    print("Privacy: secrets are removed before sending; traces mask secrets and emails")
    print(_HELP)
    print("=" * 65)

    while True:
        consolidation.review(user_id)
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
        if command == "/skills":
            print_available_skills()
            continue
        if command == "/new_thread":
            consolidation.start(user_id, thread_id)
            thread_id = _new_thread_id()
            print(f"[Thread] Now on '{thread_id}': conversation state is fresh, memories persist.")
            continue
        if command.startswith("/user"):
            new_user = prompt[len("/user") :].strip()
            if not new_user:
                print("Usage: /user <user_id>")
                continue
            consolidation.start(user_id, thread_id)
            user_id, thread_id = new_user, _new_thread_id()
            print(f"[User] Active user is now '{user_id}' on thread '{thread_id}'.")
            continue

        result = stream_with_hitl(
            agent,
            {"messages": [HumanMessage(content=sanitize_user_input(prompt))]},
            {"configurable": {"thread_id": thread_id}},
            context=UserContext(user_id=user_id),
        )
        if result["last_message"]:
            print(f"\nAssistant: {get_text(result['last_message'])}")

    consolidation.close()


if __name__ == "__main__":
    main()
