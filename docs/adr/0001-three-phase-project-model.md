# ADR-0001: Three phases per project, no Phase D

- Status: Accepted
- Date: 2026-09-13

## Context

In 2026-09, a fourth "Phase D: production hardening" was added to steer a previous mentor
model. Its charter said to drop "avoid over-engineering" and to implement enterprise patterns
even when only one use case exists. That conflicts with the phase contract (no premature
generic registries) and with the extraction rule (one consumer: keep it local). In practice
it produced speculative structure: an agent registry with zero consumers (ADR-0006) and a
planned `MemoryDomainRegistry` for a single memory domain.

## Decision

Each project keeps phases A, B, and C only. Enterprise patterns enter when a real consumer
exists, which mostly means the capstones (P6, P12) and Term E. When a pattern is tempting
earlier, write a short ADR instead of code: the forces, the options, and the concrete trigger
that would justify building it.

## Consequences

- Less code to carry. Every abstraction has a caller.
- Pattern learning moves to the places where its trade-offs are real, and the ADR habit
  trains the judgment of *when* a pattern pays off.

## Alternatives considered

- **Keep Phase D:** rejected, because it teaches speculative generality.
- **Fold Phase D's items into Phase C:** rejected for the same reason; Phase C is about
  composability, not maximal abstraction.
