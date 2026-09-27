# Mentor Log

What each project and stage delivered, newest last; append-only. Seeded by the lead on
2026-09-26 from the handoff. Earlier detail: `git show 85f714d:docs/MENTOR_HANDOFF.md` (logs
before 2026-09-13) and the study guides.

| When | Project or stage | Delivered | Record |
| :--- | :--- | :--- | :--- |
| before 2026-09 | P1 Research agent | One DeepAgents agent with search, a structured cited report, fallback, approval before search, a researcher subagent | Handoff history |
| before 2026-09 | P2 RAG agent | Raw `StateGraph`: grading, a corrective loop, checkpoints, streaming, time travel, web fallback, a hallucination check; a coordinator with a retrieval skill | Handoff history |
| before 2026-09 | P3 Code review | Three compiled subgraphs, sandboxed tests, a self-correcting loop, an `interrupt()` gate | [Study guide](../../docs/study_guides/p3_code_review/MASTER_GUIDE.md) |
| before 2026-09 | P4 Sandbox interpreter | Shell workspace with approval, artifacts, durable sessions, the coding coordinator | [Study guide](../../docs/study_guides/p4_sandbox_interpreter/MASTER_GUIDE.md) |
| 2026-09-13 | Stage 0 stabilization | One `agentlab` package, apps as composition root, identity as runtime context, sandbox secret isolation, registry and custom retry removed; 49 tests | [ADR-0001](../../docs/adr/0001-three-phase-project-model.md) to [ADR-0007](../../docs/adr/0007-built-in-model-fallback.md) |
| 2026-09-23 | P5 Memory assistant | Governed per-user memory with one writer, guards, undo, durable SQLite, eval-lite (13/13 on one live run, `EV-2026-09-23-p5-eval-lite`), governed skills, a context provider, `lab-brief`; mentor-built at the learner's request, taught again from B4 after R4 | [ADR-0013](../../docs/adr/0013-p5-completion.md) |
| 2026-09-23 | Model catalog | Five weighted tiers plus `local`, test-mode profiles; the specialist-contract status vocabulary fixed (139 tests) | [ADR-0014](../../docs/adr/0014-weighted-model-tier-catalog.md), [ADR-0015](../../docs/adr/0015-local-tier-and-test-mode-profiles.md) |
| 2026-09-22 on | R0, the specialist contract | Topic 1 (the envelope) delivered; topic 2 (the failure contract) in progress | [STATE.md](STATE.md) |
