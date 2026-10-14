"""Antigravity PreInvocation hook for the Reviewer & Tester workflow.

Triggered by `.agents/hooks.json` on `PreInvocation`. Inspects git status, recent commits,
and changed files, maps them to the 4-Scale Wave-Particle Duality architecture (ADR-0033),
and outputs an `ephemeralMessage` on `stdout` when the user request contains `/reviewer`.
Returns `{}` when `/reviewer` is not invoked.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


def should_inject(payload: dict[str, Any]) -> bool:
    """Return True when `userRequest` invokes `/reviewer`."""
    user_request = str(payload.get("userRequest") or "")
    return "/reviewer" in user_request.lower()


def run_git_command(args: list[str], cwd: Path = ROOT) -> str:
    """Run a git command safely and return stripped stdout, or empty string on failure."""
    try:
        res = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        return res.stdout.strip() if res.returncode == 0 else ""
    except (subprocess.SubprocessError, OSError):
        return ""


def get_git_branch(cwd: Path = ROOT) -> str:
    """Return current branch name or 'unknown'."""
    branch = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)
    return branch or "unknown"


def get_recent_commits(cwd: Path = ROOT, limit: int = 5) -> list[str]:
    """Return the recent git commits as a list of oneline strings."""
    out = run_git_command(["log", f"-n{limit}", "--oneline"], cwd=cwd)
    return [line.strip() for line in out.splitlines() if line.strip()]


def get_changed_files(cwd: Path = ROOT) -> list[str]:
    """Return changed files from uncommitted working tree and latest commit."""
    changed: set[str] = set()
    # 1. Staged and unstaged working tree changes
    status_out = run_git_command(["status", "--short"], cwd=cwd)
    for line in status_out.splitlines():
        line = line.strip()
        if len(line) > 3:
            parts = line[2:].strip().split(" -> ")
            changed.add(parts[-1].strip())

    # 2. Files changed in the latest commit
    diff_out = run_git_command(
        ["diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
        cwd=cwd,
    )
    for line in diff_out.splitlines():
        if line.strip():
            changed.add(line.strip())

    return sorted(changed)


def categorize_file(path_str: str) -> str:
    """Map a repository file path to its architectural role in ADR-0033."""
    norm = path_str.replace("\\", "/")
    if norm.startswith("src/agentlab/workflows/"):
        return "Rung-2: Domain Workflows & Specialists (Wave-Particle duality)"
    if norm.startswith("src/agentlab/subagents/"):
        return "Rung-2: Subagent Adapters (Workflow -> Subagent adapters)"
    if norm.startswith("src/agentlab/schemas/"):
        return "Rung-2: Typed Boundary Contracts (Input/Output schemas)"
    if norm.startswith("src/agentlab/agents/coordinators/"):
        return "Rung-3: Coordinators (Macro orchestration)"
    if norm.startswith("src/agentlab/agents/"):
        return "Rung-1: Role Agents (Particle hot loops)"
    if norm.startswith(("src/agentlab/graphs/", "src/agentlab/nodes/")):
        return "Rung-1: LangGraph Graphs & Nodes (Wave pipelines)"
    if norm.startswith(("src/agentlab/middlewares/", "src/agentlab/tools/")):
        return "Rung-0/1: Tools & Middlewares"
    if any(
        norm.startswith(f"src/agentlab/{pkg}/")
        for pkg in ("models", "data", "utils", "configs", "retrieval", "prompts")
    ):
        return "Rung-0: Primitives & Cross-Cutting Infrastructure"
    if norm.startswith("src/agentlab/apps/"):
        return "Rung-3: CLI Entry Points & Composition Roots"
    if norm.startswith(("tests/", "evals/")):
        return "Quality Gate: Test Suite & Evals"
    if any(norm.startswith(d) for d in ("mentor/", "docs/", "library/")):
        return "Governance, ADRs & Architecture Documentation"
    if norm.startswith((".agents/", ".claude/")):
        return "Agent Customizations, Skills & Hooks"
    return "Repository Support & Configuration"


def build_reviewer_briefing(cwd: Path = ROOT) -> str:
    """Construct the markdown briefing for the Reviewer & Tester role."""
    branch = get_git_branch(cwd)
    commits = get_recent_commits(cwd, limit=5)
    files = get_changed_files(cwd)

    commit_lines = (
        "\n".join(f"- `{c}`" for c in commits) if commits else "- (no commits found)"
    )

    categorized_lines: list[str] = []
    if files:
        for f in files:
            cat = categorize_file(f)
            categorized_lines.append(f"- `{f}` -> **{cat}**")
        files_text = "\n".join(categorized_lines)
    else:
        files_text = "- (no modified or committed files detected in recent git history)"

    return (
        "# [REVIEWER & TESTER ACTIVATION] Focus Protocol & Architecture Context\n\n"
        "You have been invoked as the **Reviewer & Tester** via `/reviewer`.\n\n"
        f"## 1. Git Repository State\n"
        f"- **Active Branch:** `{branch}`\n"
        f"- **Recent Commits:**\n{commit_lines}\n\n"
        f"## 2. Detected Changes & Architectural Mapping (ADR-0033)\n"
        f"{files_text}\n\n"
        "## 3. Reviewer Mandate & Operating Instructions\n"
        "- **Pragmatic Testing (No Resource Bloat):** Do NOT waste excessive resources on endless trivial "
        "tests or runaway permutations. Verify the core paths, interfaces, and real edge cases.\n"
        "- **Critical Vigilance (Do Not Blindly Trust Repo Tests):** Do NOT assume pre-existing tests "
        "cover newly introduced patterns or changes. If new logic, schemas, or descriptors were added, "
        "write focused new tests. If previous tests became obsolete or rigid, edit or replace them.\n"
        "- **Step-by-Step Verification:** Progress step-by-step: (1) inspect changed diffs, (2) check "
        "architectural alignment with ADR-0033 (Wave-Particle duality, dependency direction, typed boundaries), "
        "(3) verify type safety and error handling, (4) run and/or add unit tests, and (5) report findings clearly.\n"
        "- **Language & Tone:** Always communicate in **Finglish** (Persian written in Latin characters), "
        "maintaining concise, highly rigorous technical assessments without false flattery.\n"
    )


def handle_hook(raw_stdin: str, repo_root: Path = ROOT) -> dict[str, str]:
    """Parse PreInvocation JSON input and return ephemeral reviewer message if invoked."""
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

    return {"ephemeralMessage": build_reviewer_briefing(cwd=repo_root)}


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
