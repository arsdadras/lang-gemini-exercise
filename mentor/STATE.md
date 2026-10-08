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
- **Now: R1 topic 3, more sources and a source router.** Built and live-verified 2026-10-08
  ([design card](../docs/design_cards/P1_research_agent.md#r1-redesign-a-stronger-researcher-2026-10-05-not-built));
  teaching starts with its hook. Sources: web, academic (Exa research papers), private (P2's
  index). Router `research_sources@1`: 97.1% on 69 labeled cases, 0 unsafe, p95 605 ms. Live run
  (strong profile through GapGPT): every kind read, 8 of 11 claims supported. The free tier
  rarely calls `academic_search` when web is also offered (it does when academic is the only
  source).
- **Then:** R1 topic 4, the stop condition (`evidence_enough@1` per sub-question inside the
  budget). After R1: R2 -> R3 -> P5 teaching pass (B4 to C4) -> R5 -> D1 -> P6 (content
  generator) -> P7 (Capstone I) ([ROADMAP](ROADMAP.md), v5).

## Build queue

1. R1 topic 3 teaching, then topic 4.
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
- **A weak result because of the model (2026-10-07):** rerun it with `LLM_TEST_PROFILE=strong`
  (Gemini 3.8 Flash on Google, `gpt-6-luna` on OpenRouter as its fallback); if that doesn't
  answer, keep the free tier.
- **Live runs:** test mode per command (`LLM_TEST_MODE=true`); `.env` is never edited. Test mode
  calls Gemini through GapGPT first (the learner's direction, 2026-10-08), then Google's API, then
  Haiku on OpenRouter (out of credit). Jev's key is `TYPESAFE_API_KEY`; Exa's is `EXA_API_KEY`.
- **Scratch area:** `alireza/` is the learner's; never read, reference, or sync it.

## Live code issues

Program-level debt is the [BACKLOG](BACKLOG.md); these are the code's.

- **Coordinator shell has no approval step:** approvals raised inside a subagent aren't surfaced
  to the CLI; the banner states it. Fix: P7-B3.
- **RAG index:** rebuilt in this worktree 2026-10-08 (1536-dimensional); the main checkout's
  `.chroma_index` is still the old one: rebuild it there before `lab-rag` or the private source.
- **Approvals inside the research graph:** an outbound search waits for approval, and the
  research node reports a waiting run as a problem instead of surfacing the interrupt, so
  `run_research` with the approval gate on stops at the first search; live runs replace the gate
  in the script. Fix: run the agent as a subgraph so its interrupts reach the caller (with P7-B3).
- **A joined corpus document can pass `MAX_PAGE_CHARS`:** parts of one file read by several
  runs are joined, and the claim check sees the first 12,000 characters. Trigger: a corpus claim
  marked unsupported whose passage sits past the cut.
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
- **The researcher cites pages it never read:** on 2026-10-07 Gemini 3.5 Flash-Lite called
  `read_page` 0 or 1 times in 6 single runs (3 as `create_agent`, 3 as the old deep agent, so
  not a regression of `209fec4`), and cited search results instead; the claim check rightly
  marks those claims unsupported (a full graph run: 13 of 15). The prompt already forbids it.
  Next build: a gate that hands a draft citing unread pages back to the model (read it or drop
  the claim) before it can finish, the "send back, don't drop" rule the learner set.
- **Gemini 3.8 Flash (`strong`), 2026-10-07:** one single run read 2 pages and cited only
  those (Flash-Lite read 0-1); a second single run and the full graph run (310 s) ended on the
  OpenRouter fallback with 402 (no credit). Why Google handed over is not in the output yet.
- **Models (2026-10-08, ADR-0029):** GapGPT answers again (the 2026-10-07 failures were an
  outage); the catalog's IDs were updated and all answered live; every GapGPT model has its
  OpenRouter twin as backup; test mode is Gemini 3.5 Flash-Lite, then Claude Haiku 5.5 (not on
  GapGPT yet, so OpenRouter). The OpenRouter key can't afford one 4096-token reservation, so
  every OpenRouter path (backups, Haiku) answers 402 until the learner tops it up. The learner
  removed the placeholder `OPENROUTER_API_KEY`; sessions started before that still carry it.
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
