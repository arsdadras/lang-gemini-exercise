# Mentor State

Read first every session; rewrite it, don't append. The charter is [README.md](README.md); since
[ADR-0028](../docs/adr/0028-one-mentor-one-branch.md) the mentor is the only role and works on
`main`.

## Now

- **Stage:** R1, a stronger researcher
  ([design card](../docs/design_cards/P1_research_agent.md#r1-redesign-a-stronger-researcher-2026-10-05-not-built)).
  Topics 1 and 2 are taught. Topic 2 (options and query planning) closed on 2026-10-05 with two
  fixes from the learner's critique: the claim cap runs after the claim check and keeps
  supported claims first (`c36bc64`), and a plan over the cap gets one re-plan before any cut,
  with cut sub-questions named in the reason (`b5f6850`). The rule the learner and the mentor
  agreed: a deletion that loses nothing is fine; a lossy one needs an informed priority and is
  never silent.
- **Next: R1 topic 3, more sources and a source router.** Not built yet. Prepare it before
  teaching: the private corpus through P2's retrieval and arXiv need no key; the research-API
  source (Perplexity or Exa) needs `PERPLEXITY_API_KEY` or `EXA_API_KEY` from the learner; the
  router is the decision point `research_sources@1` on the `decision_model` seam, held to the
  [one standard](../library/architecture/decision-models.md#one-standard-for-every-decision-point).
  Build the keyless sources and the router first; add the API source when the key arrives.
- **Then:** R1 topic 4, the stop condition (`evidence_enough@1` per sub-question inside the
  budget). After R1: R2 -> R3 -> P5 teaching pass (B4 to C4) -> R5 -> D1 -> P6 (content
  generator) -> P7 (Capstone I) ([ROADMAP](ROADMAP.md), v5).

## Build queue

1. R1 topic 3 (above), then topic 4.
2. A live end-to-end run of the research agent after topic 4; the depth budgets are provisional
   until real broad runs measure them (`DEPTH_BUDGETS`).
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

- **Language:** everything to the learner is in Persian script (lessons since 2026-10-04,
  every other message since 2026-10-07), written by the `teach` skill's
  [persian.md](../.claude/skills/teach/persian.md) through `fa_isolate.py`; technical words stay
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
- **Git:** everything on `main`, pushed at the end of each session
  ([git policy](../library/engineering/git-policy.md)).
- **Live runs:** test mode per command (`LLM_TEST_MODE=true`); `.env` is never edited. Jev's key
  is `TYPESAFE_API_KEY`; Google, Tavily, Jev, and OpenRouter embeddings work in test mode.
- **Scratch area:** `alireza/` is the learner's; never read, reference, or sync it.

## Live code issues

Program-level debt is the [BACKLOG](BACKLOG.md); these are the code's.

- **Coordinator shell has no approval step:** approvals raised inside a subagent aren't surfaced
  to the CLI; the banner states it. Fix: P7-B3.
- **RAG index must be rebuilt:** `.chroma_index` predates the restructure and holds Gemini's
  vectors; the embedding model is now 1536-dimensional. Rebuild in R2 (paced; minutes).
- **Unused code:** `utils/time_travel_util.py` has no consumer outside a test; removed in R5
  unless one appears.
- **Personal data in traces:** only P5 masks before upload. Engineering track.
- **Perso-Arabic script in long P5 replies:** the repair cuts leaked lines by about three
  quarters (`EV-2026-09-17-finglish-line-repair`); its current model isn't re-measured.
- **`local` tier is opt-in only:** 90-360 s per structured call
  (`EV-2026-09-23-local-ollama-qwen`, [ADR-0015](../docs/adr/0015-local-tier-and-test-mode-profiles.md)).
- **Retries stack in hosted chat calls:** the OpenAI SDK retries twice by default, so a call can
  take three timeouts (3 x 120 s) per provider before the fallback switches. Pick `max_retries`.
- **`_TimeoutSearchWrapper`** (`tools/web_search_tool.py`) works around langchain-tavily setting
  no timeout; remove it once the library takes one (`tests/test_timeouts.py` shows what to check).
- **The `low` tier cites pages it never read:** in the 2026-10-07 live run of the research graph,
  two of three runs cited only search results and two garbled URLs, so the claim check rightly
  marked their claims unsupported (10 of 10). Gemini 3.5 Flash-Lite supported most claims on
  2026-10-05. Prompt or tier fix in R1 topic 4's live runs.
- **Live runs blocked (2026-10-07):** test mode now falls back from Google's Gemini 3.5
  Flash-Lite to OpenRouter's `gpt-6-luna` (verified: Google's 401 fell through to luna). But the
  Google key is disabled, GapGPT refuses connections, and the OpenRouter key's credit covers
  about 7,800 output tokens per request, so three parallel research runs get 402. Two more
  learner-side items: a placeholder `OPENROUTER_API_KEY` (9 characters) set in the shell
  environment shadows the real one in `.env` (`load_dotenv` never overrides), and
  `OPENROUTER_MAX_OUTPUT_TOKENS` stays 4096 until the credit allows 8192 (a `deep` draft needs it).
  The researcher's tool-surface fix (`209fec4`) still waits for its live run.
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
  [synthesis, section 5](artifacts/teaching-research/synthesis.md#5-open-questions-worth-a-verified-study).

## Reserved for the learner

- `PERPLEXITY_API_KEY` or `EXA_API_KEY` for R1 topic 3's research-API source.
- The yes before a development-loop hook sends session content to a hosted decider (DEC-025).

## Review items

Gaps from review questions and teach-backs
([review-items table](../.claude/skills/teach/materials.md#review-items-table)): none recorded.
