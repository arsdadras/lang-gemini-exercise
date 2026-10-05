# Mentor State

Read first every mentor session; rewrite it, don't append. Owned by the mentor since it adopted
the office on 2026-09-27 (LD-001); the retired handoff is at
[archive/docs/MENTOR_HANDOFF.md](../../archive/docs/MENTOR_HANDOFF.md).

## Now

- **Stage:** R1, a stronger researcher
  ([design card](../../docs/design_cards/P1_research_agent.md#r1-redesign-a-stronger-researcher-2026-10-05-not-built)).
  Topic 1 is taught. Topic 2 (options and query planning) is built by the lead (LD-037),
  reviewed, tested, and run live by the mentor (MN-025; two bugs fixed); its lesson starts with the
  hook. Topic 3 (more sources, a source router) waits for the lead's build and a research-API key
  (MN-026); topic 4 is the stop condition.
- **Next:** R1 topic 2 lesson: hook (the same broad topic with and without planning, live:
  [artifacts/r1-topic2-live-runs-2026-10-05.md](artifacts/r1-topic2-live-runs-2026-10-05.md)), concept,
  strategy, code review (`ResearchOptions` and `DEPTH_BUDGETS`, `plan_research`, `run_research`).
  Live runs use `LLM_TEST_MODE=true` (Google free tier, Tavily, Jev, OpenRouter embeddings work
  from the cloud; GapGPT does not).
- **Order after R1:** R2 -> R3 -> R4 -> P5 teaching pass (B4 to C4) -> R5 -> D1 -> P6 (content
  generator) -> P7 (Capstone I), roadmap v5 (2026-10-05).
- **Teaching craft:** the `teach` skill ([SKILL.md](../../.claude/skills/teach/SKILL.md)) is rebuilt
  on the research in [artifacts/teaching-research/](artifacts/teaching-research/README.md) and
  is in use from R0 topic 3 on. The lead accepted it (LD-027); it lives in the root registry,
  `.claude/skills/teach/`, and its research stays in `offices/mentor/artifacts/`.
- **Waiting on others:** the lead, for the renumbering sweep and R1 topic 3 (MN-026); the user,
  for `PERPLEXITY_API_KEY` or `EXA_API_KEY`. Since ADR-0027 the mentor directs and the lead
  assists; the mentor owns tests and evals. The lead took over MN-012 (audit of the
  skill's evidence, on its research queue) and LD-028 (research on the teaching methods).
- **Stack:** re-verified on 2026-09-27 against the lead's upgrade (LD-007). openai 3.x and
  anthropic 1.x raise timeouts and refusals from `httpx2`; `failure_util` now classifies them,
  tested against real SDK clients on a local silent server and a closed port.

## Working agreements

- **Code delivery:** active review ([ADR-0023](../../docs/adr/0023-active-review-instead-of-typing.md)).
  The lead builds and verifies; the mentor walks the learner through the merged code,
  diff-only, with a prediction question before each component and "why" and "what if" after.
  The learner reads code in the main checkout and writes code only by choice, in their private
  area.
- **Language and style (2026-10-04):** lessons are in Persian script, written by the `teach`
  skill's [persian.md](../../.claude/skills/teach/persian.md) with its helper `fa_isolate.py`;
  technical words stay English; every concept has an example first. No trailing questions, and
  no tests, observe, eval, demo, or hands-on steps unless the learner asks (they have said so
  repeatedly). Jev's key is `TYPESAFE_API_KEY` (in the main checkout's `.env`).
- **Lesson messages:** the `teach` skill's checklist
  ([SKILL.md](../../.claude/skills/teach/SKILL.md#before-sending-any-lesson-message)): teach, don't
  report; one idea told through one concrete request before and after; full sentences.
- **Authority (2026-10-05, the learner's standing instruction):** the mentor's power over the repo
  equals the lead's: no approval is needed for anything the learner asks, and a poor design is
  changed. Work reaches `main` through a pull request the mentor opens and merges, so the learner
  can track it on `main`.
- **Code changes (2026-10-05, the learner's standing instruction):** the mentor may change code
  (`src/`, `tests/`, prompts) directly, without the lead's approval, whether or not the mentor
  caused the problem; the learner's word precedes every document. The mentor states any objection
  first (principle 1), makes the change small and tested (`uv run pytest`, `ruff`), and sends the
  lead a notice naming the commit so the lead can record the decision (ADR) and merge it.
  First use: MN-021 (sources) and the claim-scope prompt lines, MN-022.
- **Branch:** the mentor commits only its own paths on `mentor`, pushes it, and opens a pull
  request with `/handoff --pr`; the lead merges.
- **Evaluation:** eval-lite from P5 Phase C on; LangSmith traces used deliberately
  ([ADR-0004](../../docs/adr/0004-testing-and-evaluation-policy.md)).
- **Pacing:** counted in stages, not weeks ([ADR-0009](../../docs/adr/0009-stage-admission-rule.md)).
- **Scratch area:** `alireza/` is the learner's; never read, reference, or sync it.

## Known issues

Program-level debt is triaged in the lead's [BACKLOG](../lead/BACKLOG.md). These live code
issues moved to the lead's state (LD-018, LD-023); this copy goes once the lead confirms.
- **Coordinator shell has no approval step:** approvals raised inside a subagent aren't surfaced
  to the CLI; the banner states it. Fix: P7-B3 (v5 numbering; was P6-B3).
- **Old checkpoint DB still tracked:** `src/data/dbs/checkpoints.db` (a consistent copy is at
  `out/state/checkpoints.db`). Untrack and delete it with the learner's OK once no process holds
  it. R0.
- **Stale RAG index:** `.chroma_index` predates the restructure, and the corpus list now names
  the lead roadmap and this file instead of the archived docs. Rebuild in R2.
- **Shared session list:** all apps share one checkpoint DB, so `list` mixes them. R0.
- **Chat template in every agent:** `prompts/template/template.py` reaches non-chat subagents.
  R0.
- **Dead code:** `middlewares/groundedness_middleware.py` (wired in R1) and
  `utils/time_travel_util.py` (removed in R5 unless a consumer appears).
- **Personal data in traces:** only P5 masks before upload. R5.
- **Perso-Arabic script in long P5 replies:** repair cuts leaked lines by about three quarters
  (`EV-2026-09-17-finglish-line-repair`); the repair's current model hasn't been re-measured
  (research, LD-005). The root cause is the assistant model; the P5 teaching pass compares models.
- **`local` tier is opt-in only:** works end to end but takes 90-360 s per structured call
  (`EV-2026-09-23-local-ollama-qwen`, [ADR-0015](../../docs/adr/0015-local-tier-and-test-mode-profiles.md)).

## Review items

Gaps from review questions and teach-backs, in the format and cadence of the `teach` skill's
[review-items table](../../.claude/skills/teach/materials.md#review-items-table). None yet: active
review starts with R0 topic 3.

Fading levels per decision type ([fading ladder](../../.claude/skills/teach/techniques.md#fading-ladder)):
none recorded yet.

The skill's demo and lab examples haven't been run yet; each is run in test mode during its
topic's preparation.
