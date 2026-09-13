"""Application entry point — interactive REPL loop for the P5 Personal Assistant agent."""

from dotenv import load_dotenv

load_dotenv()

import contextlib
import io
import sys
import uuid

from langchain_core.messages import HumanMessage

from agents.personal_assistant_agent import personal_assistant_agent
from configs.models_config import MODEL_TIERS
from configs.personal_assistant_config import (
    DEFAULT_ASSISTANT_PROVIDER,
    DEFAULT_ASSISTANT_THREAD_ID,
    DEFAULT_ASSISTANT_TIER,
    DEFAULT_USER_ID,
)
from utils.get_text_util import get_text
from utils.streaming_util import stream_agent_with_observability


def print_user_memories(agent, user_id: str) -> None:
    """Print all memory files stored under the user's namespace in BaseStore."""
    store = getattr(agent, "store", None)
    if store is None:
        print("  [Notice] Backing store is not available for inspection.")
        return

    items = store.search((user_id, "memories"))
    if not items:
        print(f"  [Memory] No stored memories found for user: '{user_id}'")
        return

    print(f"\n--- Stored Memories for user: '{user_id}' ({len(items)} file(s)) ---")
    for item in items:
        print(f"\n* File: {item.key}")
        content = ""
        if isinstance(item.value, dict):
            content = item.value.get("content", str(item.value))
        else:
            content = str(item.value)
        lines = content.strip().splitlines()
        for line in lines[:10]:
            print(f"    {line}")
        if len(lines) > 10:
            print(f"    ... [{len(lines) - 10} more lines]")
    print("---------------------------------------------------------------")


def print_available_skills(agent) -> None:
    """Print all procedural skills discovered via agent backend."""
    backend = getattr(agent, "backend", None)
    if backend is None:
        print("  [Notice] Agent backend is not available for inspection.")
        return

    ls_result = backend.ls("/skills/")
    entries = ls_result.entries if hasattr(ls_result, "entries") else (ls_result if isinstance(ls_result, list) else [])
    skill_dirs = [e for e in entries if e.get("is_dir")]
    if not skill_dirs:
        print("  [Skills] No procedural skills found under /skills/")
        return

    print(f"\n--- Available Procedural Skills ({len(skill_dirs)} skill(s)) ---")
    for entry in skill_dirs:
        skill_path = entry.get("path", "")
        md_path = f"{skill_path.rstrip('/')}/SKILL.md"
        res = backend.read(md_path)
        content = res.file_data.get("content", "") if hasattr(res, "file_data") and res.file_data else ""
        desc = "No description available"
        if "description:" in content:
            for line in content.splitlines():
                if line.startswith("description:"):
                    desc = line.split(":", 1)[1].strip()
                    break
        name = skill_path.strip("/").split("/")[-1]
        print(f"* Skill: {name}")
        print(f"  Path: {md_path}")
        print(f"  Summary: {desc}")
    print("---------------------------------------------------------------")


def main() -> None:
    """Launch the interactive REPL session for the P5 Personal Assistant agent."""
    if hasattr(sys.stdout, "reconfigure"):
        with contextlib.suppress(AttributeError, io.UnsupportedOperation):
            sys.stdout.reconfigure(encoding="utf-8")

    agent = personal_assistant_agent
    active_user_id = DEFAULT_USER_ID
    active_thread_id = DEFAULT_ASSISTANT_THREAD_ID

    tier_info = MODEL_TIERS.get(DEFAULT_ASSISTANT_TIER, {})
    provider = DEFAULT_ASSISTANT_PROVIDER or next(iter(tier_info.keys()), "default")
    model_id = tier_info.get(provider, {}).get("model", DEFAULT_ASSISTANT_TIER)
    print("=" * 65)
    print("[Personal Assistant] P5 Memory-Rich Assistant (DeepAgents)")
    print(f"Model Tier: {DEFAULT_ASSISTANT_TIER} [{provider}] ({model_id})")
    print(f"Active User ID: {active_user_id}")
    print(f"Active Thread ID: {active_thread_id}")
    print("\nREPL Special Commands:")
    print("  /memory           - Inspect stored memory files for active user")
    print("  /skills           - Inspect available procedural skills on disk")
    print("  /new_thread       - Switch to a new thread (test cross-thread recall)")
    print("  /user <id>        - Switch active user (test tenant isolation)")
    print("  /help             - Show this help banner")
    print("  quit / exit / q   - End session")
    print("=" * 65)

    while True:
        config = {
            "configurable": {
                "thread_id": active_thread_id,
                "user_id": active_user_id,
            }
        }

        try:
            prompt_header = f"\n[{active_user_id}@{active_thread_id}]> "
            user_prompt = input(prompt_header).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting session.")
            break

        if not user_prompt:
            continue

        # Command handling
        cmd_lower = user_prompt.lower()
        if cmd_lower in {"quit", "exit", "q"}:
            print("Session ended.")
            break

        if cmd_lower == "/help":
            print("\nCommands:")
            print("  /memory     : Inspect active user's persistent store files")
            print("  /skills     : Inspect available procedural skills on disk")
            print("  /new_thread : Start a new thread for the same user")
            print("  /user <id>  : Switch active user ID")
            continue

        if cmd_lower == "/memory":
            print_user_memories(agent, active_user_id)
            continue

        if cmd_lower == "/skills":
            print_available_skills(agent)
            continue

        if cmd_lower == "/new_thread":
            active_thread_id = f"thread_{uuid.uuid4().hex[:6]}"
            print(f"\n[Session Switched] Active thread is now: '{active_thread_id}'")
            print("Note: Ephemeral state is cleared, but persistent memory is preserved.")
            continue

        if user_prompt.startswith("/user "):
            parts = user_prompt.split(maxsplit=1)
            if len(parts) == 2 and parts[1].strip():
                active_user_id = parts[1].strip()
                active_thread_id = f"thread_{uuid.uuid4().hex[:6]}"
                print(f"\n[User Switched] Active user is now: '{active_user_id}'")
                print(f"Spawned new thread: '{active_thread_id}'")
            else:
                print("Usage: /user <user_id>")
            continue

        # Invoke agent with streaming observability
        result = stream_agent_with_observability(
            agent,
            {"messages": [HumanMessage(content=user_prompt)]},
            config=config,
        )

        last_msg = result.get("last_message")
        if last_msg:
            print(f"\nAssistant: {get_text(last_msg)}")


if __name__ == "__main__":
    main()
