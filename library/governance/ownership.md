---
title: Repository map and ownership
maintainer: lead
status: current
updated: 2026-09-27
summary: Every top-level area, what it holds, and which role writes it (one writer per path).
related: [protocol.md, principles.md, ../../AGENTS.md]
---

# Repository Map and Ownership

Each role works in its own worktree and branch ([git-policy.md](../engineering/git-policy.md)),
and every path still has one writing role: that keeps merges into `main` free of conflicts and
numbers free of collisions. Everyone else reads, links, or sends the owner a message
([protocol.md](protocol.md)). Code layout inside `src/agentlab/` is in `AGENTS.md`.

## Map

| Path | Holds | Writer |
| :--- | :--- | :--- |
| `CLAUDE.md` | Session router: what every session loads, and which role it plays | Lead |
| `AGENTS.md` | Repo mechanics for any coding agent: layout, conventions, commands, gotchas | Lead for layout, conventions, and policy; the mentor keeps commands and gotchas true when its code changes them |
| `README.md` | Public front page | Lead |
| `library/` | Shared, canonical, text-only knowledge ([library/README.md](../README.md)) | Each entry's `maintainer`; the lead owns the structure and index |
| `offices/lead/` | Lead office: decisions, plans, architecture, radar, risks, outbox | Lead |
| `offices/mentor/` | Mentor office: role contract, teaching state, lesson log, outbox | Mentor |
| `offices/research/` | Research office: landscape, evidence, briefs, catalog, outbox | Research |
| `docs/adr/` | Architecture decision records | Lead |
| `docs/design_cards/` | Specialist contracts | Lead |
| `docs/ROADMAP.md` | Roadmap v3, superseded by [`offices/lead/ROADMAP.md`](../../offices/lead/ROADMAP.md); to be archived | Lead |
| `docs/study_guides/` | Write-ups of finished projects | Mentor |
| `archive/` | Retired documents, frozen ([archive/README.md](../../archive/README.md)) | The retiring file's owner moves it in; nobody edits it after |
| `src/`, `tests/`, `evals/`, `examples/` | The `agentlab` package, its tests, live eval sets, sample inputs | Mentor |
| `scripts/` | Repo tooling: docs lint, inbox, session hooks, handoff, worktree setup, live smoke, and their tests | Lead |
| `.github/` | CI and Dependabot | Lead |
| `.claude/skills/`, `.claude/settings.json` | Claude Code skills (role bootstraps, `/handoff`) and the session hooks | Lead |
| `CLAUDE.local.md` (per worktree, ignored) | The worktree's role and charter, written by `scripts/setup_worktrees.py` | The setup script |
| `pyproject.toml`, `uv.lock` | Dependencies and tool configuration | Lead; the mentor may add a package its stage plan names |
| `.gitignore`, `.python-version`, `.gitattributes` | Repo configuration | Lead |
| `out/`, `.chroma_index/`, `.venv/` | Runtime output, vector index, environment (all ignored) | Whoever runs the code |
| `alireza/` | The user's private scratch area | The user only; nobody else reads it |

## Rules

- **Write only inside your paths.** Anything else goes to the owner as a message.
- **Don't touch a file that has another role's uncommitted changes,** even inside your paths:
  wait, or stage only your own hunks ([git-policy.md](../engineering/git-policy.md)).
- **Move, don't copy.** When knowledge becomes shared, it moves into `library/` and its old
  home links to it.
- **Retire into `archive/`,** never delete a document that others may still look for.
