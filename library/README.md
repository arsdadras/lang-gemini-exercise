---
title: Library
maintainer: lead
status: current
updated: 2026-09-26
summary: The shared, canonical, text-only knowledge base every role reads; its rules and its index.
related: [LOG.md, governance/ownership.md, ../scripts/check_docs.py]
---

# Library

Knowledge that more than one role needs lives here, once. Offices hold what only their role
uses; the library holds what everyone relies on: principles, the coordination protocol, the
repository map, engineering policies, and shared terms. It is text only (Markdown), so every
entry is reviewable in a diff and readable by any session.

## Rules

- **Canonical, never copied.** Knowledge that becomes shared *moves* here, and its old home
  links to it. Nothing here is restated elsewhere (Principle 9).
- **Every entry has one maintainer** (a role, named in its front matter). Other roles propose
  changes to the maintainer by message ([protocol.md](governance/protocol.md)); the lead owns the
  structure, this index, and the log.
- **No forks.** A role that needs a variant of an entry does not copy it. A rule that differs by
  role is written in the entry with the role named; a role-only procedure lives in that role's
  office and links here.
- **Text only.** No scripts, data, or binaries; those belong to an office's `artifacts/` or to
  `scripts/`.

## Front matter

Every entry except this index and the log starts with YAML front matter.
`scripts/check_docs.py` enforces it.

| Field | Required | Value |
| :--- | :-: | :--- |
| `title` | yes | Human title |
| `maintainer` | yes | `lead`, `engineer`, `mentor`, or `research` |
| `status` | yes | `current`, `draft`, or `superseded` |
| `updated` | yes | `YYYY-MM-DD` of the last content change |
| `summary` | yes | One sentence: what the entry holds |
| `related` | no | Relative paths of closely linked files |

## Operations

The library is maintained the way an LLM-maintained wiki is: sources come in, knowledge is
compiled into interlinked pages, and the whole is linted.

- **Ingest.** When a decision, a finding, or a convention becomes shared, the maintainer writes
  or updates one entry, links it from its related entries and this index, and appends one line
  to [LOG.md](LOG.md).
- **Query.** Start at the index below; follow links. Never answer from an office's copy of a
  shared fact: there shouldn't be one.
- **Lint.** `uv run python scripts/check_docs.py` checks links, anchors, front matter, and that
  every entry is in this index. CI runs it on every push.

## Index

### Governance

| Entry | Holds | Maintainer |
| :--- | :--- | :--- |
| [principles.md](governance/principles.md) | The rules every role follows in every session | lead |
| [protocol.md](governance/protocol.md) | How the roles coordinate: offices, outboxes, sessions | lead |
| [ownership.md](governance/ownership.md) | Repository map: every path, its one writer, and the Roles the guard enforces | lead |
| [glossary.md](governance/glossary.md) | Terms with a specific meaning in this repo | lead |

### Engineering

| Entry | Holds | Maintainer |
| :--- | :--- | :--- |
| [git-policy.md](engineering/git-policy.md) | Role worktrees and branches, pull requests, commits, pushes, and CI | lead |
| [dependency-policy.md](engineering/dependency-policy.md) | Staying current: versions, pins, Dependabot, upgrades | lead |
| [decision-models.md](engineering/decision-models.md) | The rule for every AI decision point, the one standard each is held to, and calling decision models here | lead |
| [dev-environment.md](engineering/dev-environment.md) | Python, uv, role worktrees and their environments, session hooks, sandboxes, secrets | lead |
