"""CLI for the P5 personal assistant: ``lab-assistant``.

Commands: ``/memory`` (show the active user's stored memories), ``/skills``
(list packaged skills), ``/new_thread`` (same user, fresh conversation),
``/user <id>`` (switch user; memories are isolated per user), ``/help``, ``quit``.
"""

import uuid
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
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
from agentlab.models import llm_model
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.utils.console_util import configure_utf8_stdout
from agentlab.utils.get_text_util import get_text
from agentlab.utils.memory_backend_util import MEMORIES_NAMESPACE_KIND
from agentlab.utils.run_with_hitl_util import stream_with_hitl

_HELP = """Commands:
  /memory      show stored memories for the active user
  /skills      list available procedural skills
  /new_thread  start a new conversation thread for the same user
  /user <id>   switch the active user (starts a new thread)
  /help        show this help
  quit         end the session"""
_PREVIEW_LINES = 10


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


def print_user_memories(store: BaseStore, user_id: str) -> None:
    """Print the files stored in ``user_id``'s memory namespace."""
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
        print(f"\n* {item.key}")
        for line in lines[:_PREVIEW_LINES]:
            print(f"    {line}")
        if len(lines) > _PREVIEW_LINES:
            print(f"    ... [{len(lines) - _PREVIEW_LINES} more lines]")


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

    store = InMemoryStore()
    agent = make_personal_assistant_agent(store)
    user_id, thread_id = DEFAULT_USER_ID, DEFAULT_ASSISTANT_THREAD_ID
    spec = llm_model.spec(DEFAULT_ASSISTANT_TIER, DEFAULT_ASSISTANT_PROVIDER)

    print("=" * 65)
    print("[Personal Assistant] P5 Memory-Rich Assistant")
    print(f"Model: {spec.model} (tier {llm_model.resolve_tier(DEFAULT_ASSISTANT_TIER)})")
    print("Memory store: in-memory (cleared when this process exits)")
    print(_HELP)
    print("=" * 65)

    while True:
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
        if command == "/skills":
            print_available_skills()
            continue
        if command == "/new_thread":
            thread_id = _new_thread_id()
            print(f"[Thread] Now on '{thread_id}': conversation state is fresh, memories persist.")
            continue
        if command.startswith("/user"):
            new_user = prompt[len("/user") :].strip()
            if not new_user:
                print("Usage: /user <user_id>")
                continue
            user_id, thread_id = new_user, _new_thread_id()
            print(f"[User] Active user is now '{user_id}' on thread '{thread_id}'.")
            continue

        result = stream_with_hitl(
            agent,
            {"messages": [HumanMessage(content=prompt)]},
            {"configurable": {"thread_id": thread_id}},
            context=UserContext(user_id=user_id),
            assistant_prompt="Allow this memory change? [y/n]: ",
        )
        if result["last_message"]:
            print(f"\nAssistant: {get_text(result['last_message'])}")


if __name__ == "__main__":
    main()
