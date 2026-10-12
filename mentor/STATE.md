# Mentor State

Read first every session; rewrite it, don't append. The charter is [README.md](README.md) and
onboarding is [GEMINI.md](../GEMINI.md); since [ADR-0028](../docs/adr/0028-one-mentor-one-branch.md)
the mentor is the only role and works on `main`.

- **Mentor Transition (2026-10-11):** Forked to `D:\Repos\lang-gemini-exercise`
  (`arsdadras/lang-gemini-exercise.git`). Historical records up to `d697945` were authored by the
  previous mentor (Claude); from this point forward **Gemini (Antigravity)** is the sole Mentor and
  maintains all code, curriculum, and `mentor/` records directly. See also
  [product ideas & refinements](../docs/gemini/feedbacks/product_ideas_and_refinements.md).
- **Architectural Unification & Session Plan Locked (2026-10-12, [ADR-0033](../docs/adr/0033-wave-particle-duality-and-workflow-specialist-layer.md), DEC-039):**
  Codified the 4-scale Wave-Particle Duality paradigm (`Agent/Graph` at Rung 1,
  `Specialist/Workflow` at Rung 2, `Coordinator/Operation` at Rung 3 over shared Rung-0
  infrastructure), the Top-Down Compressor Balancing pedagogy for the Return Pass, Antigravity
  skills in `.agents/skills/`, and the `PreInvocation` session hook in `.agents/hooks.json`
  (`scripts/mentor_session_hook.py`).

## Now & Execution Schedule (Multi-Session Master Plan)

- **Done:** R1 closed (2026-10-11); R1->R2 CI & repo hardening closed (2026-10-11); ADR-0033
  governance, pedagogy, `.agents/skills/` rehabilitation, and `.agents/hooks.json` session hook
  completed (2026-10-12).
- **NEXT SESSION — Dedicated Infrastructure & Architectural Adaptation Session (Phases 1-3 of [ADR-0033](../docs/adr/0033-wave-particle-duality-and-workflow-specialist-layer.md)):**
  Execute Phases 1 to 3 in a single dedicated engineering session **before** starting R2 lessons:
  1. **Phase 1 — Unified `*Report` Schemas & `Specialist[TInput, TReport]` Contract:**
     - Add `RagReport` (`answer`, `citations`, `retrieval_mode`, `grounding_verdict`),
       `InterpreterReport` (`answer`, `executed_commands`, `deliverables`), and
       `PersonalContextReport` (`profile_summary`, `relevant_facts`, `active_preferences`,
       `active_skills`) under `src/agentlab/schemas/output/`.
     - Define the flat, lightweight `Specialist[TInput, TReport]` descriptor in
       `src/agentlab/schemas/output/specialist_output_schema.py` (`name`, `description`,
       `input_schema`, `report_schema`, `run`, `as_subagent`, `as_tool`).
  2. **Phase 2 — `src/agentlab/workflows/` Package & `subagents/` Cleanup:**
     - Create `src/agentlab/workflows/` (`research_workflow.py`, `rag_workflow.py`,
       `code_review_workflow.py`, `interpreter_workflow.py`, `personal_context_workflow.py`,
       `personal_brief_workflow.py`) sitting above `agents/` and `graphs/`.
     - Move `run_research`, `run_rag`, `run_code_review`, and `run_interpreter` from `subagents/`
       into `workflows/*_workflow.py` (with re-exports in `subagents/` only if needed during
       transition, updating all callers in `apps/`, `evals/`, and `tests/`).
     - Turn `subagents/*_subagent.py` into thin adapters over `workflows/`; upgrade
       `make_researcher_subagent` so it delegates through `run_research` (the full R1 verification
       workflow) instead of the raw `Researcher` agent; add
       `subagents/personal_context_subagent.py`.
     - Remove the inverted `NewType` definitions (`Researcher`, `RagGraph`, `CodeReviewGraph`,
       `Interpreter`) that were scattered across `nodes/`, `graphs/`, and `agents/` only to work
       around the old `subagents/` import constraint.
  3. **Phase 3 — Rung-0 Infrastructure Decoupling & Research HITL Propagation:**
     - Decouple Rung-0 Memory/Store/Security/Redaction helpers so any workflow or node can consume
       them as repo-wide infrastructure rather than P5-private helpers.
     - Fix outbound-search HITL interrupt propagation inside `research_workflow.py` so approvals
       reach the caller cleanly.
