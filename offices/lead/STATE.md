# Lead State

Read first in every lead session; rewrite it, don't append. Program status in one place:
[ROADMAP.md](ROADMAP.md) "Now, next, later". Live teaching status: the mentor's
[state](../mentor/STATE.md).

- **Last lead session:** 2026-09-27 (session 3, local): synced local `main` after session 2,
  which ran in a cloud session on branch `main-1le51z` (`handoff/local-snapshot`).
- **Repo:** the stack upgrade (`0d27fa8`) and the three-offices restructure were merged into
  `main` by pull request on 2026-09-27, with CI green. On 2026-09-27 the local lead
  fast-forwarded local `main` to it, kept the mentor's convention-11 hunk in `AGENTS.md`
  uncommitted, and fixed `scripts/check_docs.py` to print POSIX paths on Windows (`439b62f`, CI
  green). Local `main` still holds the mentor's uncommitted R0 topic 2 work (suite red on
  purpose: an exercise state) and research's uncommitted office under `docs/research/` plus
  `library/engineering/decision-models.md`; all stay theirs to commit (RSK-11). Dependabot
  pull request #2 (`setuptools>=84` in `build-system.requires`) is open.

## Open messages

LD-001 (mentor, blocking), LD-002 (research, blocking), LD-003 to LD-005 (research), LD-006 to
LD-008 (mentor, R0 close), LD-009 (all). Details in [OUTBOX.md](OUTBOX.md).

## Reserved for the user

- Research's Jev investigation: the lead reviews it only when the user opens that file.
- Archive `docs/ROADMAP.md` (superseded v3): the local lead's attempt was blocked, so it waits
  for the user's word.
- Local machine: rebuild the broken main `.venv` with the IDE closed (`uv sync`); keep one `uv`
  install on `PATH`.
- A TypeSafe API key before P8-C2 closes (backlog).

## Agenda for the next lead session

1. Verify replies to LD-001 and LD-002 against the repo; close them or send what is missing.
   Then retire the precedence line in `CLAUDE.md` and close RSK-03.
2. Once research has moved, make `scripts/check_docs.py` pass on the whole tree locally.
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
