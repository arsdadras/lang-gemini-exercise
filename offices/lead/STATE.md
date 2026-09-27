# Lead State

Read first in every lead session; rewrite it, don't append. Program status in one place:
[ROADMAP.md](ROADMAP.md) "Now, next, later". Live teaching status: the mentor's
[state](../mentor/STATE.md).

- **Last lead session:** 2026-09-27 (session 4, local, run from the main checkout while the lead
  worktree was being built).
- **Repo:** each role now has its own worktree and branch (ADR-0019): `D:/Repos/lce-lead`,
  `lce-mentor`, `lce-research`, each with its own `.venv` and `.env`. The main checkout is a
  clean `main`. The mentor's R0 topic 2 work and office migration merged as pull request #3
  (`9ca81da`); the worktree setup merged as the lead's pull request (see the session log).
  Branch protection isn't available on GitHub Free for a private repo, so "main only by pull
  request" is policy ([BACKLOG.md](BACKLOG.md), Parked).

## Open messages

LD-003 to LD-005 (research), LD-006 and LD-008 (mentor, R0 close), LD-010 (mentor, blocking:
move in), LD-011 (research, blocking: move in), LD-012 (all). Held, not triaged: research's
RS-014 (BR-003, the Jev file). Details in [OUTBOX.md](OUTBOX.md).

## Reserved for the user

- Research's Jev investigation (RS-014, BR-003): the lead reviews it only when the user opens
  that file ("parvande-ye Jev ro shoru konim"); the library placement of research's design guide
  is decided then ([BACKLOG.md](BACKLOG.md), Parked).
- Archive `docs/ROADMAP.md` (superseded v3): waits for the user's word.
- Delete `handoff/local-snapshot` (not merged; its content is now on `main` through the
  mentor's and research's own commits): needs the user's OK under the git policy.
- A TypeSafe API key before P8-C2 closes (backlog).
- Trust the project's hooks once when Claude Code asks; open each role's sessions in its
  worktree.

## Agenda for the next lead session

1. Run in `D:/Repos/lce-lead`. Verify the replies to LD-010 and LD-011 (charters updated, runtime
   data in the mentor's worktree); close them.
2. Merge the role branches' green pull requests; fast-forward the main checkout.
3. Triage research's upstream notices (LD-003) and briefs; decide on LD-005's results.
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
