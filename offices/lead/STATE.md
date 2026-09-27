# Lead State

Read first in every lead session; rewrite it, don't append. Program status in one place:
[ROADMAP.md](ROADMAP.md) "Now, next, later". Live teaching status: the mentor's
[state](../mentor/STATE.md).

- **Last lead session:** 2026-09-27 to 28 (session 6, local, in `D:/Repos/lce-lead`).
- **Repo:** each role has its own worktree and branch (ADR-0019): `D:/Repos/lce-lead`,
  `lce-mentor`, `lce-research`, each with its own `.venv` and `.env`; the main checkout is a
  clean `main` that takes no edits. The ownership guard, worktree routing, and message
  awareness are live (ADR-0020). Branch protection isn't available on GitHub Free for a private
  repo, so "main only by pull request" is policy, backed by the guard and the Messages report.
  `docs/ROADMAP.md` is archived; the only branches are `main`, `lead`, `mentor`, `research`,
  plus Dependabot's; `handoff/local-snapshot` survives as the tag
  `archive/handoff-local-snapshot`.

## Open messages

LD-003, LD-005, and LD-015 (research); LD-006 and LD-008 (mentor, R0 close); LD-010 (mentor,
blocking: move in); LD-016 (mentor, R0 topic 3: decision points in the eval harness); LD-012 and
LD-014 (all: research has acknowledged both, the mentor hasn't yet). Received and under review:
research's RS-020 (BR-003 version 3). Details in [OUTBOX.md](OUTBOX.md).

## The Jev file

Open since 2026-09-27. The lead read research's whole dossier and wrote its own:
[artifacts/jev-dossier.md](artifacts/jev-dossier.md). The user asked to think it through together
before anything is decided, so its positions are leanings until the joint review settles its
seven questions. Then: DECISIONS entries and an ADR, the records they touch, the reply to
RS-020, and a directive to the mentor for R1.

## Reserved for the user

- The Jev file's joint review (the dossier's section 13).
- Consent for the development-loop hooks' data flow: session content sent to a hosted decider,
  and past transcripts read for a replay (dossier, section 11).
- Trust the project's hooks once when Claude Code asks.

## Agenda for the next lead session

1. The Jev file: the joint review with the user; then record and execute the decisions, and
   reply to RS-020.
2. Verify the mentor's replies to LD-010, LD-012, LD-014, and LD-016; close them. When research
   answers LD-015, create the weekly routine.
3. Merge the role branches' green pull requests; fast-forward the main checkout.
4. Write the P1 design card before R1 opens, naming its decision points; then P2-P4 before their
   stages.
5. When R0 closes: record the specialist contract as an ADR, update
   [ARCHITECTURE.md](ARCHITECTURE.md) "Current system", and make R1 ready (with the decision seam,
   if the Jev file accepts it).
6. When the user defines the fourth role: its office, ownership rows, worktree, and the hooks'
   role list.
7. Every session: inbox, dependency drift and Dependabot pull requests, docs lint.

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
- **2026-09-27 to 28, session 6 (local).** Opened the Jev file: read research's whole dossier
  (BR-003 version 3, its landscape, and six evidence records with their scripts) and the user's
  sources; wrote the lead's dossier. Merged research's pull request #7 (BR-003 version 3, its
  charter's Sessions section); closed LD-004 and LD-011; sent LD-016; corrected the radar's Jev
  and OpenRouter rows and closed the obsolete TypeSafe-key backlog item.
