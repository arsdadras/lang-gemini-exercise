---
title: Git policy
maintainer: mentor
status: current
updated: 2026-10-06
summary: One branch (main), every session pushes its verified work there, CI on every push, and what is never done to history.
related: [dependency-policy.md, dev-environment.md, ../../.github/workflows/ci.yml, ../../docs/adr/0028-one-mentor-one-branch.md]
---

# Git Policy

The mentor owns git and GitHub and commits and pushes without asking (principle 10). There is
one branch, `main` ([ADR-0028](../../docs/adr/0028-one-mentor-one-branch.md)).

## Every session

- **Start from `origin/main`.** On `main`, `git merge --ff-only origin/main`. In a worktree the
  desktop app made for the session (a `claude/...` branch under `.claude/worktrees/`), merge
  `origin/main` into it (the app's `sync_with_base_branch` tool does this).
- **End with `/handoff`:** the checks, one or more commits, and `git push origin HEAD:main`.
  Then the main checkout is fast-forwarded when it is clean, so the learner reads the new code
  there.
- **No other branches.** No role branches, no pull requests, no long-lived worktrees. The app's
  per-session `claude/...` branches are disposable: their work reaches `main` by the push above.
  Dependabot's pull requests are the one exception; they are merged when CI is green.

## Commits

- **Only verified states reach `main`:** `pytest`, `ruff check`, `ruff format --check`, `mypy`, and
  `scripts/check_docs.py` pass before the push. Nothing is ever reset for the learner to type
  ([ADR-0023](../../docs/adr/0023-active-review-instead-of-typing.md)).
- **Conventional commits:** `type(scope): summary` in English, imperative, at most 72
  characters. Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`.
- **Never committed:** `.env` or any secret, `alireza/`, `.venv/`, `out/`, `.chroma_index/`,
  `mentor/sandbox/`, `.claude/settings.local.json`, plugin data under `.claude/`.

## CI

CI (`.github/workflows/ci.yml`) runs `ruff check`, `ruff format --check`, `mypy src/agentlab`,
`pytest`, and `scripts/check_docs.py` on every push and pull request. A red `main` is fixed before
any other work. A check is never skipped or weakened to get a change through.

## Never

- Force-push, rebase, or amend anything already pushed.
- Rewrite `main`'s history, or push with the checks red.
