---
title: Git policy
maintainer: lead
status: current
updated: 2026-09-26
summary: How every role commits and pushes, what CI guards, and what is never done to history.
related: [dependency-policy.md, ../governance/ownership.md, ../../.github/workflows/ci.yml]
---

# Git Policy

Git and GitHub belong to the lead: it sets this policy, owns `.github/`, merges pull requests,
and keeps `main` green. Under this policy every role commits and pushes its own work without
asking (Principle 10).

## Branches

- **`main`** on GitHub is the integration branch. CI runs on every push to any branch, so a
  pull request shows its head's result.
- **Local sessions** share one working tree on `main`. Each commits its own paths and pushes
  `main` at the end of its session.
- **Cloud sessions** work on the branch their session was given and reach `main` through a
  pull request, merged by the lead when CI is green.
- **Short-lived branches** (a Dependabot update, a handoff, a spike) are deleted by the lead
  once merged. Deleting a branch that isn't merged needs the user's OK.

## Commits

- **Path-limited.** Stage your own paths by name ([ownership.md](../governance/ownership.md));
  never `git add -A` or `git add .`. In a file that also holds another role's uncommitted hunks,
  stage only yours (`git add -p`, or `git apply --cached` with a hunk patch).
- **Only verified states.** The suite and the linters pass on what you commit. The mentor never
  commits an exercise state (lesson files reset for the learner to type); it commits the
  verified version.
- **Conventional commits:** `type(scope): summary` in English, imperative, at most 72
  characters. Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`. Documentation
  from an office uses the role as scope (`docs(lead): ...`, `docs(research): ...`).
- **Never committed:** `.env` or any secret, `alireza/`, `.venv/`, `out/`, `.chroma_index/`,
  office sandboxes, `.claude/settings.local.json`.

## Pushes and CI

- Push after committing, at least at the end of every session; unpushed commits are one lost
  machine away from gone.
- A red `main` is fixed before any other work by the role whose commit broke it. If that role
  can't fix it in its session, the lead reverts the commit and sends the owner a message.
- CI (`.github/workflows/ci.yml`) runs `ruff check`, `ruff format --check`, `pytest`, and
  `scripts/check_docs.py`. A check is never skipped or weakened to get a change through.

## Never

- Force-push, rebase, or amend anything already pushed.
- Rewrite `main`'s history, or merge with CI red.
- Push another role's uncommitted work as your own; send it a message instead.
