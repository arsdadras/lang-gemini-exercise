# Mentor Handoff

Read first, every session. This file holds the **current state only**; keep it short and
rewrite it, don't just append.
Rules: `docs/MENTORING.md`. Mechanics: `AGENTS.md`. Plan: `docs/ROADMAP.md`.
Full history before 2026-09-13 (Claude and Gemini logs): `git show 85f714d:docs/MENTOR_HANDOFF.md`.

## Mentors

- P1-P2: Claude Sonnet 5
- P3: Gemini Flash 3.7
- P4 through P5 Phase B Stage 1: Gemini Flash 3.8
- From 2026-09-13: Claude Opus 5, with full authority over plan and process

## Status (2026-09-13)

| Project | State |
| :--- | :--- |
| P1 Research | Done (current scope) |
| P2 RAG | Done |
| P3 Code review | Done |
| P4 Sandbox interpreter + coordinator | Done |
| Stage 0 stabilization | Done 2026-09-13 |
| **P5 Memory assistant** | A done, B1 (skills) done. **Next: Phase B intro, then B2 brief** |
| P6-P12, Term E | Planned (`docs/ROADMAP.md`) |

## Working agreements

- **Code delivery (2026-09-13):** the mentor sends verified code in chat and the mentee applies
  it. The mentor edits the repo directly only for docs, hygiene, and delegated fixes.
- **Evaluation (2026-09-13):** eval-lite starts at P5 Phase C, and LangSmith traces get used
  deliberately ([ADR-0004](adr/0004-testing-and-evaluation-policy.md)).
- **Pacing:** default 1-2 weeks per project, adjusted together.
- **Scratch area:** `alireza/` (notebooks, practice files) is the mentee's scratch paper.
  Never read, reference, or sync it.

## Stage 0 summary (2026-09-13)

- **Correctness.** P5 memory was shared by every user; identity now travels as runtime context
  ([ADR-0003](adr/0003-runtime-context-for-user-identity.md)). Verified with a real-graph test
  and a live two-user run.
- **Security.** The sandbox shell and test subprocesses got every `.env` secret; they now get an
  allow-listed environment. The repo-insight agent is denied `.env` reads and all writes
  ([ADR-0005](adr/0005-sandbox-secret-isolation.md)).
- **Structure.**
  - One `agentlab` package with `lab-*` scripts.
  - No construction at import time; apps are the composition root.
  - Runtime state moved to `out/state/`, and `checkpoints.db` is no longer tracked
    ([ADR-0002](adr/0002-single-package-and-composition-root.md)).
  - `output_schemas/` and `state/` merged into `schemas/{output,state,context}` — one reference
    location for every typed contract, grouped by role rather than by construction method.
  - `utils/subagent_util.py` and `utils/sandbox_util.py`'s `snapshot_sandbox_artifacts`/
    `diff_sandbox_artifacts` extract the plumbing that was identically duplicated across the
    3 `subagents/*.py` adapters and across `interpreter_app.py`/`interpreter_subagent.py`
    (the interactive app previously missed `[MODIFIED]` artifacts; it now reports them too).
- **Removed.** The unused agent registry ([ADR-0006](adr/0006-remove-agent-registry.md)), the
  custom retry middleware (replaced by the built-in, [ADR-0007](adr/0007-built-in-model-fallback.md)),
  and the dead `ExecutionManifest` and sandbox-type stubs.
- **Governance.** One short contract (`docs/MENTORING.md`) replaced the two rulebooks; Phase D
  was dropped ([ADR-0001](adr/0001-three-phase-project-model.md)). Roadmap v3 replaced v1/v2 and
  the Term E doc. `CLAUDE.md` loads `AGENTS.md` and the contract. `docs/MENTORING.md` also now
  has a "When to build ahead of need" section (observed-vs-predicted shape, plumbing-vs-policy,
  reversibility, teaches-the-curriculum-or-not) for the extract-now-vs-later call that recurs
  every project.
- **Tests.** 49 passing, including new model-registry, env-isolation, real-graph memory,
  sandbox-diff, and subagent-plumbing tests. The `core` tests had been testing the scratch
  copy under `alireza/temps`.

## Known issues and risks

- **Coordinator shell has no approval step.** The coordinator's interpreter runs shell commands
  without per-command approval, because approvals raised inside a subagent aren't surfaced to
  the CLI. The banner states this. Fix: P6 Phase B.
- **Old checkpoint DB still in place.** `src/data/dbs/checkpoints.db` couldn't be moved on
  2026-09-13 because running Python processes (probably notebook kernels) held it open. A
  consistent copy with all 53 threads is at `out/state/checkpoints.db`. Delete `src/data/`
  once those processes are closed.
- **Stale RAG index metadata.** `.chroma_index` was built before the restructure, so source
  paths show the old layout. Rebuild when convenient (paced, takes minutes).
- **Shared session list.** All apps share one checkpoint DB, so `list` shows every app's threads.
- **Chat template in every agent.** `prompts/template/template.py` is a chat-assistant persona
  (Finglish policy, response-mode codes) applied to every agent, including non-chat subagents.
  Revisit with the P6 contracts.
- **Personal data in traces.** LangSmith tracing is on for all runs, including P5 personal
  data, under project `lang_claude_exercise-p1`. Consider one project per curriculum project.
- **Placeholder skills.** P5 ships coding SOPs (`python-pro`, `clean-committer`) instead of
  assistant-domain skills. Replace them in B2.

## Backlog

Priority tags: **E** = Essential, **N** = Nice-to-have.

**Cross-project**
- **E:** Surface approvals raised inside subagents through composition (P6 Phase B).
- **N:** Per-app checkpoint databases, or tagging threads by app.
- **N:** Session-scoped sandbox workspaces or a remote sandbox such as `LangSmithSandbox`
  (Term E, E1).

**P1 Research**
- **E:** Memory for recurring research preferences (original Phase B item; fits after P5).
- **N:** Wire `rag_subagent` into the researcher as a local-knowledge overlay.
- **N:** Check citation groundedness with the `response_groundedness` middleware.

**P2 RAG**
- **N:** Reroute ungrounded answers to query rewrite or web search instead of a disclaimer.
- **N:** Run the groundedness check on the web fallback path too.
- **N:** Batch document grading.
- **N:** Index agents/apps as well (batching now keeps the rebuild within rate limits).
- **N:** Dual-collection embedding fallback (Gemini 3072-dim vs OpenAI 1536-dim).

**P3 Code review**
- **N:** Multi-file and PR-diff input.
- **N:** Deterministic static checks (ruff/AST) before the LLM review.

**P4 Sandbox**
- **N:** HITL "edit" decision for commands.
- **N:** Clearer approval prompt formatting.
- **N:** Snapshot the sandbox filesystem alongside checkpoints for true time travel.

**P5 Memory assistant**
- Planned stages are tracked in `docs/ROADMAP.md`. Nothing extra logged yet.
