---
title: Coordination protocol
maintainer: lead
status: current
updated: 2026-10-03
summary: The two parties' roles, the message format between the lead and the mentor, the flow, routing, sessions, and the session rhythm.
related: [principles.md, ownership.md, ../../docs/adr/0025-two-roles-lead-and-mentor.md, ../engineering/git-policy.md]
---

# Coordination Protocol

Three parties run this project: the user and two roles. Each role works in its own Claude Code
session and its own office, and the offices talk only through files, never through memory
([ADR-0025](../../docs/adr/0025-two-roles-lead-and-mentor.md)).

| Party | Office | Job |
| :--- | :--- | :--- |
| **User** | none (`alireza/` is private scratch) | Sponsor, product owner, and learner; final authority |
| **Lead** | [`offices/lead/`](../../offices/lead/README.md) | Decides, plans, builds, researches, and reviews: direction, roadmap, architecture, technology, governance, code and tooling, evidence, git and GitHub |
| **Mentor** | [`offices/mentor/`](../../offices/mentor/README.md) | Teaches the learner; reviews the code it teaches |

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
| ID | `LD-###` (lead), `MN-###` (mentor); numbered per outbox, never reused. Old `EN-###` and `RS-###` IDs (the retired engineer and research roles) stay as history |
| to | `lead`, `mentor`, `user`, or `all`; several are comma-separated. Messages written before 2026-10-03 may name `engineer` or `research`; new ones never do |
| type | `directive` (lead only: must be applied at its timing), `request` (asks for a decision or a record), `notice` (for information), or `reply <ID>` (answers a message) |
| status | For directives, requests, and notices: `open`, then `closed` or `withdrawn` (set by the sender). For replies: `done`, `partial`, or `declined` |

The body starts with `Issued <date>`, and for a directive a timing: **blocking** (before any
other work), **next topic boundary**, **stage close**, or a named stage. A directive ends with
`Accepted when:` and its criteria. Keep bodies short; link the records that carry the detail.

## Flow

1. **Send.** The sender appends the message to its own outbox with status `open`.
2. **Receive.** Every session hears its inbox without asking: the start hook lists the open
   messages addressed to the role that it hasn't replied to, and the replies to its own open
   messages; the prompt hook announces anything that arrives later. `python scripts/inbox.py
   --fetch` (or `/inbox`) shows it on demand, read from both roles' branches.
3. **Act and reply.** The recipient acts at the stated timing (the mentor never breaks a topic
   for a non-blocking message), then appends `reply <ID>` to its own outbox: `done` with the
   commit, `partial` with what remains, or `declined` with the reason (Principle 1).
4. **Close.** The sender checks the reply against the repo at its next session and sets its
   message to `closed`, or sends a new message saying what is still missing.

## Routing

| From | To | Typical types |
| :--- | :--- | :--- |
| Lead | Mentor | Directives (what to teach, conventions), notices (decisions that touch lessons; verified code ready to teach: where its core code is, what to watch for) |
| Mentor | Lead | Requests (a decision the plan doesn't settle, a record for an ADR, a change that makes code teachable, a bug found in a lesson), notices (parked ideas, found debt) |
| Anyone | User | Only what the user alone can do: accounts, keys, approvals the rules reserve. The lead surfaces these in its report |

The user talks to each office in its own session. The lead plans, builds, and investigates; the
mentor teaches and brings what teaching reveals back as requests.

## Sessions

Identity lives in files, not in sessions: a session is short and disposable, and every one of
them rebuilds its context from its office's `STATE.md` and its inbox
([ADR-0019](../../docs/adr/0019-role-worktrees-hooks-and-handoff.md)). A session plays one
role; switching roles means a new session, in the other role's worktree.

| Role | Where its sessions run | Loads its charter through |
| :--- | :--- | :--- |
| Lead | `../lce-lead` (branch `lead`) | `CLAUDE.local.md`, or `/lead` |
| Mentor | `../lce-mentor` (branch `mentor`) | `CLAUDE.local.md`, or `/mentor` |

`CLAUDE.md` loads `AGENTS.md`, [principles.md](principles.md), and this protocol into every
session. The session hook tells each session its role (from the worktree, or the branch name in
a cloud session), what `main` has that its branch lacks, its uncommitted work, the head of its
`STATE.md`, and its inbox ([dev-environment.md](../engineering/dev-environment.md)).

## Session rhythm

- **Start:** read the hook's summary. Merge `origin/main` into your branch when it says `main`
  has moved, then read your `STATE.md` and act on your inbox.
- **During:** keep sessions short; when one grows long, hand off and start a fresh one rather
  than compacting the same session again and again.
- **End:** `/handoff`: update `STATE.md`, reply to what you acted on, commit, push, and open a
  pull request when the work is ready for `main`
  ([git-policy.md](../engineering/git-policy.md)).
- **Lead, every session:** merge green pull requests and fast-forward the main checkout, verify
  the mentor's replies and close messages, triage requests, check dependency drift and
  Dependabot, run `scripts/check_docs.py`.
