# ADR-0028: One mentor, one branch

- Status: Accepted
- Date: 2026-10-05
- Origin: user override (the learner, in a mentor session). The mentor agreed, with one
  concern recorded under Alternatives.
- Supersedes: [ADR-0019](0019-role-worktrees-hooks-and-handoff.md) (role worktrees, hooks,
  `/handoff` on role branches), [ADR-0020](0020-ownership-guard-routing-and-message-awareness.md)
  (ownership guard, routing, message awareness), [ADR-0025](0025-two-roles-lead-and-mentor.md)
  (two roles), [ADR-0027](0027-the-mentor-directs-the-lead-assists.md) (decision rights between
  the roles; its MN-024 curriculum decisions stand), and the office and message parts of
  [ADR-0018](0018-three-offices-library-and-archive.md) and
  [ADR-0024](0024-a-lead-curated-library-in-five-categories.md).
- Revisit when: `main` goes red twice from an unverified push, or the learner asks for a
  separate reviewer again.

## Context

Between 2026-09-26 and 2026-10-05 the project grew from one mentor to four roles and back to
two: separate offices, outboxes and message IDs, an inbox script and a GitHub workflow, an
ownership guard, one worktree and branch per role, pull requests, and a lead that merged them.
The learner found that this machinery cost more than it gave: messages waited between sessions,
work was split across branches, and every change needed a hand-off. They want one mentor again.

## Decision

1. **One role: the mentor.** It plans, builds, tests, researches, records, and teaches. The
   lead's records (roadmap, backlog, decisions, risks, research) are the mentor's now.
2. **One office, `mentor/`:** `README.md` (charter), `STATE.md`, `LOG.md`, `ROADMAP.md`,
   `BACKLOG.md`, `DECISIONS.md`, `RISKS.md`, `research/`, `artifacts/`, `sandbox/` (ignored).
   The system architecture moves to [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md). There are no
   messages: an open question is an item in `STATE.md` or `BACKLOG.md`.
3. **One branch: `main`.** Every session, local or in an app-made worktree, starts from
   `origin/main` and pushes its verified work straight to `main`. No role branches, no role
   worktrees, no pull requests (Dependabot's excepted).
4. **One command per session: `/mentor`.** It syncs with `main`, reads the state, prepares the
   lesson and its code (building, testing, and running whatever the lesson needs), teaches, and
   when the learner has no more questions announces the end, prepares the next session, and
   pushes. `/handoff` is the closing step it calls.
5. **Retired** (archived or deleted): the lead's charter and both outboxes
   (`archive/offices/`), the protocol and the ownership table (`archive/library/governance/`),
   `scripts/inbox.py`, `pr_report.py`, `setup_worktrees.py`, `session_hooks.py`, `workspace.py`,
   `handoff.py` and their tests, the `Messages` workflow, the `/lead` and `/inbox` skills, the
   `lce-lead` and `lce-mentor` worktrees, and the `lead`, `mentor`, and `claude/*` branches once
   `main` held everything on them.

## Consequences

- No hand-offs between roles: the session that finds a problem fixes it.
- Nobody reviews the mentor's code but the checks and the learner. The gate is deterministic:
  `pytest`, `ruff check`, `ruff format --check`, `scripts/check_docs.py`, CI on every push, and a
  live run in test mode for behavior a test can't pin.
- History keeps the old message IDs (`LD-`, `MN-`, `EN-`, `RS-`) and `DEC-` numbers; they stay
  valid references into `archive/offices/` and `mentor/DECISIONS.md`.

## Alternatives considered

- **Keep two roles with lighter messaging.** Rejected by the learner: the cost was the split
  itself, not the message format.
- **The mentor's concern:** building and teaching in one role loses the second pair of eyes the
  lead gave. Answer: the checks above, plus a habit already in the `teach` skill (the teaching
  review of every component before it is taught). The trigger in "Revisit when" reopens it.
