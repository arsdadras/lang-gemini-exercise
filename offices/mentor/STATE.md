# Mentor State

Read first every mentor session; rewrite it, don't append. Owned by the mentor since it adopted
the office on 2026-09-27 (LD-001); the retired handoff is at
[archive/docs/MENTOR_HANDOFF.md](../../archive/docs/MENTOR_HANDOFF.md).

## Now

- **Stage:** R1, P1 evidence-grounded research ([ROADMAP](../lead/ROADMAP.md#return-pass-r0-r5)).
  R0 is closed by the lead ([ADR-0026](../../docs/adr/0026-the-specialist-contract.md), LD-032).
  The stage brief (no code) was sent 2026-10-05; it waits on the learner's OK. Ready to teach
  (LD-033, the lead is one topic ahead): topic 1, claims instead of findings (`ResearchDraft`,
  `ResearchReport`, `read_page`), and topic 2, the claim check (`nodes/claim_check_node.py`, the
  `decision_model` seam). Topic 3, the stop condition, waits for the lead's next notice.
- **Next:** R1 topic 1, step 1. The hook is sent (2026-10-05): the pre-R1 schema, run in the
  sandbox (`sandbox/r1_hook_old_report.py`, a labeled variant), accepts an unsupported finding
  with a model-typed confidence. The concept (claim = text + evidence; status and confidence
  from code) comes next, then strategy, then the code review (`research_output_schema.py`,
  `read_page_tool.py`). No live agent run is possible in a cloud session (no keys), so hooks
  here use sandbox traces and the repo's labeled cases.
- **Order after R1:** R2 -> R3 -> R4 -> P5 teaching pass (B4 to C4) -> R5 -> P6.
- **Teaching craft:** the `teach` skill ([SKILL.md](../../.claude/skills/teach/SKILL.md)) is rebuilt
  on the research in [artifacts/teaching-research/](artifacts/teaching-research/README.md) and
  is in use from R0 topic 3 on. The lead accepted it (LD-027); it lives in the root registry,
  `.claude/skills/teach/`, and its research stays in `offices/mentor/artifacts/`.
- **Waiting on others:** nobody. Two roles since ADR-0025: the lead builds, tests, and
  researches; requests and notices go to the lead. The lead took over MN-012 (audit of the
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
  to the CLI; the banner states it. Fix: P6-B3.
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