- **SUBSEQUENT SESSIONS — Phase 4 (Separate Fresh `/mentor` Sessions per `R` Stage / Part):**
  Each Return Pass stage (or sub-part of a stage) runs in its own fresh `/mentor` session, taught
  top-down from the mountain peak using the Compressor Balancing rule
  ([pedagogy](../library/teaching/pedagogy.md#top-down-mountain-peak-perspective-and-the-compressor-balancing-rule-return-pass)):
  - **Session R2 (P2 RAG):** Write P2 design card (points 16-17, Wave/Particle density) and
    build/teach R2 over `rag_workflow.py` (`RagReport`): hybrid search (BM25 + vector + reranker),
    query rewriting, single-request grading/reranking in `Jev`, per-claim verification with
    reroutes, and incremental re-indexing.
  - **Session R3 (P3 Code Review):** Vertical preventative hardening over
    `code_review_workflow.py` (`CodeReviewReport`): deterministic `ruff`/AST pass first, `Jev`
    decider severity/category labeling second, LLM explanation third.
  - **Session R4 (P4 Interpreter):** Vertical preventative hardening over
    `interpreter_workflow.py` (`InterpreterReport`), risk label on `execute` approval, declared
    side effects.
  - **Session P5 Pass:** Practical walk-through and verification of `personal_context_workflow.py`
    (`PersonalContextReport`) + Rung-0 memory governance (B4-C4: 3-check fail-closed guard,
    staleness pre-pass, recall ranking, schema compiler).
  - **Session R5 Close:** Coordinator pre-router on a labeled set across all five `Specialist`
    contracts (`P1`-`P5`), unified practice scenario, and the first teach-back.

## Build queue

1. **Next Session (Phases 1-3):** Execute the 3-phase architectural adaptation in `src/agentlab/`
   (`schemas/output/`, `workflows/`, `subagents/`, `apps/`, `tests/`) and verify 100% green on
   `pytest`, `ruff`, `mypy`, and `check_docs.py`.
2. **R2 Session:** Write the P2 design card (with point 16, production path, and point 17, decision
   points) and build/teach **R2** over `rag_workflow.py`.
3. A live end-to-end run of the research workflow; the depth budgets are provisional until real
   broad runs measure them (`DEPTH_BUDGETS`).
4. Grow the claim-check labeled set from 34 to 50 cases (200 before fitting thresholds), fit
   `SUPPORTS_THRESHOLD` and `CONTRADICTS_THRESHOLD`, and decide whether Jev (91.2%) or Gemini 3.5
   Flash-Lite (34/34, 20 s p95) is primary
   ([EV-2026-10-05-claim-check-jev](research/evidence/EV-2026-10-05-claim-check-jev/README.md),
   [EV-2026-10-05-claim-check-flash-lite](research/evidence/EV-2026-10-05-claim-check-flash-lite/README.md)).
5. The roadmap v5 renumbering sweep in live files (P6 is the content generator).
6. The P6 design card, from the learner's details, before P6.

## Working agreements

- **Language & Persian Bidi Formatting:**
  - When the learner writes in Persian script or during lessons (DEC-034, 2026-10-07), reply in
    Persian script following [`.agents/skills/teach/persian.md`](../.agents/skills/teach/persian.md):
    every paragraph and heading MUST start with `RLM` (`U+200F`) + a Persian word (never markdown
    bullets `- ` or `1. ` or an English character at line start), and every inline English term,
    code span, or markdown link MUST be wrapped in `RLM + LRI ... PDI + RLM` (`fa_isolate.py`).
  - When the learner writes in Finglish, reply in Finglish (or Persian with strict bidi isolation).
    Technical words and code always stay in English.
- **Honesty & Independent Spine (Principle 1 — `Asl-e Ghorur`):**
  - Zero flattery and zero automatic agreement (`tayid-e alaki`).
  - Never flip-flop because of an earlier session's or Claude's opinion; judge strictly on
    first-principles production engineering.
  - Even when a proposal is strong, always provide constructive engineering critique (edge cases,
    failure modes, trade-offs) and precise terminology rather than echoing imprecise phrasing.
- **Decide, Don't Ask (Principle 10):**
  - Never end a message by asking "what do you want to do next?" or handing open architectural
    choices to the user. Decide, justify, and state the concrete action or next lesson step.
- **Top-Down Return Pass & Lesson Shape (2026-10-09 & 2026-10-12):**
  - Start every `R` stage from the mountain peak (`Workflow` film script + `Specialist` contract +
    Wave/Particle density).
  - Apply the Compressor Threshold: vertical preventative hardening for `P2`-`P4`, horizontal
    specialist completion for `P5`.
  - Concepts and core code in depth; preventative engineering mindset explained clearly; routine
    plumbing summarized in 2 lines with clickable file links. No trailing questions, and no tests,
    observe, eval, demo, or hands-on steps unless the learner asks. "edame" means go on to the
    next step.
- **Every change reported (2026-10-06):** each file added, changed, or deleted is named as a
  clickable link with its path, with what and why; each new function that matters gets one or
  two lines ([charter](README.md#reporting-every-change)).
- **Code delivery:** the mentor builds and verifies; the learner reviews the code in lessons
  ([ADR-0023](../docs/adr/0023-active-review-instead-of-typing.md)) and writes code only by
  choice, in `alireza/`.
- **The learner reads the main checkout (2026-10-11):** the IDE opens
  `D:\Repos\lang-gemini-exercise`. Work happens there, on `main`.
- **Git:** everything on `main`, pushed at the end of each session
  ([git policy](../library/engineering/git-policy.md)).
- **Test-mode ladder (2026-10-08, ADR-0031):** `LLM_TEST_MODE=true` per command (`.env` is never
  edited). Default is Gemini 3.5 Flash-Lite; if a weak result is caused by the model, step up one
  rung at a time: `LLM_TEST_PROFILE=strong` (Claude Haiku 5.5, then GPT-6 Luna), then `strongest`
  (Gemini 3.8 Flash, Claude Sonnet 5.5, GPT-6.1 Sol).
- **Scratch area:** `alireza/` is the learner's; never read, reference, or sync it.

## Live code issues

Program-level debt is the [BACKLOG](BACKLOG.md); these are the code's.

- **Architectural inconsistencies scheduled for next session (Phases 1-3, ADR-0033):**
  - `run_*` workflows currently live inside `subagents/*_subagent.py` instead of `workflows/*_workflow.py`.
  - `make_researcher_subagent` wraps the raw `Researcher` agent instead of `run_research`.
  - P2 (`rag_subagent.py`) and P4 (`interpreter_subagent.py`) return `SpecialistResult[str]` instead of `RagReport` / `InterpreterReport`, and P5 (`user_context_tool.py`) returns raw `dict[str, str]` instead of `PersonalContextReport`.
  - Outbound-search HITL interrupts inside `research_node.py` are caught as problems instead of propagating cleanly through `research_workflow.py` (fixed in Phase 3).
- **Coordinator shell has no approval step:** approvals raised inside a subagent aren't surfaced
  to the CLI; the banner states it. Fix: P7-B3 (research workflow HITL fixed in Phase 3).
- **RAG index:** rebuilt 2026-10-08 (1536-dimensional) and copied to the main checkout.
- **Unused code:** `utils/time_travel_util.py` has no consumer outside a test; removed in R5
  unless one appears.
- **Personal data in traces:** only P5 masks before upload; promoted to Rung-0 in Phase 3 / R5.
- **Perso-Arabic script in long P5 replies:** the repair cuts leaked lines by about three
  quarters (`EV-2026-09-17-finglish-line-repair`); its current model isn't re-measured.
- **`local` tier is opt-in only:** 90-360 s per structured call
  (`EV-2026-09-23-local-ollama-qwen`, [ADR-0015](../docs/adr/0015-local-tier-and-test-mode-profiles.md)).
- **`_TimeoutSearchWrapper`** (`tools/web_search_tool.py`) works around langchain-tavily setting
  no timeout; remove it once the library takes one (`tests/test_timeouts.py` shows what to check).
- **The researcher cites pages it never read:** on 2026-10-07 Gemini 3.5 Flash-Lite called
  `read_page` 0 or 1 times in 6 single runs and cited search results instead; the claim check
  marks those claims unsupported. Next build: a gate that hands a draft citing unread pages back to
  the model before it can finish ("send back, don't drop").
- **Jev model router (2026-10-08, ADR-0031):** built and unit-tested (`chain`, `runnable`, `plan`),
  never run live. Three GapGPT IDs are unverified (`claude-haiku-5-5`, `gpt-6-luna`, `gpt-6.1-sol`).
- **No retry layer on the agents' tools:** convention 11 asks for `ToolRetryMiddleware` on an
  agent's external tools; no agent has one. Decide with the engineering track.
- **The claim check's cost has no hard cap:** it checks every drafted claim before the cap,
  bounded only by the agent prompt's "at most N".

## Research queue

Recorded in [research/](research/CATALOG.md) when done.

- An upstream-watch routine over the pinned stack's releases and the radar's watched items.
- BR-002's measurements, and LangSmith Sandboxes for P4.
- Decision-accuracy techniques for Jev (question wording, decomposition, answer sets) on our
  labeled sets. Replaying our own sessions needs the learner's yes (DEC-025).
- Reconcile the consolidator records (ADR-0014's erratum vs ADR-0012,
  `EV-2026-09-19-consolidator-model-comparison`).
- The teaching-method questions in
  [synthesis, section 5](attachments/teaching-research/synthesis.md#5-open-questions-worth-a-verified-study).

## Reserved for the learner

- `PERPLEXITY_API_KEY` or `EXA_API_KEY` for R1 topic 3's research-API source.
- The yes before a development-loop hook sends session content to a hosted decider (DEC-025).

## Review items

Gaps from review questions and teach-backs
([review-items table](../.agents/skills/teach/materials.md#review-items-table)): none recorded.
