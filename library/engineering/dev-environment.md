---
title: Development environment
maintainer: lead
status: current
updated: 2026-09-27
summary: Python, uv, the role worktrees and their environments, session hooks, sandboxes, secrets, and live runs.
related: [dependency-policy.md, git-policy.md, ../../AGENTS.md, ../../scripts/setup_worktrees.py, ../../.claude/settings.json]
---

# Development Environment

Repo commands and conventions are in [`AGENTS.md`](../../AGENTS.md); this entry covers the
environment those commands run in.

## Python and uv

- Python 3.14 (`.python-version`); new environments use the latest 3.14 patch uv provides.
- `uv` manages everything: `uv sync` installs the project editable with the dev group;
  `uv sync --locked` (CI) fails instead of changing the lock.
- Keep one `uv` install per machine, current (`uv self update`, or the package manager that
  installed it). Two installs on `PATH` drift apart silently.

## Role worktrees

Each role has its own checkout next to the main one, so no session ever shares a working tree,
an index, or a `.venv` with another ([git-policy.md](git-policy.md),
[ADR-0019](../../docs/adr/0019-role-worktrees-hooks-and-handoff.md)).

```
D:/Repos/lang_claude_exercise   main checkout: clean main, the IDE, alireza/; no role session
D:/Repos/lce-lead               lead's worktree, branch lead
D:/Repos/lce-mentor             mentor's worktree, branch mentor; the learner's exercises
D:/Repos/lce-research           research's worktree, branch research
```

`python scripts/setup_worktrees.py` (run from any checkout) creates what is missing and never
touches what exists. For each role it adds the worktree, records the role in the worktree's
own git config (`agentlab.role`), writes `CLAUDE.local.md` so every session there loads the
role's charter, copies `.env` from the main checkout, runs `uv sync`, and pushes the branch.
`--copy-runtime` copies the main checkout's `out/state/` and `.chroma_index/` into a worktree
that has none; run it with no app running.

- **Open a role's sessions in its worktree.** The IDE opens the mentor's worktree for exercises.
- **Each worktree has its own `.venv`, `.env`, and runtime data** (`out/`, `.chroma_index/`),
  because paths resolve from the checkout. Copy `.env` into a worktree; never put one in a
  parent directory, where `load_dotenv()`'s upward search would also hand it to sibling
  projects.
- **Never delete or recreate a `.venv` while anything may be using it** (a session, the IDE's
  ruff server, a running app). On Windows a held executable makes the recreate fail halfway and
  leaves a broken environment. To rebuild one: close what uses it, then `uv sync`.
- **Auto-memory is shared:** Claude Code keeps one memory directory per repository, for every
  worktree, so memories reach every role. Keep role-specific rules in the offices, not in memory.

## Session hooks

`.claude/settings.json` runs `scripts/session_hooks.py`, which needs only the standard library:

- **SessionStart** adds to the session's context the role (from the worktree's config, or the
  branch name in a cloud session), what `main` has that the branch lacks, unpushed commits,
  `git status`, the head of the role's `STATE.md`, and its inbox. It fetches first and carries
  on offline.
- **Stop** shows one warning, never a block, when a role worktree has uncommitted or unpushed
  work: end the session with `/handoff`.

A session outside the role worktrees (the main checkout, a fresh clone) is told it plays no
role until `/lead` or `/research` says otherwise.

## Office sandboxes

Each office has a `sandbox/` for scratch work: throwaway scripts, downloads, experiment output,
verified component copies. Git ignores everything in it except its `README.md`, so a sandbox
stays on its machine; anything another machine needs moves to the office's `artifacts/` or
into a `wip` commit.

## Secrets and live runs

- Secrets live only in `.env` (never committed, never printed, never read by agents whose file
  tools expose the repo). Docs name variables, never values.
- Live model runs use test mode per command (`LLM_TEST_MODE=true`, optionally
  `LLM_TEST_PROFILE=<name>`); `.env` is never edited for it.
- Local-only services (Ollama for the `local` tier) are optional; code and tests never require
  them.

## Cloud sessions

A cloud session starts from a fresh clone on its given branch: `uv sync` builds its own `.venv`,
its `.env` is absent unless the environment provides the variables, and the session hook takes
the role from the branch name. Switching between local and cloud needs only a pushed branch
(`/handoff`) and a pull.
