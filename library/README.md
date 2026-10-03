---
title: Library
maintainer: lead
status: current
updated: 2026-09-28
summary: The shared, canonical, text-only knowledge base every role reads and only the lead writes; its rules, its categories, and its index.
related: [LOG.md, governance/ownership.md, ../docs/adr/0024-a-lead-curated-library-in-five-categories.md, ../scripts/check_docs.py]
---

# Library

Knowledge that more than one role needs lives here, once: the rules every role follows, how we
build, how we design, the facts about our stack, and how the learner learns. Offices hold what
only their role uses and their own plans and records. It is text only (Markdown), so every entry
is reviewable in a diff and readable by any session.

## Rules

- **Only the lead writes here** ([ADR-0024](../docs/adr/0024-a-lead-curated-library-in-five-categories.md)).
  Every role reads the library; a role that wants an entry changed sends the lead a message
  ([protocol.md](governance/protocol.md)). The ownership guard enforces it.
- **The lead curates.** At every phase and project boundary, and whenever a record becomes
  knowledge other roles rely on, the lead brings it here from whichever office holds it and
  whoever wrote it, and files it under its category.
- **Move, never copy** (principle 9):
  - Stable knowledge (a rule, a guide, a policy, a lesson learned) moves here, and its old home
    links to it. For another role's file, the lead asks the owner by message to replace the
    original with the link.
  - The living facts (vendors, numbers, measurements) stay in the research record
    (`offices/lead/research/`: landscape and evidence). An entry here carries the practical takeaway and the key numbers, with the record
    ID and its date.
- **No forks.** A rule that differs by role is written in its entry with the role named; a
  role-only procedure lives in that role's office and links here.
- **Text only.** No scripts, data, or binaries; those belong to an office's `artifacts/` or to
  `scripts/`.
- **`alireza/` stays outside.** It is the learner's private area; nothing enters from it unless
  the learner sends it.

## Categories

| Category | Holds |
| :--- | :--- |
| Governance | How the roles work together: principles, protocol, ownership, terms |
| Engineering | How we build and ship: git, dependencies, the environment |
| Architecture | How we design: the standards every component meets, decision points |
| Technology | Facts about the stack at hand: the radar, the model tiers and deciders |
| Teaching | How the learner learns: the pedagogy |

## Front matter

Every entry except this index and the log starts with YAML front matter.
`scripts/check_docs.py` enforces it.

| Field | Required | Value |
| :--- | :-: | :--- |
| `title` | yes | Human title |
| `maintainer` | yes | `lead` |
| `status` | yes | `current`, `draft`, or `superseded` |
| `updated` | yes | `YYYY-MM-DD` of the last content change |
| `summary` | yes | One sentence: what the entry holds |
| `related` | no | Relative paths of closely linked files |

## Operations

The library is maintained the way an LLM-maintained wiki is: sources come in, knowledge is
compiled into interlinked pages, and the whole is linted.

- **Ingest.** When a decision, a finding, or a convention becomes shared, the lead writes or
  updates one entry, links it from its related entries and this index, and appends one line to
  [LOG.md](LOG.md).
- **Query.** Start at the index below; follow links. Never answer from an office's copy of a
  shared fact: there shouldn't be one.
- **Lint.** `uv run python scripts/check_docs.py` checks links, anchors, front matter, and that
  every entry is in this index. CI runs it on every push.

## Index

### Governance

| Entry | Holds |
| :--- | :--- |
| [principles.md](governance/principles.md) | The rules every role follows in every session |
| [protocol.md](governance/protocol.md) | How the roles coordinate: offices, outboxes, sessions |
| [ownership.md](governance/ownership.md) | Repository map: every path, its one writer, and the Roles the guard enforces |
| [glossary.md](governance/glossary.md) | Terms with a specific meaning in this repo |

### Engineering

| Entry | Holds |
| :--- | :--- |
| [git-policy.md](engineering/git-policy.md) | Role worktrees and branches, pull requests, commits, pushes, and CI |
| [dependency-policy.md](engineering/dependency-policy.md) | Staying current: versions, pins, Dependabot, upgrades |
| [dev-environment.md](engineering/dev-environment.md) | Python, uv, role worktrees and their environments, session hooks, sandboxes, secrets |

### Architecture

| Entry | Holds |
| :--- | :--- |
| [standards.md](architecture/standards.md) | The architecture principles, the scale seams, and the composition patterns |
| [decision-models.md](architecture/decision-models.md) | The rule for every AI decision point, the one standard each is held to, and calling decision models here |

### Technology

| Entry | Holds |
| :--- | :--- |
| [radar.md](technology/radar.md) | Where each technology stands (adopt, trial, assess, hold), and the locked versions |
| [models.md](technology/models.md) | The LLM tiers, fallback, and test mode; the deciders; what is measured; how tiers will be chosen |

### Teaching

| Entry | Holds |
| :--- | :--- |
| [pedagogy.md](teaching/pedagogy.md) | Learning outcomes, the learning method (active review), curriculum rules, readiness, delivery invariants, assessment |
