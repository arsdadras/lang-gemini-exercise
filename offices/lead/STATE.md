# Lead State

Read first in every lead session; rewrite it, don't append. Program status in one place:
[ROADMAP.md](ROADMAP.md) "Now, next, later". Live teaching status: the mentor's
[state](../mentor/STATE.md).

- **Last lead session:** 2026-09-27 (session 5, local; the session moved from the main checkout
  to `D:/Repos/lce-lead` at its end).
- **Repo:** each role has its own worktree and branch (ADR-0019): `D:/Repos/lce-lead`,
  `lce-mentor`, `lce-research`, each with its own `.venv` and `.env`; the main checkout is a
  clean `main` that takes no edits. The ownership guard, worktree routing, and message
  awareness are live (ADR-0020). Branch protection isn't available on GitHub Free for a private
  repo, so "main only by pull request" is policy, backed by the guard and the Messages report.
  `docs/ROADMAP.md` is archived; the only branches are `main`, `lead`, `mentor`, `research`,
  plus Dependabot's; `handoff/local-snapshot` survives as the tag
  `archive/handoff-local-snapshot`.

## Open messages

LD-003 to LD-005 and LD-015 (research), LD-006 and LD-008 (mentor, R0 close), LD-010 (mentor,
blocking: move in), LD-011 (research, blocking: move in), LD-012 and LD-014 (all). Held until
the Jev file opens: research's RS-014 (BR-003). Details in [OUTBOX.md](OUTBOX.md).

## Reserved for the user

- Trust the project's hooks once when Claude Code asks. The guard makes a misplaced session
  harmless, and it moves itself to the right worktree.
- A TypeSafe API key before P8-C2 closes (backlog).

## Agenda for the next lead session

1. Open the Jev file (the user's go-ahead, 2026-09-27): review research's RS-014 (BR-003 v2) and
   decide its proposals, including the design guide's library placement.
2. Verify the replies to LD-010 and LD-011 (charters updated, runtime data in the mentor's
   worktree); close them. When research answers LD-015, create the weekly routine.
3. Merge the role branches' green pull requests; fast-forward the main checkout.
4. Write the P1 design card (point 16 included) before R1 opens; then P2-P4 before their stages.
5. When R0 closes: record the specialist contract as an ADR, update
   [ARCHITECTURE.md](ARCHITECTURE.md) "Current system", and make R1 ready.
6. Every session: inbox, dependency drift and Dependabot pull requests, docs lint.

## Session log

- **2026-09-26, session 1 (as "the office").** The office was established: charter,
  principles, pedagogy, roadmap v4, architecture, radar, backlog re-triage, risks, DEC-001 to
  DEC-010, ADR-0016 and ADR-0017, six directives, `CLAUDE.md` as a role router.
- **2026-09-26, session 2.** Stack upgraded to the latest releases (`0d27fa8`). Restructured
  into three offices, the library, and the archive (DEC-015, ADR-0018); CI, Dependabot,
  `scripts/check_docs.py`, and `scripts/inbox.py` (DEC-016); LangChain, LangSmith, and
  knowledge-graph findings decided (DEC-011 to DEC-013); research's outbox dispositioned
  (DEC-014); messages LD-001 to LD-009. Moved mid-session from the local machine to a cloud
  session.
- **2026-09-27, session 3 (local).** Synced local `main` with the cloud merge; kept the mentor's
  `AGENTS.md` hunk; fixed `check_docs.py` paths on Windows; merged Dependabot #2 after verifying
  `uv build`; recorded the per-role worktree, hooks, and `/handoff` plan (backlog items a-e) for
  the user's go-ahead, and the Jev-related library placement as a held decision.
- **2026-09-27, session 4 (local).** Merged the mentor's pull request #3 (R0 topic 2, mentor
  office). Built ADR-0019: one worktree and branch per role, `scripts/setup_worktrees.py`,
  session hooks, `/handoff`, and an inbox that reads role branches; decided MN-002 (DEC-018);
  closed LD-001, LD-002, LD-007, LD-009; sent LD-010 to LD-013.
- **2026-09-27, session 5 (local).** On the user's direction: archived `docs/ROADMAP.md`;
  retired `handoff/local-snapshot` as the tag `archive/handoff-local-snapshot` and archived its
  handoff record; built ADR-0020 (ownership guard over a machine-read Roles column, worktree
  routing and `/mentor`, a prompt hook, `/inbox`, the Messages workflow; DEC-019 to DEC-021);
  sent LD-014 and LD-015. The lead now merges without asking.
