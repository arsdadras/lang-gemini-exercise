---
title: Development environment
maintainer: mentor
status: current
updated: 2026-10-06
summary: Python, uv, the checkouts a session may run in, the sandbox, secrets, and live runs.
related: [dependency-policy.md, git-policy.md, ../../AGENTS.md]
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

## Checkouts

```
D:/Repos/lang_claude_exercise                    main checkout, on main: where the learner reads code; .env; alireza/
D:/Repos/lang_claude_exercise/.claude/worktrees/  worktrees the desktop app makes, one per session (claude/... branches)
```

A session runs either in the main checkout or in the worktree the app made for it; both start
from `origin/main` and push to `main` ([git policy](git-policy.md)).

- **`.env`** lives only in the main checkout. An app worktree sits inside it, so
  `load_dotenv()`'s upward search from the calling file finds the same `.env`. Never put one in a
  parent directory of the main checkout, where sibling projects would also find it.
- **Each checkout has its own `.venv` and runtime data** (`out/`, `.chroma_index/`), because
  paths resolve from the checkout. A fresh worktree runs `uv sync` first.
- **Never delete or recreate a `.venv` while anything may be using it** (a session, the IDE's
  ruff server, a running app). On Windows a held executable makes the recreate fail halfway and
  leaves a broken environment. To rebuild one: close what uses it, then `uv sync`.

## The sandbox

`mentor/sandbox/` holds scratch work: throwaway scripts, downloads, experiment output, "what
if" variations of verified code. Git ignores everything in it except its `README.md`; anything
worth keeping moves to `mentor/attachments/` and is linked from a record.

## Secrets and live runs

- Secrets live only in `.env` (never committed, never printed, never read by agents whose file
  tools expose the repo). Docs name variables, never values.
- Live model runs use test mode per command (`LLM_TEST_MODE=true`, optionally
  `LLM_TEST_PROFILE=<name>`); `.env` is never edited for it.
- Local-only services (Ollama for the `local` tier) are optional; code and tests never require
  them.

## Cloud sessions

A cloud session starts from a fresh clone: `uv sync` builds its `.venv`, and its `.env` is
absent unless the environment provides the variables. It pushes to `main` like any other
session.
