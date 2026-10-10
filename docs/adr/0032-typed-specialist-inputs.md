# ADR-0032: A specialist takes the type its factory returns

- Status: Accepted
- Date: 2026-10-11
- Origin: the learner's question (2026-10-11): after the researcher was typed (DEC-038), are
  other agents, graphs, or chains injected under a type wider than the one their consumer
  really needs?
- Revisit when: a type checker runs in CI (backlog), so the static half is enforced; or a
  second implementation of one of these roles appears, which would call for a `Protocol`
  instead of a `NewType`.

## Context

A specialist boundary (`run_*`) and a node factory read keys that only one factory produces:
`run_rag` reads `answer`, `answer_source`, and `chunks`; `run_code_review` reads `review`,
`tests`, `test_run`, `applied_code`, and `error`; `run_interpreter` diffs the sandbox the
interpreter agent writes to; the research node reads `structured_response`. Each took
`Runnable`, so any runnable passed the annotation and a wrong one failed only at run time, often
quietly (an empty answer, no side effects). Injected structured-output chains had the same gap:
`verdict_chain: Runnable` said nothing about returning a `ClaimVerdict`.

## Decision

1. A compiled graph or agent whose consumers read its particular state gets a `NewType` over
   `CompiledStateGraph`, returned by its one factory and required by every consumer:
   `Researcher` (`nodes/research_node.py`), `RagGraph` (`graphs/rag_graph.py`),
   `CodeReviewGraph` (`graphs/code_review_parentgraph.py`), and `Interpreter`
   (`subagents/interpreter_subagent.py`). Each type lives at the lowest layer that uses it, so
   imports still point downward.
2. An injected chain is typed by what it returns: `Runnable[Any, ClaimVerdict]`,
   `Runnable[Any, ResearchPlan]`, `Runnable[Any, MemoryEdits]`, `Runnable[Any, SkillDraft]`,
   `Runnable[Any, GuardVerdict]`, `Runnable[Any, FinglishLines]`. These come from the generic
   `llm_model.chain(structured=...)`, so the generic parameter, not a `NewType`, is the honest
   tool.
3. Code that works on any graph keeps the wide type: the HITL loop, streaming, sessions, time
   travel, and the memory session helper.

## Consequences

- The signature states the contract; passing the RAG graph where the code-review graph belongs
  is visible in the IDE and, once one runs, to a type checker.
- No run-time cost or wrapper: `NewType` returns its argument, so `.invoke`, `.stream`, and
  `get_state` keep working at every call site.
- The guarantee is static only. Tests that build through the real factory (the researcher's
  contract test, `build_rag_graph` and `build_code_review_graph` in the specialist tests) cover
  the run-time half. Scripted fakes in tests are not wrapped: they are not compiled graphs, so
  wrapping them would only pretend.

## Alternatives

- A Pydantic or dataclass wrapper: a run-time layer and an `.agent` unwrap at every call site,
  for no check `NewType` doesn't already give statically. Rejected.
- A `Protocol` per role: right when two implementations of one role exist; today each role has
  one factory. Deferred to that trigger.
