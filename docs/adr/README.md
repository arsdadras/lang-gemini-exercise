# Architecture Decision Records

An ADR records one significant decision: the forces behind it, what was decided, what it
costs, and what else was considered. Write one whenever a stage settles a design or process
question that future work depends on, and whenever the mentee overrides the mentor
(record the dissent too).

Keep ADRs short. Never rewrite an accepted ADR's decision: supersede it with a new ADR and
set the old one's status to `Superseded by ADR-XXXX`.

## Index

| ADR | Decision | Status |
| :--- | :--- | :--- |
| [0001](0001-three-phase-project-model.md) | Three phases per project, no Phase D | Accepted |
| [0002](0002-single-package-and-composition-root.md) | One `agentlab` package; apps are the composition root | Accepted |
| [0003](0003-runtime-context-for-user-identity.md) | User identity travels as runtime context | Accepted |
| [0004](0004-testing-and-evaluation-policy.md) | Unit tests now, eval-lite from P5-C, eval infrastructure in Term E | Accepted |
| [0005](0005-sandbox-secret-isolation.md) | Sandboxed code never sees secrets | Accepted |
| [0006](0006-remove-agent-registry.md) | Remove the agent registry until P6 needs one | Accepted |
| [0007](0007-built-in-model-fallback.md) | Agent model fallback uses `ModelFallbackMiddleware` | Accepted |
| [0008](0008-memory-write-governance.md) | Memory writes governed by operation in code; content by a later guard | Accepted |
| [0009](0009-stage-admission-rule.md) | A stage admission rule; P10 folded into P7 and the roadmap refined | Accepted |
| [0010](0010-one-gate-in-memory-storage.md) | One gate inside the memory storage, judging content as well as operation | Accepted |
| [0011](0011-return-pass-before-p6.md) | A return pass over P1-P5 before P6, and a fixed difficulty curve | Accepted |
| [0012](0012-memory-consolidation-single-writer.md) | Memory has one writer: a background consolidator proposing line-level edits | Accepted |

## Template

```markdown
# ADR-NNNN: Title

- Status: Proposed | Accepted | Superseded by ADR-XXXX
- Date: YYYY-MM-DD

## Context
## Decision
## Consequences
## Alternatives considered
```
