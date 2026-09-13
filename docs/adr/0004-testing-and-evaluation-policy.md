# ADR-0004: Unit tests now, eval-lite from P5 Phase C, eval infrastructure in Term E

- Status: Accepted
- Date: 2026-09-13

## Context

- **The rules contradicted each other.** One rulebook deferred all tests to Term E. `AGENTS.md`
  required a test for every node. About 40 tests existed anyway.
- **Evaluation was deferred to the far end.** On 2026-08-19 evaluation was deferred to after
  P12. That leaves months of prompt and routing changes with no way to tell whether a change
  helped.
- **Tracing was on but unused.** LangSmith tracing has been enabled through `.env` all along,
  and nobody has looked at the traces.
- **Mocks hid a bug.** The P5 isolation bug (ADR-0003) passed its test because the test mocked
  the framework.

## Decision

1. **Unit tests for deterministic code.** Routers, backends, adapters, and utilities get unit
   tests in the same stage that writes them.
2. **Real framework at boundaries.** Code at a framework boundary is tested with real framework
   objects (graphs, stores, backends). Only the model is faked, with a scripted fake chat model.
3. **Eval-lite for LLM behavior.** From P5 Phase C on, each project verifies LLM behavior with a
   small scenario set (5-20 cases) and reads the traces.
4. **Heavy infrastructure waits for Term E.** Datasets at scale, CI regression gates, online
   evaluation, and dashboards stay in Term E.
5. **Definition of done.** `uv run pytest` and `uv run ruff check src tests` are green, and the
   stage's live scenario has been run.

## Consequences

- Refactors are safe to make, and bugs at framework boundaries get caught.
- Evaluation grows gradually, one cross-cutting thread in `docs/ROADMAP.md`.

## Alternatives considered

- **No tests until Term E:** rejected, because refactors become unsafe and bugs like
  ADR-0003's slip through.
- **Full evaluation infrastructure now:** rejected as premature; there is nothing stable yet
  to regress against.
