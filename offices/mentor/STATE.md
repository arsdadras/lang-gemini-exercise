# Mentor State

Read first every mentor session; rewrite it, don't append. Seeded by the lead on 2026-09-26 from
`docs/MENTOR_HANDOFF.md`; the mentor reconciles it with its live handoff when it adopts the office
(LD-001), then owns it.

## Now

- **Stage:** R0, the specialist contract ([ROADMAP](../lead/ROADMAP.md#return-pass-r0-r5)).
  Topic 1 (the envelope) is integrated; its tests-and-demo step was skipped at the learner's
  request. Topic 2 (the failure contract) is built, verified, and committed on branch `mentor`:
  `utils/failure_util.py`, the `failed` envelope with `failure_reason` in every `run_*`,
  `TRANSIENT_RETRY` on P2's `retrieve` and `web_search` nodes, the `search_results` adapter
  for Tavily, P3's nodes re-raising bugs, and `AGENTS.md` convention 11. Teaching position:
  Code 1 typed and integrated; Code 2 (P2) sent, the learner hasn't typed it yet; Code 3 (P1,
  P3, P4 boundaries, links only) and tests-and-demo remain.
- **Next:** once the lead builds the `mentor` worktree, reset `nodes/rag_node.py`,
  `graphs/rag_graph.py`, and `subagents/rag_subagent.py` there for the learner to type Code 2
  (the verified version is the `mentor` commit; restore it with `git checkout HEAD -- <files>`).
  Then LD-001 (blocking), then Topic 3.
- **Order after R0:** R1 -> R2 -> R3 -> R4 -> P5 teaching pass (B4 to C4) -> R5 -> P6.
- **Stack:** upgraded by the lead (LD-007); R0 re-verified against it on 2026-09-27. Found and
  fixed: openai 3.x and anthropic 1.x raise timeouts and refusals from `httpx2`, which
  `failure_util` classified as bugs; now covered by tests against real SDK clients on a local
  silent server and a closed port. `failure_util` imports `httpx`, `httpx2`, and `requests`,
  none declared in `pyproject.toml`: send the lead a request at R0 close.

## Working agreements

- **Code delivery:** the mentor verifies each component, reverts, and sends the lesson code in
  chat; the learner types it (tests aren't sent). Before the next component, the mentor
  integrates the verified code and tests, replacing the learner's copy.
- **Evaluation:** eval-lite from P5 Phase C on; LangSmith traces used deliberately
  ([ADR-0004](../../docs/adr/0004-testing-and-evaluation-policy.md)).
- **Pacing:** counted in stages, not weeks ([ADR-0009](../../docs/adr/0009-stage-admission-rule.md)).
- **Scratch area:** `alireza/` is the learner's; never read, reference, or sync it.

## Known issues

Program-level debt is triaged in the lead's [BACKLOG](../lead/BACKLOG.md); these are the live
code issues.

- **Coordinator shell has no approval step:** approvals raised inside a subagent aren't surfaced
  to the CLI; the banner states it. Fix: P6-B3.
- **Old checkpoint DB still tracked:** `src/data/dbs/checkpoints.db` (a consistent copy is at
  `out/state/checkpoints.db`). Untrack and delete it with the learner's OK once no process holds
  it. R0.
- **Stale RAG index metadata:** `.chroma_index` predates the restructure. Rebuild in R2.
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
