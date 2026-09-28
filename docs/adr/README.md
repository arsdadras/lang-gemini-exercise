# Architecture Decision Records

An ADR records one significant decision: the forces behind it, what was decided, what it
costs, and what else was considered. Write one when a decision is hard to reverse,
cross-cutting, or sets a convention, and whenever the user overrides a decision (record the
dissent too). Smaller decisions go only in the lead's
[decision register](../../offices/lead/DECISIONS.md).

**Owner:** the lead writes every ADR, so numbers and quality stay consistent across concurrent
sessions ([ADR-0016](0016-project-office-and-document-governance.md),
[ADR-0018](0018-three-offices-library-and-archive.md)). Other roles send decision and record
requests as messages ([protocol](../../library/governance/protocol.md)). ADRs up to 0015 were
written by mentors, before the office existed. Evidence is cited by research record ID
(`EV-...`, `BR-...`), not by path.

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
| [0013](0013-p5-completion.md) | Finishing P5: history and undo, durable memory, governed skills, a context provider | Accepted |
| [0014](0014-weighted-model-tier-catalog.md) | Model catalog splits into 5 tiers, ranked by a weighted speed/power/cost score | Accepted |
| [0015](0015-local-tier-and-test-mode-profiles.md) | A `local` Ollama tier, and named test-mode profiles switchable mid-session | Accepted |
| [0016](0016-project-office-and-document-governance.md) | A project office owns direction; the mentor teaches; one writer per file | Accepted |
| [0017](0017-production-standards-as-design-yardstick.md) | Production engineering standards are the design yardstick | Accepted |
| [0018](0018-three-offices-library-and-archive.md) | Three offices, a shared library, an archive, and one message protocol | Accepted; amended by ADR-0019, ADR-0022, and ADR-0024 |
| [0019](0019-role-worktrees-hooks-and-handoff.md) | One worktree and branch per role, session hooks, and a /handoff skill | Accepted |
| [0020](0020-ownership-guard-routing-and-message-awareness.md) | An ownership guard, worktree routing, and automatic message awareness | Accepted |
| [0021](0021-decision-models-as-a-second-model-family.md) | Decision models as a second model family, and one standard for every decision point | Accepted |
| [0022](0022-engineer-role-and-division-of-labor.md) | An engineer role: building apart from teaching, research, and review | Accepted; amended by ADR-0023 |
| [0023](0023-active-review-instead-of-typing.md) | The learner reviews verified code instead of typing it | Accepted |
| [0024](0024-a-lead-curated-library-in-five-categories.md) | A library the lead alone writes and curates, in five categories | Accepted |

## Template

```markdown
# ADR-NNNN: Title

- Status: Proposed | Accepted | Rejected | Superseded by ADR-XXXX | Deprecated
- Date: YYYY-MM-DD
- Origin: lead | mentor or research request | user override (dissent under Alternatives)
- Revisit when: (optional) the concrete trigger that reopens this decision

## Context
## Decision
## Consequences
## Alternatives considered
```
