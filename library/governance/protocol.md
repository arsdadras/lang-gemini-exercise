---
title: Coordination protocol
maintainer: lead
status: current
updated: 2026-09-26
summary: How the offices and the user coordinate through outboxes, inboxes, and state files.
related: [principles.md, ownership.md, ../../scripts/inbox.py]
---

# Coordination Protocol

Four parties run this project. Each role works in its own Claude Code session and its own
office, and the offices talk only through files, never through memory.

| Party | Office | Job |
| :--- | :--- | :--- |
| **User** | none (`alireza/` is private scratch) | Sponsor, product owner, and learner; final authority |
| **Lead** | [`offices/lead/`](../../offices/lead/README.md) | Decides and executes: direction, roadmap, architecture, technology, governance, git and GitHub |
| **Mentor** | [`offices/mentor/`](../../offices/mentor/README.md) | Teaches the learner and implements the plan in lesson code |
| **Research** | `offices/research/` (at `docs/research/` until it moves, LD-002) | Investigates, measures, and advises; decides nothing |

## Files every office has

| File | Holds | Written by |
| :--- | :--- | :--- |
| `README.md` | The office's charter: mandate, scope, session protocol, file map | That office (the lead sets the mandate) |
| `STATE.md` | Current status and agenda; read first every session | That office |
| `OUTBOX.md` | Every message the office sends | That office |
| `artifacts/` | Files worth keeping: scripts, outputs, data, each linked from a record (created with its first file) | That office |
| `sandbox/` | Local scratch; never committed ([dev-environment.md](../engineering/dev-environment.md)) | That office |

## Messages

A message lives in its sender's `OUTBOX.md` and nowhere else. Its heading is one line, so
people and `scripts/inbox.py` read it the same way:

```markdown
### LD-007 | to mentor | directive | open
```

| Field | Values |
| :--- | :--- |
| ID | `LD-###` (lead), `MN-###` (mentor), `RS-###` (research); numbered per outbox, never reused |
| to | `lead`, `mentor`, `research`, `user`, or `all`; several are comma-separated |
| type | `directive` (lead only: must be applied at its timing), `request` (asks for a decision, research, a measurement, or a record), `notice` (for information), or `reply <ID>` (answers a message) |
| status | For directives, requests, and notices: `open`, then `closed` or `withdrawn` (set by the sender). For replies: `done`, `partial`, or `declined` |

The body starts with `Issued <date>`, and for a directive a timing: **blocking** (before any
other work), **next topic boundary**, **stage close**, or a named stage. A directive ends with
`Accepted when:` and its criteria. Keep bodies short; link the records that carry the detail.

## Flow

1. **Send.** The sender appends the message to its own outbox with status `open`.
2. **Receive.** At session start every role runs `uv run python scripts/inbox.py <role>`,
   which lists open messages addressed to it that it hasn't replied to, and replies to its own
   open messages.
3. **Act and reply.** The recipient acts at the stated timing (the mentor never breaks a topic
   for a non-blocking message), then appends `reply <ID>` to its own outbox: `done` with the
   commit, `partial` with what remains, or `declined` with the reason (Principle 1).
4. **Close.** The sender checks the reply against the repo at its next session and sets its
   message to `closed`, or sends a new message saying what is still missing.

## Routing

| From | To | Typical types |
| :--- | :--- | :--- |
| Lead | Mentor | Directives (plans, migrations, conventions), notices (upgrades, decisions that touch lessons) |
| Lead | Research | Requests (a question to investigate, a measurement, an upstream check) |
| Mentor | Lead | Requests (a decision the plan doesn't settle, a record for an ADR), notices (parked ideas, found debt) |
| Research | Lead | Notices (a brief or an upstream change is ready), requests (a key, a budget, a decision) |
| Research | Mentor | Requests (a harness change needed for a measurement) |
| Anyone | User | Only what the user alone can do: accounts, keys, approvals the rules reserve. The lead surfaces these in its report |

The user talks to each office in its own session. Discussion with the lead is for decisions and
execution; investigation and analysis go to research, and the lead decides on its briefs.

## Sessions

`CLAUDE.md` routes every session. It always loads `AGENTS.md`, [principles.md](principles.md),
this protocol, and the mentor's charter, because the mentor is the default role. The other
roles start with a user-invoked skill:

| Role | Starts with | First reads |
| :--- | :--- | :--- |
| Mentor | Any session (default) | [`offices/mentor/STATE.md`](../../offices/mentor/STATE.md), then its inbox |
| Lead | `/lead` | [`offices/lead/README.md`](../../offices/lead/README.md), its `STATE.md`, then its inbox |
| Research | `/research` | Its charter and `STATE.md`, then its inbox |

A session plays one role; switching roles means a new session.

## Session rhythm

- **Start:** your `STATE.md`, then your inbox.
- **End:** update `STATE.md`, reply to what you acted on, and commit and push your own paths
  ([git-policy.md](../engineering/git-policy.md)).
- **Lead, every session:** verify replies and close messages, triage requests, check dependency
  drift and open Dependabot pull requests, run `scripts/check_docs.py`.
