---
title: Repository map and ownership
maintainer: lead
status: current
updated: 2026-09-27
summary: Every top-level area, what it holds, and which role writes it (one writer per path); the guard reads the Roles column.
related: [protocol.md, principles.md, ../../AGENTS.md, ../../scripts/workspace.py]
---

# Repository Map and Ownership

Each role works in its own worktree and branch ([git-policy.md](../engineering/git-policy.md)),
and every path still has one writing role: that keeps merges into `main` free of conflicts and
numbers free of collisions. Everyone else reads, links, or sends the owner a message
([protocol.md](protocol.md)). Code layout inside `src/agentlab/` is in `AGENTS.md`.

## Map

The **Roles** column is machine-read: the session guard (`scripts/session_hooks.py`) lets a
role's session edit a path only when that role is listed, and the pull-request report warns about
the rest ([ADR-0020](../../docs/adr/0020-ownership-guard-routing-and-message-awareness.md)).
Values are role names, `all`, or `none`. The longest matching path wins; a path not listed here
belongs to the lead.

| Path | Holds | Writer | Roles |
| :--- | :--- | :--- | :--- |
| `CLAUDE.md` | Session router: what every session loads, and which role it plays | Lead | lead |
| `AGENTS.md` | Repo mechanics for any coding agent: layout, conventions, commands, gotchas | Lead for layout, conventions, and policy; the mentor keeps commands and gotchas true when its code changes them | lead, mentor |
| `README.md` | Public front page | Lead | lead |
| `library/` | Shared, canonical, text-only knowledge ([library/README.md](../README.md)) | The lead, which owns the structure, the index, and every current entry | lead |
| `offices/lead/` | Lead office: decisions, plans, architecture, radar, risks, outbox | Lead | lead |
| `offices/mentor/` | Mentor office: role contract, teaching state, lesson log, outbox | Mentor | mentor |
| `offices/research/` | Research office: landscape, evidence, briefs, catalog, outbox | Research | research |
| `docs/adr/`, `docs/design_cards/` | Architecture decision records; specialist contracts | Lead | lead |
| `docs/study_guides/` | Write-ups of finished projects | Mentor | mentor |
| `archive/` | Retired documents, frozen ([archive/README.md](../../archive/README.md)) | The retiring file's owner moves it in; nobody edits it after | all |
| `src/`, `tests/`, `evals/`, `examples/` | The `agentlab` package, its tests, live eval sets, sample inputs | Mentor | mentor |
| `scripts/`, `.github/` | Repo tooling (docs lint, inbox, session hooks, handoff, worktree setup, reports, live smoke) and their tests; CI, Dependabot, and the message report | Lead | lead |
| `.claude/skills/`, `.claude/settings.json` | Claude Code skills (role bootstraps, `/handoff`, `/inbox`) and the session hooks | Lead | lead |
| `CLAUDE.local.md` | The worktree's role and charter (per worktree, ignored), written by `scripts/setup_worktrees.py` | The setup script | none |
| `pyproject.toml`, `uv.lock` | Dependencies and tool configuration | Lead; the mentor may add a package its stage plan names | lead, mentor |
| `.gitignore`, `.python-version`, `.gitattributes` | Repo configuration | Lead | lead |
| `out/`, `.chroma_index/`, `.venv/` | Runtime output, vector index, environment (all ignored) | Whoever runs the code | all |
| `alireza/` | The user's private scratch area | The user only; nobody else reads it | none |

## Rules

- **Write only inside your paths.** Anything else goes to the owner as a message. When your own
  move breaks another role's links, send the lead a request listing them; the lead fixes them
  when it merges your pull request.
- **Move, don't copy.** When knowledge becomes shared, it moves into `library/` and its old home
  links to it.
- **Retire into `archive/`,** never delete a document that others may still look for.
