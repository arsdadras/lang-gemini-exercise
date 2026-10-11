# Mentor State

Read first every session; rewrite it, don't append. The charter is [README.md](README.md) and
onboarding is [GEMINI.md](../GEMINI.md); since [ADR-0028](../docs/adr/0028-one-mentor-one-branch.md)
the mentor is the only role and works on `main`.

- **Mentor Transition (2026-10-11):** Forked to `D:\Repos\lang-gemini-exercise`
  (`arsdadras/lang-gemini-exercise.git`). Historical records up to `d697945` were authored by the
  previous mentor (Claude); from this point forward **Gemini (Antigravity)** is the sole Mentor and
  maintains all code, curriculum, and `mentor/` records directly. See also
  [product ideas & refinements](../docs/gemini/feedbacks/product_ideas_and_refinements.md).

## Now

- **R1 closed (2026-10-11):** All 4 topics of R1 (a stronger researcher: claims with provenance,
  options and `Send` query planning, multi-source routing over web/corpus/academic with
  `SourceRouteMiddleware`, and `EvidenceStopMiddleware` with `evidence_enough@1`) are built and
  taught ([design card](../docs/design_cards/P1_research_agent.md)).
- **R1 -> R2 inter-stage CI & repo hardening (2026-10-11):**
  - Added `mypy src/agentlab` to `.github/workflows/ci.yml` (0 errors across 125 source files),
    added `pull_request` triggers, and merged Dependabot updates (`langchain 1.4.3`,
    `langgraph 1.2.14`, `deepagents 0.7.20`, `ruff 0.16.10`, `python-dotenv 1.2.4`).
  - Applied review refinements: P3 sandbox tests now verify `review.refactored_code` when present;
    R1 `page_window` extracts windows around cited passages past 12,000 chars and `_merge`
    deduplicates identical claims while combining their `evidence` lists; `ModelRouter.runnable()`
    enables LCEL `PROMPT | model_router.runnable(...)` routing on full rendered prompt length;
    `lab-research` exposes `--depth {quick,standard,deep}` and `verify_research` applies the
    depth's claim cap; chat models set `max_retries=1` (`CHAT_MODEL_MAX_RETRIES`) so provider SDK
    retries don't stack before fallback; `smoke_live.py` wraps `plain()` and `tools()` with
    fallbacks; `sqlite_db_data.py` provides `prune_checkpoints` + `VACUUM`.
- **Now: R2, a stronger retriever (P2):** Next stage to start ([ROADMAP](ROADMAP.md), v5):
  hybrid search (BM25 + vector + reranker), query rewriting, grading and reranking in one decider
  request, per-claim verification with reroutes, and incremental re-indexing. Then R3 -> R4 -> P5
  teaching pass (B4 to C4) -> R5 -> D1 -> P6 (content generator) -> P7 (Capstone I).

## Build queue

1. Write the P2 design card (with point 16, production path, and point 17, decision points) and
   build/teach **R2** (hybrid search, reranking, query rewriting, single-request grading/reranking,
   per-claim verification with reroutes, incremental re-index).
2. A live end-to-end run of the research agent; the depth budgets are provisional until real broad
   runs measure them (`DEPTH_BUDGETS`).
3. Grow the claim-check labeled set from 34 to 50 cases (200 before fitting thresholds), fit
   `SUPPORTS_THRESHOLD` and `CONTRADICTS_THRESHOLD`, and decide whether Jev (91.2%) or Gemini 3.5
   Flash-Lite (34/34, 20 s p95) is primary
   ([EV-2026-10-05-claim-check-jev](research/evidence/EV-2026-10-05-claim-check-jev/README.md),
   [EV-2026-10-05-claim-check-flash-lite](research/evidence/EV-2026-10-05-claim-check-flash-lite/README.md)).
4. The roadmap v5 renumbering sweep in live files (P6 is the content generator).
5. The P6 design card, from the learner's details, before P6.
6. The repo-level engineering track (ADR-0027, decision 5): redaction and masking,
   observability, timeouts, contract conformance (`UserContext`, one approval path, declared
   side effects, an eval-lite set per specialist).

## Working agreements

- **Language:** communicate with the learner in Finglish (Persian in Latin characters, per global
  user rules, unless the learner explicitly requests otherwise); technical words and code stay
  English; every concept starts from an example.
