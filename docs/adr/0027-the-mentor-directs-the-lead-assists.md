# ADR-0027: The mentor directs, the lead assists

- Status: Accepted
- Date: 2026-10-05
- Origin: the user (lead session 10), and the learner's standing instruction relayed by the
  mentor (MN-022) and its decisions of the day (MN-024).
- Supersedes in part: [ADR-0025](0025-two-roles-lead-and-mentor.md) (decision rights),
  the git policy's "main only by pull request".
- Revisit when: the user changes the arrangement, or `main` goes red twice from unreviewed pushes.

## Context

ADR-0025 made the lead the only builder and tester, and the mentor a teacher that never writes
code. In practice the learner works through the mentor, and the mentor already changed code at
the learner's word (MN-022). The user now makes this the rule.

## Decision

1. **The mentor directs; the lead assists.** The lead keeps doing the same work (planning,
   building, research, records, git and GitHub), but on the mentor's orders. A mentor message is
   acted on as a directive.
2. **Tests and evals belong to the mentor.** The lead proposes (code, designs, records); the
   mentor reviews, tests, evaluates, edits if it wants, and teaches.
3. **The mentor writes code** (`src/`, `tests/`, `evals/`, `examples/`) without the lead's
   approval, naming each commit to the lead (MN-022). The ownership table lists both roles there.
4. **Direct pushes to `main`** are allowed for both roles; pull requests are optional.
5. **MN-024, the learner's decisions, recorded:**
   - A repo-level **engineering track** (hardening and service health: security, redaction and
     masking, observability, failure handling and timeouts, contract conformance) applies to every
     project and is no project's stage. R stages grow capability.
   - R0 stays (done). R1 is redesigned. R3 stays. **R2** becomes a RAG capability upgrade
     (hybrid search, reranking, query rewriting, the index rebuilt) judged by hit rate at k; the
     harness itself goes to the track. **R4** (declared side effects, a risk label) moves to the
     track; P4's capability upgrade is chosen with the mentor. R5 stays a practice stage.
   - **P13** is the browser and computer-use agent (acting in web apps that have no API).
   - **P11** (Capstone, midterm II) is an insight-to-publication workflow: P10 analysis and P8
     documents feed P6's content generator, with P9's review gate before publishing. Stages are
     written when semester 2 starts.

## Consequences

- The ownership guard lets the mentor edit code paths; one writer per path no longer holds there,
  so merge conflicts on `src/` are possible and are resolved by whoever merges second.
- The lead's charter, `CLAUDE.md`, the ownership table, and the git policy say so.

## Dissent (Principle 1, the lead)

- Code reaching `main` without the author running the suite makes `main` red for both roles. The
  lead therefore still runs the existing linters before a push; CI runs the suite on every push.
- Without pull requests nothing reviews a change before `main`; the mentor's review happens after
  the fact.

## Alternatives considered

- Keep ADR-0025 and send the mentor's code changes as requests: rejected by the user.
