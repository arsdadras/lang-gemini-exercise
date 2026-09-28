---
title: Dependency policy
maintainer: lead
status: current
updated: 2026-09-26
summary: How the stack stays on the latest stable releases, LangChain's ecosystem above all.
related: [git-policy.md, dev-environment.md, ../technology/radar.md, ../../.github/dependabot.yml]
---

# Dependency Policy

The stack tracks the latest stable releases. LangChain, LangGraph, DeepAgents, and LangSmith
come first: they are the curriculum's subject, and a lesson taught on a stale API teaches the
wrong thing (Principle 2, "Stay current").

## Versions

- **Released versions only.** A pre-release enters `main` only with a recorded reason and an
  exit date in the [radar](../technology/radar.md).
- **`uv.lock` holds the exact versions.** `pyproject.toml` declares lower bounds; an exact pin
  exists only where a known break or a reviewed tool needs it, with a comment saying why (ruff
  is pinned so new lint rules arrive as their own change).
- **Declare what you import.** A package the code imports directly is a declared dependency,
  even when another package already pulls it in.
- **A new dependency** enters through the radar (Assess, then Trial or Adopt) with its reason,
  never silently with a feature.

## Staying current

- **Dependabot** (`.github/dependabot.yml`) checks `uv` dependencies daily and GitHub Actions
  weekly. The LangChain family (`langchain*`, `langgraph*`, `deepagents`, `langsmith`) arrives as
  one grouped pull request, everything else as another.
- **The lead merges an update** when CI is green and, for the LangChain family or any model
  provider SDK, after reading the release notes and running `uv run python
  scripts/smoke_live.py` in test mode.
- **Taught APIs wait for a boundary.** An update that changes an API the current stage teaches
  is merged at the next topic boundary, with a notice to the mentor naming the change; the
  stage's beta APIs are re-verified when it starts.
- **Every session of the lead** checks drift (`uv lock --upgrade --dry-run`) and open Dependabot
  pull requests, and follows LangChain's releases, changelog, and blog for changes to what the
  curriculum teaches or plans (research watches upstream in depth).

## Verification for any upgrade

1. Read the changelogs for breaking changes in APIs this repo uses.
2. `uv lock --upgrade` (or the package-specific `--upgrade-package`), then `uv sync`.
3. `uv run pytest`, `uv run ruff check src tests scripts`, `uv run ruff format --check src tests
   scripts`.
4. `uv run python scripts/smoke_live.py` in test mode for the LangChain family and provider SDKs.
5. Update the radar's version line, and notify the mentor of anything a lesson touches.
