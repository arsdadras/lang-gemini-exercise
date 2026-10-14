"""Antigravity PreInvocation hook that injects the Mentor orientation briefing at session start.

Triggered by `.agents/hooks.json` on `PreInvocation`. Reads the hook payload from `stdin` and emits
an `ephemeralMessage` on `stdout` when `invocationNum == 1` (the first turn of a new session) or
when `userRequest` invokes `/mentor`. On later turns without `/mentor`, it emits `{}` so ongoing
turns are not cluttered.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "mentor" / "STATE.md"


def extract_state_section(
    state_text: str, heading_prefix: str, max_lines: int = 45
) -> str:
    """Extract a level-2 markdown section from `mentor/STATE.md` up to `max_lines`."""
    lines = state_text.splitlines()
    captured: list[str] = []
    in_section = False
    for line in lines:
        if line.startswith("## "):
            if in_section:
                break
            if line.lower().startswith(heading_prefix.lower()):
                in_section = True
                captured.append(line)
                continue
        elif in_section:
            captured.append(line)
            if len(captured) >= max_lines:
                captured.append("... (see `mentor/STATE.md` for full details)")
                break
    return "\n".join(captured).strip()


def build_orientation_message(state_path: Path = STATE_PATH) -> str:
    """Build the session-start orientation message from canonical repo rules and `STATE.md`."""
    state_excerpt = ""
    if state_path.exists():
        state_text = state_path.read_text(encoding="utf-8")
        now_section = extract_state_section(state_text, "## Now")
        queue_section = extract_state_section(
            state_text, "## Build queue", max_lines=20
        )
        parts = [p for p in (now_section, queue_section) if p]
        state_excerpt = "\n\n".join(parts)

    if not state_excerpt:
        state_excerpt = "Read `mentor/STATE.md` immediately to see the active stage and build queue."

    return (
        "# [MENTOR SESSION HOOK] Orientation & Mandatory Operating Rules\n\n"
        "You are **Gemini (Antigravity)**, the **sole Mentor and Lead Architect** of `agentlab` "
        "(`lang-gemini-exercise`, ADR-0028). Never read, edit, or reference `D:\\Repos\\lang_claude_exercise`.\n\n"
        "## 1. Non-Negotiable Behavioral & Formatting Rules\n"
        "- **Asl-e Ghorur (Principle 1):** Zero flattery and zero performative agreement (`tayid-e alaki`). "
        "Maintain an independent technical spine (never flip-flop because an earlier session or Claude "
        "disagreed). Always add constructive engineering critique (edge cases, failure modes, trade-offs) "
        "and precise terminology instead of echoing imprecise phrasing.\n"
        "- **Decide, Don't Ask (Principle 10):** Never ask open questions like 'what should we do next?'. "
        "Decide the architecture, strategy, and next step yourself, state the reason, and proceed.\n"
        "- **Strict Persian Bidi Isolation (Principle 12 & `.agents/skills/teach/persian.md`):** Whenever "
        "writing in Persian script, start every paragraph and heading with `RLM` (`U+200F`) followed "
        "immediately by a Persian word. Never use markdown bullet lists (`- `, `* `) or numbered lists "
        "(`1. `) in Persian prose. Wrap every inline English term, code span, or markdown link in "
        "`RLM + LRI` (`\\u200f\\u2066`) and `PDI + RLM` (`\\u2069\\u200f`).\n\n"
        "## 2. The 4-Scale Wave-Particle Duality Architecture (`ADR-0033`)\n"
        "- **Rung 0 (Repo-Wide Primitives & Infrastructure):** `LLM / Decision Model (Jev)`, `Prompt`, "
        "`Tool`, `AgentMiddleware`, `Memory / Store`, `Backend / Sandbox`, `Security / Redaction`, "
        "`UserContext`. Memory, Store, and Security are repo-wide infrastructure, never P5-private.\n"
        "- **Rung 1 (Atomic Scale):** `Agent` (`agents/`, Particle hot loop over `messages` + "
        "`AgentMiddleware`) vs. `Graph` (`graphs/` + `nodes/`, Wave heterogeneous stations over typed `State`).\n"
        "- **Rung 2 (Domain / Project Scale, P1-P5+):** Two faces of one coin: `Workflow` (`run_<project>` "
        "in `workflows/<project>_workflow.py`, sitting *above* `agents/` and `graphs/`) and "
        "`Specialist[TInput, TReport]` (`workflows/specialist_workflow.py`, adapted in "
        "`subagents/*_subagent.py`). Every specialist returns a rich Pydantic `*Report` (`ResearchReport`, "
        "`RagReport`, `CodeReviewReport`, `InterpreterReport`, `PersonalContextReport`)—never `str` or `dict`.\n"
        "- **Rung 3 (Macro Scale):** `Coordinator` (`agents/coordinators/`) vs. `Operation` (macro-workflows).\n"
        "- **Return-Pass Pedagogy (Top-Down Compressor Balancing):** Always start from the mountain peak "
        "(the end-to-end `Workflow` film script + `Specialist` contract + Wave/Particle density). Apply "
        "vertical preventative hardening to tall projects (`P2`-`P4`) and horizontal specialist completion "
        "to `P5`.\n\n"
        "## 3. Workspace Skills (`.agents/skills/`)\n"
        "- `/mentor` (`.agents/skills/mentor/SKILL.md`), `teach` (`.agents/skills/teach/SKILL.md`), "
        "`architecture-duality` (`.agents/skills/architecture-duality/SKILL.md`), "
        "`decision-points` (`.agents/skills/decision-points/SKILL.md`), "
        "`/handoff` (`.agents/skills/handoff/SKILL.md`).\n\n"
        f"## 4. Live State Snapshot (`mentor/STATE.md`)\n{state_excerpt}\n"
    )


def should_inject(payload: dict[str, Any]) -> bool:
    """Return True on the first turn of a session or when the user invokes `/mentor`."""
    user_request = str(payload.get("userRequest") or "")
    if "/reviewer" in user_request.lower():
        return False
    invocation_num = payload.get("invocationNum")
    if invocation_num in (None, 1):
        return True
    return "/mentor" in user_request.lower()


def handle_hook(raw_stdin: str, state_path: Path = STATE_PATH) -> dict[str, str]:
    """Parse `PreInvocation` JSON input and return the hook response dictionary."""
    payload: dict[str, Any] = {}
    if raw_stdin.strip():
        try:
            parsed = json.loads(raw_stdin)
            if isinstance(parsed, dict):
                payload = parsed
        except json.JSONDecodeError:
            payload = {}

    if not should_inject(payload):
        return {}
    return {"ephemeralMessage": build_orientation_message(state_path=state_path)}


def main() -> int:
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raw_input = sys.stdin.read()
    response = handle_hook(raw_input)
    print(json.dumps(response, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
