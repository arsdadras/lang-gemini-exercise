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

## Status (2026-09-22)

| Project | State |
| :--- | :--- |
| P1 Research | Done (current scope) |
| P2 RAG | Done |
| P3 Code review | Done |
| P4 Sandbox interpreter + coordinator | Done |
| Stage 0 stabilization | Done 2026-09-13 |
| P5 Memory assistant | **Complete** (2026-09-23, mentor-built at the mentee's request, [ADR-0013](adr/0013-p5-completion.md)): B4 rest, C1 durable SQLite memory, C2 eval-lite (13/13 on one live run), C3 skill designer, C4 context provider and `lab-brief`. 122 tests. Taught again from B4 after R4 |
| **Return pass R0-R5** | In progress: **R0 topic 1, hook delivered** (P1-P4 called like a workflow would; P5 joins the hook's recap). Prediction question pending: which is more dangerous for P6, P4's crash or P2's confident wrong answer? Order R0-R4 -> P5 teaching pass -> R5 -> P6 |
| P6-P12, Term E | Planned (`docs/ROADMAP.md`) |

## Working agreements

- **Code delivery (2026-09-13):** the mentor verifies each component, reverts, and sends the
  lesson code in chat; the mentee types it for practice (tests aren't sent). Before the next
  component, the mentor integrates the verified code and tests into the repo, replacing the
  mentee's copy. The repo is always the mentor's clean version.
- **Evaluation (2026-09-13):** eval-lite starts at P5 Phase C, and LangSmith traces get used
  deliberately ([ADR-0004](adr/0004-testing-and-evaluation-policy.md)).
- **Pacing:** counted in stages (one central lesson each), not weeks
  ([ADR-0009](adr/0009-stage-admission-rule.md)).
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
- **Old checkpoint DB still in place, and still tracked by git.** `src/data/dbs/checkpoints.db`
  couldn't be moved on 2026-09-13 because running Python processes held it open; a consistent
  copy with all 53 threads is at `out/state/checkpoints.db`. The 2026-09-22 audit found it is
  still in the git index (`git ls-files src/data`). Untrack and delete it with the mentee's OK
  (deleting data needs asking) once those processes are closed. Destination: `[R]` R0.
- **Stale RAG index metadata.** `.chroma_index` was built before the restructure, so source
  paths show the old layout. Rebuild when convenient (paced, takes minutes).
- **Shared session list.** All apps share one checkpoint DB, so `list` shows every app's threads.
  Destination: `[R]` R0.
- **Chat template in every agent.** `prompts/template/template.py` is a chat-assistant persona
  (Finglish policy, response-mode codes) applied to every agent, including non-chat subagents.
  Destination: `[R]` R0 (chat vs worker prompts).
- **No shared specialist contract** (audit 2026-09-22): P1 returns a Pydantic report, P2 a
  string, P3 formatted text, P4 text plus an artifact diff. P6-A needs one. Destination: `[R]` R0.
- **Dead code:** `middlewares/groundedness_middleware.py` and `utils/time_travel_util.py` are
  exported but used nowhere. The first gets wired in R1; the second is removed in R5 unless a
  consumer appears.
- **Personal data in traces.** The P5 app masks secrets and emails before upload (B3), but
  conversation content still reaches LangSmith under project `lang_claude_exercise-p1`.
  Consider one project per curriculum project.
- **Perso-Arabic script in long P5 replies.** `gpt-5.6-luna` writes Perso-Arabic in 30-50% of
  the lines of a long plan. B3's repair cuts that by about three quarters (215 leaked lines to
  55 across three plans), but some lines survive two repair passes. The root cause is the
  assistant model itself. Since 2026-09-23 the repair pass itself runs on the `opensource` tier
  (`glm-5.3`, [ADR-0014](adr/0014-weighted-model-tier-catalog.md)); that repair rate hasn't been
  re-measured against the new model. Repair still fails open, so worst case is unchanged.
- **Model catalog restructured (2026-09-23).** 5 tiers now (`high`/`medium`/`low`/`opensource`/
  `free`), a tier's provider order comes from a weighted speed/power/cost score instead of a
  hand-picked one, and OpenRouter is deferred out entirely. [ADR-0014](adr/0014-weighted-model-tier-catalog.md).
  The `opensource` entries (GLM, Qwen, DeepSeek via GapGPT) have no live-verified
  structured-output or function-calling track record in this repo yet; only two low-stakes node
  calls were moved onto that tier so far (see the ADR's call-site audit).
- **A 6th tier, `local` (Ollama), and named `LLM_TEST_PROFILE` values** (`default`/`cheapest`/
  `reliable`/`local`) for switching test mode's tier mid-session without a code change
  ([ADR-0015](adr/0015-local-tier-and-test-mode-profiles.md)). **Measured 2026-09-23** against a
  real `ollama serve` with `qwen3.5:2b` and `qwen3.5:4b` pulled: both work end to end (plain
  chat, structured output, tool-calling), `qwen-4b` is more reliable (only it passed a
  multi-line structured-output task `qwen-2b` failed) and is the tier's primary. Both are far
  too slow for interactive use (90-360s per structured-output call, likely CPU-bound reasoning
  overhead, no GPU confirmed) — kept opt-in only, never in `TEST_TIER` auto-selection. Good for
  patient offline iteration; not a fit for `rag_node`'s per-document grading or the Finglish
  repair pass at that latency. Resolved; see the ADR's follow-up section for the full numbers.
- **Specialist-contract status vocabulary fixed (2026-09-23).** A concurrent session's in-flight
  rename (`success`→`ok`, `failure`→`failed`) had updated every call site and the tests but not
  `SpecialistResult.status`'s `Literal` (still `success/partial/failure/timeout/error`) or
  `to_text()`'s `render` param (no default, but called with none at one call site) — 13 tests
  failed on import/validation. Fixed: `Literal["ok", "partial", "failed"]`, `render: ... | None
  = None`, and `rag_subagent.py`'s wiped `"Answered from the indexed corpus."` reason string
  restored. 139/139 pass now.

## Backlog

Priority tags: **E** = Essential, **N** = Nice-to-have. Destination tags say where an item
lands: a named stage, `[R]` (the return pass before P6, `docs/ROADMAP.md`), or `[deep-dive]`
(an optional standalone session at a project boundary). Items without a tag wait for their
trigger.

**Cross-project**
- **E:** Surface approvals raised inside subagents through composition. P6-B.
- **N:** A typed failure class on the envelope (`failure: transient | permanent`), once a
  caller branches on it (R0 puts it only in `reason`). P6-B2.
- **N:** Model-output errors (structured output that fails validation) as a "recoverable"
  class: today they're indistinguishable from our own bugs by type, so they crash after the
  model fallback. P6-B2.
- **N:** Model callers of `web_search` (P1, the coordinator's researcher) still get Tavily's
  errors as `{"error": ...}` text; `search_results` is used only where code reads results.
  Revisit with the recoverable class. P6-B2.
- **N:** Grow the P5 security guard from a classifier into a generic, policy-parameterized
  security agent once a second consumer needs it (triggers: document prompt injection in P7,
  action permissions in P8/P11), and add tools only if that consumer's judgment needs them.
- **N:** DeepAgents harness profiles, once a fallback model needs different prompts or tool
  descriptions than the primary.
- **N:** Per-app checkpoint databases, or tagging threads by app. `[R]` R0.
- **N:** Carry the typed envelope into a DeepAgents coordinator's state, not only its text:
  extra state keys a `CompiledSubAgent` returns reach the parent (verified in
  `deepagents/middleware/subagents.py`). Coordinator code then lists side effects and reads
  status itself instead of the model copying the `Changed:` line. `[R]` R4.
- **N:** One CLI approval loop (`run_with_hitl` and `stream_with_hitl` overlap). `[R]` R5.
- **N:** Secret redaction and trace masking in every app, not only P5. `[R]` R5.

**P5 Memory assistant**
- **E:** Compare assistant models in C2 (script leakage per line, false "saved" claims, guard
  agreement), since B3's Finglish repair only mitigates the leak.
- **N:** Semantic search over memory (`IndexConfig` on the store, one item per fact or per
  goal file). Not needed while the profile and its goal index fit in the prompt. Trigger:
  memory that can't be loaded whole, such as episodic memory or a goal list too long for the
  profile. Search per fact (a chunk per line with `{file, line}` metadata, as in P2), not per
  file, and keep the index in sync on every write, edit, and delete.
- **N:** After an HITL resume, the streamed CLI prints the approved tool call a second time
  (the middleware re-emits the AI message update). Cosmetic. `[R]` R5.
- **N:** Session-scoped sandbox workspaces or a remote sandbox such as `LangSmithSandbox`
  (Term E, E1).

**P1 Research**
- **N:** P1's report can leak Perso-Arabic script (seen in the `lab-brief` live run); P1 has no
  Finglish repair. `[R]` R1.
- **N:** Check citation groundedness with the `response_groundedness` middleware. `[R]` R1.
- **N:** Decide whether the coordinator's `researcher` spec becomes a `CompiledSubAgent` over
  `run_research`, once a search budget replaces per-search approval (until then every
  delegation would stop at its first search). `[R]` R1.
- **N:** Wire `rag_subagent` into the researcher as a local-knowledge overlay. P6-A (the
  workflow composes P1 and P2 instead).

**P2 RAG**
- **N:** Reroute ungrounded answers to query rewrite or web search instead of a disclaimer.
  `[R]` R2.
- **N:** Run the groundedness check on the web fallback path too. `[R]` R2.
- **N:** Batch document grading. `[R]` R2.
- **N:** Rebuild the stale index; index agents and apps as well. `[R]` R2.
- **N:** Dual-collection embedding fallback (Gemini 3072-dim vs OpenAI 1536-dim).

**P3 Code review**
- **N:** Deterministic static checks (ruff/AST) before the LLM review. `[R]` R3.
- **N:** Multi-file and PR-diff input. `[R]` R3.

**P4 Sandbox**
- **N:** Artifact diff as declared side effects in the contract. `[R]` R4.
- **N:** HITL "edit" decision for commands.
- **N:** Clearer approval prompt formatting. `[R]` R5.
- **N:** Snapshot the sandbox filesystem alongside checkpoints for true time travel.

**Deep-dive candidates** (`[deep-dive]`, optional, one per project boundary)
- None yet. Parked techniques above the current level land here when they have no stage.
