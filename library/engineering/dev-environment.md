---
title: Development environment
maintainer: lead
status: current
updated: 2026-09-26
summary: Python, uv, the shared virtual environment, office sandboxes, secrets, and live runs.
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

## The shared `.venv`

Several sessions, and the IDE, use the repo's `.venv` at once.

- **Never delete or recreate it while anything may be using it** (a session, the IDE's ruff
  server, a running app). On Windows a held executable makes the recreate fail halfway and
  leaves a broken environment. To rebuild: close the IDE and other sessions, then `uv sync`.
- **Isolated work** (a worktree, a spike on other versions) gets its own environment:
  `UV_PROJECT_ENVIRONMENT=<path> uv sync`, or a git worktree with its own `.venv`.

## Office sandboxes

Each office has a `sandbox/` for scratch work: throwaway scripts, downloads, experiment output.
Git ignores everything in it except its `README.md`. Anything worth keeping moves to the
office's `artifacts/` and is linked from a record.

## Secrets and live runs

- Secrets live only in `.env` (never committed, never printed, never read by agents whose file
  tools expose the repo). Docs name variables, never values.
- Live model runs use test mode per command (`LLM_TEST_MODE=true`, optionally
  `LLM_TEST_PROFILE=<name>`); `.env` is never edited for it.
- Local-only services (Ollama for the `local` tier) are optional; code and tests never require
  them.

## Cloud sessions

A cloud session starts from a fresh clone: `uv sync` builds its own `.venv`, and its `.env` is
absent unless the environment provides the variables. Work that needs keys runs locally or in a
cloud environment configured with them.
