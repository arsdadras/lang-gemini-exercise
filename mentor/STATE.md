# Mentor State

Read first every session; rewrite it, don't append. The charter is [README.md](README.md) and
onboarding is [GEMINI.md](../GEMINI.md); since [ADR-0028](../docs/adr/0028-one-mentor-one-branch.md)
the mentor is the only role and works on `main`.

- **Mentor Transition (2026-10-11):** Forked to `D:\Repos\lang-gemini-exercise`
  (`arsdadras/lang-gemini-exercise.git`). Historical records up to `d697945` were authored by the
  previous mentor (Claude); from this point forward **Gemini (Antigravity)** is the sole Mentor and
  maintains all code, curriculum, and `mentor/` records directly. See also
  [product ideas & refinements](../docs/gemini/feedbacks/product_ideas_and_refinements.md).
- **Architectural Unification & Phases 1-3 Completed (2026-10-12, [ADR-0033](../docs/adr/0033-wave-particle-duality-and-workflow-specialist-layer.md), DEC-039):**
  Implemented the 4-scale Wave-Particle Duality architecture in `src/agentlab/`:
  - **Phase 1:** Added `RagReport`, `InterpreterReport` (with `deliverables: list[Deliverable]`),
    `PersonalContextReport`, and `SpecialistName` in `src/agentlab/schemas/output/`, plus typed
    `*Input` schemas in `src/agentlab/schemas/input/`.
  - **Phase 2:** Created `src/agentlab/workflows/` (`specialist_workflow.py` with the frozen
    `Specialist[TInput, TReport]` descriptor, `research_workflow.py`, `rag_workflow.py`,
    `code_review_workflow.py`, `interpreter_workflow.py`, `personal_context_workflow.py`,
    `personal_brief_workflow.py`), turned `src/agentlab/subagents/` into thin adapters over
    `workflows/`, upgraded `make_researcher_subagent` to delegate through `run_research` (the full
    R1 verification pipeline), added `subagents/personal_context_subagent.py`, and removed the 4
    scattered `NewType` wrappers (`Researcher`, `RagGraph`, `CodeReviewGraph`, `Interpreter`).
  - **Phase 3:** Promoted Rung-0 privacy/redaction helpers (`personal_data_redaction`,
    `configure_trace_masking`, `PERSONAL_DATA_TYPES`) into `utils/secret_redaction_util.py` and
    added HITL interrupt propagation + `Command(resume=...)` forwarding inside `nodes/research_node.py`
    when `research_graph` is compiled with a checkpointer.

## Now & Execution Schedule (Multi-Session Master Plan)

- **Done:** R1 closed (2026-10-11); R1->R2 CI & repo hardening closed (2026-10-11); ADR-0033
  governance, pedagogy, `.agents/skills/` rehabilitation, `.agents/hooks.json` session hook, and
  **Phases 1-3 code implementation** completed (2026-10-12); **Test suite review & hardening**
  completed (2026-10-14: 393 tests green, 92% coverage across repo, 88 files with 100% complete
  coverage, 0 ruff/mypy/docs errors across 139 source files).
- **Foundational Refinements Topics 1-3 Completed (2026-10-14):**
  1. *Target & Pre-composition Unification:* In `run_research`, target was unified to accept
     `engine: CompiledStateGraph` with `make_research_graph` providing factory-time composition,
     while maintaining backward-compatible adaptation for leaf worker agents.
  2. *Relocated `Specialist` Descriptor:* Moved `Specialist` out of `workflows/specialist_workflow.py`
     into foundational [`src/agentlab/workflows/base.py`](file:///D:/Repos/lang-gemini-exercise/src/agentlab/workflows/base.py),
     eliminating the category error and leaving `specialist_workflow.py` as a re-export shim.
  3. *Eliminated `_resolve_target` Reflection Hack & Introduced `WorkflowRunner` Protocol:*
     Replaced `inspect.signature` with `WorkflowRunner[TReport](Protocol)` and modern Python 3.12
     generics (PEP 695), removing runtime reflection overhead and enforcing type safety.
  4. *Consultant Hook & Skill (`/consultant` / `/cansultant`):* Implemented `scripts/mentor_session_hook.py`
     detection of consultant commands, diff extraction since last checkpoint (`mentor/.consultant_checkpoint.json`),
     `scripts/record_consultant_checkpoint.py`, and `.agents/skills/consultant/SKILL.md` (396 tests green).
  5. Git author identity configured globally and locally to `arsdadras` matching the primary GitHub account.
- **NEXT SESSION — Topic 4 Refinement & Transition to R2:**
  1. **Topic 4 (Unified Capability / Extension Protocol):** Design, teach, and implement a typed
     `Capability` / `Extension` protocol for Rung-1 engines (`create_deep_agent` and `build_graph`)
     so attachments (subagents, tools, middlewares, subgraphs) are declared polymorphically rather
     than wired ad-hoc.
  2. Verify all checks (`pytest`, `ruff`, `mypy`, `check_docs`).
  3. Launch **Session R2 (P2 RAG — Top-Down Return Pass)** from the mountain-peak perspective:
     P2 design card, hybrid retrieval, query rewrite, Jev chunk grading/reranking, and per-claim verification.
- **SUBSEQUENT SESSIONS — Remaining Return Pass Stages:**
  - **Session R3 (P3 Code Review):** Vertical preventative hardening over `code_review_workflow.py`.
  - **Session R4 (P4 Interpreter):** Vertical preventative hardening over `interpreter_workflow.py`.
  - **Session P5 Pass:** `personal_context_workflow.py` + Rung-0 memory governance.
  - **Session R5 Close:** Coordinator pre-router across all 5 `Specialist` contracts, unified practice scenario, first teach-back.

## Build queue

1. **Foundational Architectural Refinement & Teaching (Next):** Implement, verify, and teach the 4
   agreed refinements (pre-composed `ResearchGraph` target in `run_research`, relocate `Specialist`
   descriptor, eliminate `_resolve_target` via `Protocol`, unified `Capability` protocol).
2. **R2 Session:** Write the P2 design card (points 16-17, Wave/Particle density) and
   build/teach **R2** over `rag_workflow.py` (`RagReport`).
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

- **Coordinator shell has no approval step:** approvals raised inside a subagent aren't surfaced
  to the CLI; the banner states it. Fix: P7-B3 (research workflow HITL fixed in Phase 3 of
  ADR-0033).
- **RAG index:** rebuilt 2026-10-08 (1536-dimensional) and copied to the main checkout.
- **Unused code:** `utils/time_travel_util.py` has no consumer outside a test; removed in R5
  unless one appears.
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
