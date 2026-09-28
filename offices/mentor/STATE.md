# Mentor State

Read first every mentor session; rewrite it, don't append. Owned by the mentor since it adopted
the office on 2026-09-27 (LD-001); the retired handoff is at
[archive/docs/MENTOR_HANDOFF.md](../../archive/docs/MENTOR_HANDOFF.md).

## Now

- **Stage:** R0, the specialist contract ([ROADMAP](../lead/ROADMAP.md#return-pass-r0-r5)).
  Topics 1 and 2 are closed and merged to `main`.
  - Topic 1, one envelope for every answer: `SpecialistResult[T]` and a `run_*` boundary per
    specialist. Tests and demo skipped at the learner's request.
  - Topic 2, the failure contract: `utils/failure_util.py` (`failure_kind`, `is_transient`,
    `failure_reason`, `TRANSIENT_RETRY`), a `failed` envelope from every `run_*`, one retry
    layer per call (`AGENTS.md` convention 11), P2's web fallback split into `web_search` and
    `generate_from_web`, Tavily's hidden errors raised by `search_results`, P3's nodes
    re-raising bugs. The learner typed Code 1; Code 2, Code 3, and the tests-and-demo step
    were integrated by the mentor at the learner's request.
- **Next:** Topic 3, the shared eval-lite harness (first consumer: R1), taught once the
  engineer merges it. R0's remaining implementation (timeouts, evidence IDs, chat prompts split
  from worker prompts, per-app checkpoint databases, untracking the old checkpoint DB) is the
  engineer's (LD-019); the mentor teaches each piece after its teaching review. The lead
  records the contract as an ADR when R0 closes.
- **Order after R0:** R1 -> R2 -> R3 -> R4 -> P5 teaching pass (B4 to C4) -> R5 -> P6.
- **Stack:** re-verified on 2026-09-27 against the lead's upgrade (LD-007). openai 3.x and
  anthropic 1.x raise timeouts and refusals from `httpx2`; `failure_util` now classifies them,
  tested against real SDK clients on a local silent server and a closed port.

## Working agreements

- **Code delivery:** active review ([ADR-0023](../../docs/adr/0023-active-review-instead-of-typing.md)).
  The engineer builds and verifies; the mentor walks the learner through the merged code,
  diff-only, with a prediction question before each component and "why" and "what if" after.
  The learner reads code in the main checkout and writes code only by choice, in their private
  area.
- **Lesson messages:** the `teach` skill's checklist
  ([SKILL.md](.claude/skills/teach/SKILL.md#before-sending-any-lesson-message)): teach, don't
  report; one idea told through one concrete request before and after; full sentences.
- **Branch:** the mentor commits only its own paths on `mentor`, pushes it, and opens a pull
  request with `/handoff --pr`; the lead merges.
- **Evaluation:** eval-lite from P5 Phase C on; LangSmith traces used deliberately
  ([ADR-0004](../../docs/adr/0004-testing-and-evaluation-policy.md)).
- **Pacing:** counted in stages, not weeks ([ADR-0009](../../docs/adr/0009-stage-admission-rule.md)).
- **Scratch area:** `alireza/` is the learner's; never read, reference, or sync it.

## Known issues

Program-level debt is triaged in the lead's [BACKLOG](../lead/BACKLOG.md). These live code
issues move to the engineer's state (LD-018, LD-023); this copy goes once the engineer confirms.
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

Gaps from teach-backs and review questions, to revisit in the next project. None yet: the first
teach-back under active review is at R0's close.
