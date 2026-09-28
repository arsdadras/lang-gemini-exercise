---
title: Coordination protocol
maintainer: lead
status: current
updated: 2026-09-27
summary: How the offices and the user coordinate through outboxes, inboxes, and state files.
related: [principles.md, ownership.md, ../../scripts/inbox.py]
---

# Coordination Protocol

Five parties run this project. Each role works in its own Claude Code session and its own
office, and the offices talk only through files, never through memory.

| Party | Office | Job |
| :--- | :--- | :--- |
| **User** | none (`alireza/` is private scratch) | Sponsor, product owner, and learner; final authority |
| **Lead** | [`offices/lead/`](../../offices/lead/README.md) | Decides, coordinates, and reviews: direction, roadmap, architecture, technology, governance, git and GitHub |
| **Engineer** | [`offices/engineer/`](../../offices/engineer/README.md) | Builds what the lead decides: implements, tests, debugs, and verifies the code and the repo tooling |
| **Mentor** | [`offices/mentor/`](../../offices/mentor/README.md) | Teaches the learner; reviews the code it teaches |
| **Research** | [`offices/research/`](../../offices/research/README.md) | Investigates, analyzes, and advises; brings the user the big picture; decides nothing |

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
| ID | `LD-###` (lead), `EN-###` (engineer), `MN-###` (mentor), `RS-###` (research); numbered per outbox, never reused |
| to | `lead`, `engineer`, `mentor`, `research`, `user`, or `all`; several are comma-separated |
| type | `directive` (lead only: must be applied at its timing), `request` (asks for a decision, research, a measurement, or a record), `notice` (for information), or `reply <ID>` (answers a message) |
| status | For directives, requests, and notices: `open`, then `closed` or `withdrawn` (set by the sender). For replies: `done`, `partial`, or `declined` |

The body starts with `Issued <date>`, and for a directive a timing: **blocking** (before any
other work), **next topic boundary**, **stage close**, or a named stage. A directive ends with
`Accepted when:` and its criteria. Keep bodies short; link the records that carry the detail.

## Flow

1. **Send.** The sender appends the message to its own outbox with status `open`.
2. **Receive.** Every session hears its inbox without asking: the start hook lists the open
   messages addressed to the role that it hasn't replied to, and the replies to its own open
   messages; the prompt hook announces anything that arrives later. `python scripts/inbox.py
   --fetch` (or `/inbox`) shows it on demand, read from every role's branch.
3. **Act and reply.** The recipient acts at the stated timing (the mentor never breaks a topic
   for a non-blocking message), then appends `reply <ID>` to its own outbox: `done` with the
   commit, `partial` with what remains, or `declined` with the reason (Principle 1).
4. **Close.** The sender checks the reply against the repo at its next session and sets its
   message to `closed`, or sends a new message saying what is still missing.

## Routing

| From | To | Typical types |
| :--- | :--- | :--- |
| Lead | Engineer | Directives (what to build or fix, with acceptance criteria), notices (decisions that touch code) |
| Lead | Mentor | Directives (what to teach, conventions), notices (decisions that touch lessons) |
| Lead | Research | Requests (a question to investigate, a measurement, an upstream check) |
| Engineer | Lead | Requests (a decision the plan doesn't settle), replies (the commits and what was verified) |
| Engineer | Mentor | Notices (a verified component is ready to teach: where its core code is, what to watch for) |
| Mentor | Lead | Requests (a decision the plan doesn't settle, a record for an ADR), notices (parked ideas, found debt) |
| Mentor | Engineer | Requests (a change that makes code teachable, a bug found in a lesson) |
| Research | Lead | Notices (a brief or an upstream change is ready), requests (a key, a budget, a decision) |
| Research | Engineer | Requests (a harness or code change a measurement needs) |
| Anyone | User | Only what the user alone can do: accounts, keys, approvals the rules reserve. The lead surfaces these in its report |

The user talks to each office in its own session. Discussion with the lead is for decisions and
execution; investigation and analysis go to research, and the lead decides on its briefs.

## Sessions

Identity lives in files, not in sessions: a session is short and disposable, and every one of
them rebuilds its context from its office's `STATE.md` and its inbox
([ADR-0019](../../docs/adr/0019-role-worktrees-hooks-and-handoff.md)). A session plays one
role; switching roles means a new session, in the other role's worktree.

| Role | Where its sessions run | Loads its charter through |
| :--- | :--- | :--- |
| Lead | `../lce-lead` (branch `lead`) | `CLAUDE.local.md`, or `/lead` |
| Engineer | `../lce-engineer` (branch `engineer`) | `CLAUDE.local.md`, or `/engineer` |
| Mentor | `../lce-mentor` (branch `mentor`) | `CLAUDE.local.md`, or `/mentor` |
| Research | `../lce-research` (branch `research`) | `CLAUDE.local.md`, or `/research` |

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
  replies and close messages, triage requests, check dependency drift and Dependabot, run
  `scripts/check_docs.py`.
