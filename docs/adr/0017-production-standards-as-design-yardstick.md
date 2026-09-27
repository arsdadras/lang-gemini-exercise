# ADR-0017: Production engineering standards are the design yardstick

- Status: Accepted. Refines [ADR-0001](0001-three-phase-project-model.md) and the build-ahead-of-need
  test (now [principles](../../library/governance/principles.md) section 3); supersedes neither.
- Date: 2026-09-26
- Origin: user direction; formulated by the office

## Context

- **This repo's product is a skill, not software.** Nobody will use agentlab as a product; the
  learner will build production systems elsewhere. What the repo must teach is how those systems
  are designed.
- **A volume argument rejected a pattern.** On 2026-09-25 a session evaluated encoder decision
  models (a System-1 layer that answers typed decisions in about 0.2 s and escalates to an LLM
  when unsure) and opposed them because "our decision volume is small (interactive CLI); 1.5 s to
  0.25 s doesn't change the UX, and the cost is near zero". That measures the teaching harness
  instead of the system being learned, and it removes exactly the architecture the learner would
  need at scale.
- **The same error happened before.** On 2026-08-23 a file split was rejected with "our current
  scale doesn't need it"; the user corrected it, but the lesson was never written into the repo's
  rules, so it came back.
- **The opposite error is also documented.** ADR-0001 and [ADR-0006](0006-remove-agent-registry.md)
  removed speculative enterprise structure (a registry with no consumer, drifting out of sync).
  The fix must not reopen that door.

## Decision

- **Design load is production.** Designs are judged as if the system served real users at scale.
- **Inadmissible arguments:** current usage or call volume, number of users, savings "too small
  to matter here", time-to-market or business ROI.
- **Admissible arguments,** and every rejection or deferral names one: wrong at production scale
  too; sequencing (a named later stage); evidence (unverified, measured worse, immature
  dependency); scope (an office decision).
- **Efficiency is a quality, not a veto:** it chooses among designs that meet the standard.
- **Over-engineering is redefined** as complexity no production force justifies, or generality
  ahead of an observed shape.
- **Scale-ready seams now, abstractions when observed.** Identity, persistence, concurrency,
  failure handling and timeouts, security, secrets, observability, and idempotency are
  production-grade from their first consumer. Registries, generic layers, and plugin points wait
  for two or three observed instances.
- **Operational hooks:** the stage admission rule judges "needed now" at production load; every
  design card names its production path (point 16).

## Consequences

- Deferrals that rested only on volume were reviewed. One was found and re-decided: the System-1
  layer is now stage P8-C3, while its candidate implementation (Laya) stays at Assess on evidence
  (DEC-004).
- Development standards the repo lacked now land: CI (DEC-005), explicit timeouts on external
  calls, released dependency versions (DEC-009, DEC-010).
- Deferrals to Term E that rest on sequencing stay valid when a seam exists (for example,
  concurrent SQLite users: the checkpointer and store sit behind swappable interfaces).
- Reviews take longer: a rejection now has to say which admissible argument it uses.

## Alternatives considered

- **Keep the rules as they were:** rejected; the error recurred because nothing forbade it.
- **Drop "avoid over-engineering" altogether and build enterprise patterns early:** rejected;
  that was the old Phase D, and speculative generality is itself a production anti-pattern
  (ADR-0001).
- **Build everything at production scale now:** rejected; it breaks the difficulty curve. The
  curriculum sequences production concerns; it doesn't skip them.