- **Lesson shape (the learner's repeated instruction):** concepts and core code only. No
  trailing questions, and no tests, observe, eval, demo, or hands-on steps unless the learner
  asks. "edame" means go on to the next step.
- **Every change reported (2026-10-06):** each file added, changed, or deleted is named as a
  clickable link with its path, with what and why; each new function that matters gets one or
  two lines ([charter](README.md#reporting-every-change)).
- **Critique:** a design objection from the learner is judged on its merits, conceded where it
  holds and argued where it doesn't (principle 1), and a fix that holds is built, tested, and
  pushed in the same session.
- **Code delivery:** the mentor builds and verifies; the learner reviews the code in lessons
  ([ADR-0023](../docs/adr/0023-active-review-instead-of-typing.md)) and writes code only by
  choice, in `alireza/`.
- **The learner reads the main checkout (2026-10-11):** the IDE opens
  `D:\Repos\lang-gemini-exercise`. Work happens there, on `main`.
- **Git:** everything on `main`, pushed at the end of each session
  ([git policy](../library/engineering/git-policy.md)).
- **A weak result because of the model (2026-10-08, ADR-0031):** test mode is a ladder, one
  rung at a time and only when the rung below was not enough: `LLM_TEST_PROFILE=strong`
  (Claude Haiku 5.5, then GPT-6 Luna), then `strongest` (Gemini 3.8 Flash, Claude Sonnet 5.5,
  GPT-6.1 Sol). Each model is called on GapGPT, then OpenRouter, never on Google; if the
  rung fails, keep the result of the rung below.
- **Live runs:** test mode per command (`LLM_TEST_MODE=true`); `.env` is never edited. Test mode
  calls Gemini 3.5 Flash-Lite through GapGPT, then OpenRouter, then Google's API (the learner's
  direction, 2026-10-08). Jev's key is `TYPESAFE_API_KEY`; Exa's is `EXA_API_KEY`.
- **Scratch area:** `alireza/` is the learner's; never read, reference, or sync it.

## Live code issues

Program-level debt is the [BACKLOG](BACKLOG.md); these are the code's.

- **Coordinator shell has no approval step:** approvals raised inside a subagent aren't surfaced
  to the CLI; the banner states it. Fix: P7-B3.
- **RAG index:** rebuilt 2026-10-08 (1536-dimensional) and copied to the main checkout.
- **Approvals inside the research graph:** an outbound search waits for approval, and the
  research node reports a waiting run as a problem instead of surfacing the interrupt, so
  `run_research` with the approval gate on stops at the first search; live runs replace the gate
  in the script. Fix: run the agent as a subgraph so its interrupts reach the caller (with P7-B3).
- **Unused code:** `utils/time_travel_util.py` has no consumer outside a test; removed in R5
  unless one appears.
- **Personal data in traces:** only P5 masks before upload. Engineering track.
- **Perso-Arabic script in long P5 replies:** the repair cuts leaked lines by about three
  quarters (`EV-2026-09-17-finglish-line-repair`); its current model isn't re-measured.
- **`local` tier is opt-in only:** 90-360 s per structured call
  (`EV-2026-09-23-local-ollama-qwen`, [ADR-0015](../docs/adr/0015-local-tier-and-test-mode-profiles.md)).
- **`_TimeoutSearchWrapper`** (`tools/web_search_tool.py`) works around langchain-tavily setting
  no timeout; remove it once the library takes one (`tests/test_timeouts.py` shows what to check).
- **The researcher cites pages it never read:** on 2026-10-07 Gemini 3.5 Flash-Lite called
  `read_page` 0 or 1 times in 6 single runs (3 as `create_agent`, 3 as the old deep agent, so
  not a regression of `209fec4`), and cited search results instead; the claim check rightly
  marks those claims unsupported (a full graph run: 13 of 15). The prompt already forbids it.
  Next build: a gate that hands a draft citing unread pages back to the model (read it or drop
  the claim) before it can finish, the "send back, don't drop" rule the learner set.
- **Gemini 3.8 Flash (then `strong`, now `strongest`), 2026-10-07:** one single run read 2 pages and cited only
  those (Flash-Lite read 0-1); a second single run and the full graph run (310 s) ended on the
  OpenRouter fallback with 402 (no credit). Why Google handed over is not in the output yet.
- **Models (2026-10-08, ADR-0029):** GapGPT answers again (the 2026-10-07 failures were an
  outage); the catalog's IDs were updated and all answered live; every GapGPT model has its
  OpenRouter twin as backup; test mode is Gemini 3.5 Flash-Lite, then Claude Haiku 5.5 (not on
  GapGPT yet, so OpenRouter). The OpenRouter key can't afford one 4096-token reservation, so
  every OpenRouter path (backups, Haiku) answers 402 until the learner tops it up. The learner
  removed the placeholder `OPENROUTER_API_KEY`; sessions started before that still carry it.
- **Jev model router (2026-10-08, ADR-0031):** built and unit-tested (`chain`, `runnable`, `plan`),
  never run live (the learner's instruction). Three GapGPT IDs are unverified (`claude-haiku-5-5`,
  `gpt-6-luna`, `gpt-6.1-sol`): run `uv run python scripts/smoke_live.py` (all three ladder
  profiles) and then `uv run python evals/model_route_eval.py` (54 tasks) before any call site
  adopts the router; thresholds are provisional. Adoption is per call site, with a shadow run first.
- **No retry layer on the agents' tools:** convention 11 asks for `ToolRetryMiddleware` on an
  agent's external tools; no agent has one (the research tools turn errors into text the model
  reads). Decide with the engineering track.
- **The claim check's cost has no hard cap:** it now checks every drafted claim before the cap,
  and the number of drafted claims is bounded only by the agent prompt's "at most N".

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
([review-items table](../.claude/skills/teach/materials.md#review-items-table)): none recorded.
