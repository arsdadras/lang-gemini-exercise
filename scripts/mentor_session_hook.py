"""Antigravity PreInvocation hook that injects Mentor or Consultant briefings.

Triggered by `.agents/hooks.json` on `PreInvocation`.
- When `userRequest` invokes `/consultant` or `/cansultant`, emits an `ephemeralMessage`
  containing recent git changes since the last reviewed commit, project state, and instructions
  for the Lead Architectural Consultant & Devil's Advocate role.
- When `invocationNum == 1` or when `userRequest` invokes `/mentor`, emits the standard Mentor
  orientation briefing.
- On other turns, emits `{}` to keep ongoing context clean.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "mentor" / "STATE.md"
CHECKPOINT_PATH = ROOT / "mentor" / ".consultant_checkpoint.json"
DEFAULT_BASELINE_COMMIT = "597421e"


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
        "`Specialist[TInput, TReport]` (`workflows/base.py`, adapted in `subagents/*_subagent.py`). "
        "Every specialist returns a rich Pydantic `*Report` (`ResearchReport`, `RagReport`, `CodeReviewReport`, "
        "`InterpreterReport`, `PersonalContextReport`)—never `str` or `dict`.\n"
        "- **Rung 3 (Macro Scale):** `Coordinator` (`agents/coordinators/`) vs. `Operation` (macro-workflows).\n"
        "- **Return-Pass Pedagogy (Top-Down Compressor Balancing):** Always start from the mountain peak "
        "(the end-to-end `Workflow` film script + `Specialist` contract + Wave/Particle density). Apply "
        "vertical preventative hardening to tall projects (`P2`-`P4`) and horizontal specialist completion "
        "to `P5`.\n\n"
        "## 3. Workspace Skills (`.agents/skills/`)\n"
        "- `/mentor` (`.agents/skills/mentor/SKILL.md`), `/consultant` (`.agents/skills/consultant/SKILL.md`), "
        "`teach` (`.agents/skills/teach/SKILL.md`), `architecture-duality` (`.agents/skills/architecture-duality/SKILL.md`), "
        "`decision-points` (`.agents/skills/decision-points/SKILL.md`), `/handoff` (`.agents/skills/handoff/SKILL.md`).\n\n"
        f"## 4. Live State Snapshot (`mentor/STATE.md`)\n{state_excerpt}\n"
    )


def is_consultant_command(user_request: str) -> bool:
    """Return True if user explicitly invokes the consultant role."""
    lowered = user_request.lower()
    return "/consultant" in lowered or "/cansultant" in lowered


def load_consultant_checkpoint(checkpoint_path: Path = CHECKPOINT_PATH) -> str:
    """Read last consulted commit from checkpoint_path or fallback to default."""
    if checkpoint_path.exists():
        try:
            data = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("last_consulted_commit"):
                return str(data["last_consulted_commit"]).strip()
        except (json.JSONDecodeError, OSError, KeyError):
            return DEFAULT_BASELINE_COMMIT
    return DEFAULT_BASELINE_COMMIT


def get_git_changes_since(
    checkpoint_commit: str, root_dir: Path = ROOT
) -> tuple[list[str], str]:
    """Retrieve list of commits and diffstat since checkpoint_commit."""
    try:
        log_res = subprocess.run(
            ["git", "log", f"{checkpoint_commit}..HEAD", "--oneline"],
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        commits = [c.strip() for c in log_res.stdout.splitlines() if c.strip()]
    except (subprocess.SubprocessError, OSError):
        commits = []

    try:
        diff_res = subprocess.run(
            ["git", "diff", "--stat", f"{checkpoint_commit}..HEAD"],
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        diff_stat = diff_res.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        diff_stat = ""

    return commits, diff_stat


def build_consultant_briefing(
    root: Path = ROOT,
    state_path: Path = STATE_PATH,
    checkpoint_path: Path = CHECKPOINT_PATH,
) -> str:
    """Build the specialized briefing for the Architectural Consultant."""
    last_commit = load_consultant_checkpoint(checkpoint_path=checkpoint_path)
    commits, diff_stat = get_git_changes_since(last_commit, root_dir=root)

    commits_text = (
        "\n".join(f"- `{c}`" for c in commits)
        if commits
        else "(No new commits since last checkpoint)"
    )
    diff_text = (
        f"```\n{diff_stat}\n```"
        if diff_stat
        else "(No working directory or commit diffs)"
    )

    state_excerpt = ""
    if state_path.exists():
        state_text = state_path.read_text(encoding="utf-8")
        now_section = extract_state_section(state_text, "## Now")
        queue_section = extract_state_section(
            state_text, "## Build queue", max_lines=15
        )
        state_excerpt = "\n\n".join(p for p in (now_section, queue_section) if p)

    return (
        "# [CONSULTANT HOOK] Mode: Lead Architectural Consultant & Devil's Advocate\n\n"
        "You are acting as the **Lead Architectural Consultant & Devil's Advocate** for `agentlab` "
        "(`lang-gemini-exercise`). This role was explicitly triggered by the user (`/consultant` / `/cansultant`) "
        "to critically evaluate recent code and design evolution against the foundational architectural vision.\n\n"
        "## 1. Non-Negotiable Consultant Principles\n"
        "- **Asl-e Ghorur (Principle 1):** Zero flattery and zero performative agreement (`tayid-e alaki`). "
        "Conduct a demanding, uncompromising technical critique. Point out leaky abstractions, reflection hacks, "
        "untyped shims, fragile shortcuts, and architectural drift.\n"
        "- **Decide, Don't Ask (Principle 10):** Deliver clear, authoritative architectural verdicts and concrete "
        "recommendations. Do not ask open questions about what should be done.\n"
        "- **Communication Language:** Respond in Finglish when the user writes in Finglish. Code, symbols, and "
        "file links must remain in English.\n\n"
        "## 2. Changes Since Last Review Checkpoint\n"
        f"- **Baseline Checkpoint Commit:** `{last_commit}`\n\n"
        "### Commits Since Checkpoint:\n"
        f"{commits_text}\n\n"
        "### Modified Files & Diffstat:\n"
        f"{diff_text}\n\n"
        f"## 3. Current Project State (`mentor/STATE.md`)\n{state_excerpt}\n\n"
        "## 4. Evaluation Mandate & Dimensions\n"
        "Evaluate the codebase across four critical dimensions:\n"
        "1. **Architecture & Boundary Fidelity (ADR-0033):** Does `src/agentlab/workflows/` sit properly above `agents/` "
        "and `graphs/`? Are `Specialist[TInput, TReport]` contracts typed and enforced? Is Rung-0 decoupled?\n"
        "2. **Code Quality, Type Safety & Smells:** Are there reflection hacks, untyped fallbacks (`*args/**kwargs`), "
        "or duck-typing crutches? Are errors handled with transient retries and HITL propagation?\n"
        "3. **Completeness vs. Raw Design:** What parts of the raw agreed design have been realized, what remains "
        "temporary scaffolding, and what has drifted?\n"
        "4. **Concrete Strategic Recommendations:** What should be refactored, hardened, or scheduled next?\n\n"
        "> **Note:** When the consultation is complete, record the new checkpoint commit via:\n"
        '> `uv run python scripts/record_consultant_checkpoint.py "<summary of review>"`\n'
    )


def should_inject(payload: dict[str, Any]) -> bool:
    """Return True on the first turn of a session or when the user invokes `/mentor`."""
    invocation_num = payload.get("invocationNum")
    if invocation_num in (None, 1):
        return True
    user_request = str(payload.get("userRequest") or "")
    return "/mentor" in user_request.lower()


def handle_hook(
    raw_stdin: str,
    state_path: Path = STATE_PATH,
    checkpoint_path: Path = CHECKPOINT_PATH,
    root_dir: Path = ROOT,
) -> dict[str, str]:
    """Parse `PreInvocation` JSON input and return the hook response dictionary."""
    payload: dict[str, Any] = {}
    if raw_stdin.strip():
        try:
            parsed = json.loads(raw_stdin)
            if isinstance(parsed, dict):
                payload = parsed
        except json.JSONDecodeError:
            payload = {}

    user_request = str(payload.get("userRequest") or "")

    if is_consultant_command(user_request):
        return {
            "ephemeralMessage": build_consultant_briefing(
                root=root_dir,
                state_path=state_path,
                checkpoint_path=checkpoint_path,
            )
        }

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
