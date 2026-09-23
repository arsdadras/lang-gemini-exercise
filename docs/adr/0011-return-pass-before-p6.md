# ADR-0011: A return pass over P1-P5 before P6, and a fixed difficulty curve

- Status: Accepted; amended 2026-09-23 by [ADR-0013](0013-p5-completion.md) (P5 finished
  by the mentor before R0, then taught again from B4 after R4)
- Date: 2026-09-22

## Context

- **The specialists were built at rising levels.** P1 is a single DeepAgents agent over Tavily
  snippets with self-reported confidence; P2 a raw corrective-RAG graph; P3 and P4 composed
  subgraphs, sandboxes, and approval gates; P5 added governance, guards, and background work.
  An audit on 2026-09-22 found no shared contract: P1 returns a Pydantic report, P2 a string,
  P3 formatted text, P4 text plus an artifact diff, P5 chat.
- **P6 composes them.** Its Phase A plan says "calls P1 and P2 through typed contracts",
  which neither has. Building P6 on uneven parts would either spend P6 retrofitting them or
  bake the unevenness into the capstone.
- **Cross-cutting pieces exist in one project only.** User identity (`UserContext`), secret
  redaction at the app boundary, and trace masking are P5-only. Approvals use four mechanisms
  and two CLI loops. Only P5 has a design card; only P3 and P4 have study guides. The
  groundedness middleware and `time_travel_util` are exported but unused.
- **The mentee proposed a return pass** to upgrade and unify P1-P5 before P6, and asked for a
  predictable difficulty curve after B3 rose too steeply in one stage.

## Decision

- **A return pass (R0-R5) runs before P6** (`docs/ROADMAP.md`). The mentee asked to pause
  P5 after B4 topic 1: R0-R4 run first, P5 then resumes and is finished against the
  contract, and R5 closes the pass with every specialist, P5 included. R0 defines one
  specialist contract; R1-R4 bring each specialist to it and give each one real upgrade; R5
  closes with cross-cutting cleanup and a before/after demo.
- **Every R stage teaches one new concept.** Conformance work (renaming, wiring, envelopes,
  boilerplate) is done by the mentor directly; the stage's lesson is the upgrade.
- **No rewrites by default.** A project keeps its architecture unless the audit shows it can't
  meet the contract; that call is made at the stage, with its reason.
- **The contract is defined by P6's needs, not guessed.** R0 derives it from P6's Phase A-B
  plan, so the pass passes "observed, not predicted" (`docs/MENTORING.md`).
  *Update (2026-09-23):* in practice R0 derived the envelope from the callers P1-P5 already
  have (the P2 and P4 coordinators, the P5 brief), which is stronger evidence than a plan.
  The contract is caller-agnostic; P6 is its first composed consumer, not its author. A
  generic calling layer (one input shape, discovery, a catalog) stays out until P12.
- **A fixed difficulty curve** (levels L1-L7 in the roadmap): the level rises only at project
  boundaries, a stage holds at most one hard new concept, and a steep stage is followed by a
  lighter one. Every project from P6 on is planned as named stages, each with its one hard
  concept, re-cut at phase start when the build shows a better split.

## Consequences

- P6 starts from comparable parts, and its Phase A can focus on the workflow.
- About six stages are added before P6. Each stays one sitting per topic.
- Backlog items for P1-P4 now have a destination instead of waiting indefinitely.
- The pass risks feeling like going backwards; each stage ends with a before/after demo of
  the same scenario on the old and the upgraded specialist.

## Alternatives considered

- **Upgrade each specialist inside P6 as it's composed:** rejected. P6's lessons (parallel
  fan-in, failure classes, control comparison) would compete with retrofitting.
- **Rebuild P1-P5 from scratch:** rejected. The existing designs are sound where tested; a
  rewrite repeats lessons without new ones.
- **Leave them as they are:** rejected. The contract gap blocks P6-A as planned.
