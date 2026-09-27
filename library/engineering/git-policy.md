---
title: Git policy
maintainer: lead
status: current
updated: 2026-09-27
summary: One worktree and branch per role, pull requests to main merged by the lead without asking, branch retirement, CI, and what is never done to history.
related: [dependency-policy.md, dev-environment.md, ../governance/ownership.md, ../../.github/workflows/ci.yml, ../../docs/adr/0019-role-worktrees-hooks-and-handoff.md]
---

# Git Policy

Git and GitHub belong to the lead: it sets this policy, owns `.github/`, merges pull requests,
and keeps `main` green. Under this policy every role commits and pushes its own work without
asking (Principle 10).

## Branches and worktrees

Each role works in its own git worktree, on its own long-lived branch
([ADR-0019](../../docs/adr/0019-role-worktrees-hooks-and-handoff.md)):

| Role | Worktree | Branch |
| :--- | :--- | :--- |
| Lead | `../lce-lead` | `lead` |
| Mentor | `../lce-mentor` | `mentor` |
| Research | `../lce-research` | `research` |

- **`main`** is the integration branch, and nobody commits to it directly. Every change reaches
  it by pull request: the role opens one from its branch (`/handoff --pr`), CI runs, and the
  lead merges when CI is green, its own pull requests included.
- **The lead merges whenever it judges a pull request ready, and never asks first** (the user's
  standing direction, 2026-09-27). Readiness means CI green, the Messages report read, and any
  file outside the branch's role accounted for.
- **Merge commits** for role branches: they keep every commit's SHA valid on `main`, so the
  SHAs that office records cite stay true, and the role branch never diverges from `main`.
  Dependabot's single-commit updates are squash-merged.
- **Sync at every session start:** the role runs `git merge origin/main` into its branch when
  `main` has moved (the session hook says so), so work always builds on what others merged.
- **The main checkout** stays on a clean `main` for the user and runs no role session. The lead
  fast-forwards it after merging.
- **Cloud sessions** work on the branch their session was given (a role's branch, or one the
  platform names) and reach `main` the same way.
- **Short-lived branches** (a Dependabot update, a handoff, a spike) are deleted by the lead
  once merged. A branch retired without merging is first kept as an annotated tag
  `archive/<branch>` pushed to `origin`, so nothing is lost; then the branch goes. Role branches
  are never deleted; GitHub's automatic head-branch deletion stays off.

`scripts/setup_worktrees.py` creates or completes the worktrees
([dev-environment.md](dev-environment.md)).

## Commits

- **Your worktree holds only your work.** Every path you change must list your role in
  [ownership.md](../governance/ownership.md)'s Roles column; the session guard refuses other
  edits, and the Messages report on each pull request lists any that slipped through a shell
  command. When your own move breaks another role's links, send the lead a request listing them.
- **End every session with `/handoff`:** it updates your state, commits everything in your
  worktree, pushes your branch, and prints a three-line summary. Unfinished work is committed
  as `wip(<role>): ...`; a role branch may be red between sessions.
- **Only verified states reach `main`.** A pull request is opened when the suite and the linters
  pass. The mentor never opens one on an exercise state (lesson files reset for the learner to
  type); it commits the verified version first.
- **Conventional commits:** `type(scope): summary` in English, imperative, at most 72
  characters. Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`. Documentation
  from an office uses the role as scope (`docs(lead): ...`, `docs(research): ...`).
- **Never committed:** `.env` or any secret, `alireza/`, `.venv/`, `out/`, `.chroma_index/`,
  office sandboxes, `CLAUDE.local.md`, `.claude/settings.local.json`, plugin data under
  `.claude/`.

## Pushes and CI

- Push at the end of every session (`/handoff` does); unpushed commits are one lost machine away
  from gone, and a pushed branch is all another machine or a cloud session needs.
- A red `main` is fixed before any other work by the role whose change broke it. If that role
  can't fix it in its session, the lead reverts the merge and sends the owner a message.
- CI (`.github/workflows/ci.yml`) runs `ruff check`, `ruff format --check`, `pytest`, and
  `scripts/check_docs.py` on every push to any branch. A check is never skipped or weakened to
  get a change through.

## Never

- Force-push, rebase, or amend anything already pushed.
- Commit to `main` directly, rewrite its history, or merge with CI red.
- Commit another role's work as your own; send it a message instead.
