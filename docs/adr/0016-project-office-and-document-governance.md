# ADR-0016: A project office owns direction; the mentor teaches; one writer per file

- Status: Accepted. Amended by [ADR-0018](0018-three-offices-library-and-archive.md): the office
  became the lead, under `offices/lead/`, and the two-file interface became the message protocol.
- Date: 2026-09-26
- Origin: user mandate; design by the office

## Context

- **One session carried two jobs.** The mentor designed the architecture, planned the
  curriculum, and taught it, often in the same message. Design questions surfaced mid-lesson
  (the two-door redesign in B3, [ADR-0010](0010-one-gate-in-memory-storage.md)), and the plan
  document mixed curriculum policy with the plan itself.
- **The handoff grew a program backlog.** About thirty parked items with destinations lived in
  the mentor's state file, so planning decisions sat in an operational log.
- **Sessions run concurrently on one working tree.** On 2026-09-23 a concurrent session's partial
  rename left 13 tests failing. Two writers of the ADR directory can also allocate the same
  number.
- **A design judgment used an invalid argument.** On 2026-09-25 a session opposed a decision-model
  layer because the CLI's decision volume is small ([ADR-0017](0017-production-standards-as-design-yardstick.md)).
- **The user created the office** on 2026-09-26: a separate session role that decides direction,
  architecture, technology, pedagogy policy, and governance, with the mentor focused on teaching
  and executing the plan.

## Decision

- **Three roles** with explicit decision rights (`docs/office/README.md`, now [`offices/lead/README.md`](../../offices/lead/README.md)):
  the user (sponsor, product owner, learner; final authority), the office (decides, plans,
  records, directs), the mentor (teaches and implements; decides stage-internal design).
- **One writer per file.** The office writes `docs/office/`, `docs/adr/`, `docs/design_cards/`,
  `CLAUDE.md`, `README.md`, and its skill. The mentor writes its contract, its handoff, `AGENTS.md`,
  and all lesson code. Each role changes the other's files only through the interface.
- **The interface is two files.** Office to mentor: `docs/office/DIRECTIVES.md`, with timing and
  acceptance criteria, applied at topic or stage boundaries so lessons aren't interrupted.
  Mentor to office: a "For the office" section in the handoff (decision requests, record
  requests, new ideas, acknowledgments).
- **`CLAUDE.md` is a role router.** It always loads `AGENTS.md`, the project principles, and the
  mentor contract (the default role). The office charter loads on demand through a user-invoked
  `/office` skill, or when the user opens the session as an office session. Where the mentor's
  documents and the office's disagree during migration, the office's win.
- **Project-wide rules move to `docs/office/PRINCIPLES.md`;** the mentor contract keeps only the
  mentor's procedure (DIR-002). The old `docs/ROADMAP.md` is retired (DIR-004).

## Consequences

- An architecture question raised mid-lesson now waits for an office session; the mentor keeps
  teaching whatever doesn't depend on it.
- ADR numbers and design cards have one author, so they can't collide or drift between sessions.
- Until DIR-001 to DIR-004 are applied, some rules exist twice; the precedence line in `CLAUDE.md`
  settles conflicts.
- Office sessions still load the mentor contract through `CLAUDE.md`; the router says its
  delivery procedure doesn't apply there.

## Alternatives considered

- **One session wearing both hats:** rejected; it is what the user split, and it spends teaching
  sessions' context and attention on design.
- **The office edits the mentor's files directly:** rejected; concurrent sessions would lose
  updates, and the user ruled it out.
- **Import the office charter in `CLAUDE.md`:** rejected; it would load the office's procedure into
  every mentor session. Claude Code loads skills on demand, which fits an occasional role.
- **Move the mentor contract into a `/mentor` skill as well:** rejected for now; the mentor is the
  default and most frequent role, and an import is the most reliable way to keep its contract in
  context for long lessons.
- **The mentor keeps writing ADRs:** rejected; two writers collide on numbers, and significant
  decisions belong to the office.
