# Lead State

Read first in every lead session; rewrite it, don't append. Program status in one place:
[ROADMAP.md](ROADMAP.md) "Now, next, later". Live teaching status: the mentor's
[state](../mentor/STATE.md); live build status: the engineer's [state](../engineer/STATE.md).

- **Last lead session:** 2026-09-27 to 28 (session 6, local, in `D:/Repos/lce-lead`).
- **Roles:** four since 2026-09-28 (ADR-0022). The lead decides, coordinates, and reviews; the
  engineer builds, tests, debugs, and verifies every code and tooling change; the mentor teaches
  and reviews the code it teaches; research investigates, analyzes, and advises. A change flows
  lead -> engineer -> the lead's review and merge -> mentor. The learner reviews the verified
  code instead of typing it (ADR-0023). Reports to the user open with the bottom line
  (principle 12).
- **Library:** the lead's alone to write and curate, in five categories (ADR-0024). First pass
  done: the pedagogy, the radar, and the architecture standards moved in from this office;
  redirects stay at `PEDAGOGY.md` and `TECH_RADAR.md` until the mentor and research update
  their links.
- **Repo:** each role has its own worktree and branch (ADR-0019): `D:/Repos/lce-lead`,
  `lce-engineer`, `lce-mentor`, `lce-research`, each with its own `.venv` and `.env`; the main
  checkout is a clean `main` that takes no edits. The ownership guard, worktree routing, and
  message awareness are live (ADR-0020); since ADR-0022 the guard keeps the lead out of code and
  tooling. Branch protection isn't available on GitHub Free for a private repo, so "main only by
  pull request" is policy, backed by the guard and the Messages report.

## Open messages

- **Engineer:** LD-018 (blocking: move in, adopt the office and the live code issues), LD-024
  (charter wording, docs lint for a lead-only library), LD-019 (R0's remaining implementation,
  in order).
- **Mentor:** LD-010 and LD-023 (blocking: move in; teaching only, active review, charter and
  state).
- **Research:** LD-021 (mandate and the Jev follow-ups), LD-025 (library links), LD-003 with
  LD-015 (upstream watch), LD-005 (measurements; its code-needing parts go through the engineer).
- **All:** LD-012, LD-014, LD-022, LD-026 (research acknowledged the first two; the mentor and
  the engineer haven't yet).

Details in [OUTBOX.md](OUTBOX.md).

## The Jev file

Decided 2026-09-28: the user accepted the lead's [dossier](artifacts/jev-dossier.md) in full
(DEC-022 to DEC-025, ADR-0021, roadmap v4.2). The rules live in
[`library/architecture/decision-models.md`](../../library/architecture/decision-models.md). First
code: the eval harness's decision datasets (LD-019), then the `decision_model` seam when R1 is made
ready.

## Reserved for the user

- The explicit yes before a development-loop hook sends session content to a hosted decider, or a
  replay reads past transcripts (DEC-025); asked when the first such hook is ready.
- The OK to delete the old `src/data/dbs/checkpoints.db` (LD-019 item 5).
- Trust the project's hooks once when Claude Code asks.

## Agenda for the next lead session

1. Inbox waiting since 2026-09-29: the mentor's request MN-013 (its rebuilt teaching research)
   and its replies MN-005 to MN-010 (LD-010, LD-023, LD-012, LD-014, LD-022, LD-026). Decide
   MN-013; check each reply against the repo and close what checks out.
2. Review and merge the engineer's pull requests against LD-018, LD-019, and LD-024; verify
   research's replies to LD-021 and LD-025; close what checks out. When the mentor and research
   have updated their links, remove the redirects (BACKLOG).
3. Write the P1 design card before R1 opens, with its decision points (point 17); then P2-P4
   before their stages.
4. When R0 closes: record the specialist contract as an ADR, update
   [ARCHITECTURE.md](ARCHITECTURE.md) "Current system", and make R1 ready: the decision seam
   (ADR-0021) as the engineer's next directive, ahead of the lesson.
5. When research answers LD-015, create the weekly routine.
6. At every phase and project boundary: curate the library from every office (ADR-0024).
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
- **2026-09-27 to 28, session 6 (local).** Opened and closed the Jev file: read research's whole
  dossier and the user's sources, wrote the lead's dossier, and after the user accepted it
  recorded DEC-022 to DEC-025 and ADR-0021 (roadmap v4.2, stage D1, design card point 17, the
  library entry, the `decision-points` skill). Founded the engineer role on the user's direction
  (DEC-026, ADR-0022): its office, worktree, tooling support, and ownership; moved R0's
  implementation to it (LD-018, LD-019); new mandates for the mentor and research (LD-020,
  LD-021); reports open with the bottom line (DEC-027). Merged pull requests #7 and #8; closed
  LD-004 and LD-011.
- **2026-09-28, session 6 continued.** On the user's direction, relayed from a side chat: the
  learner reviews instead of typing (DEC-028, ADR-0023; LD-020 reissued as LD-023, LD-024 to the
  engineer), and the library became the lead's alone, in five categories, with a first curation
  pass (DEC-029, ADR-0024; LD-025, LD-026).
