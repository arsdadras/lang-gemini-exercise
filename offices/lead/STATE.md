# Lead State

Read first in every lead session; rewrite it, don't append. Program status in one place:
[ROADMAP.md](ROADMAP.md) "Now, next, later". Live teaching status: the mentor's
[state](../mentor/STATE.md).

- **Last lead session:** 2026-10-05 (session 9, local, worktree `claude/lead-d01ef5`).
- **Roles:** two since 2026-10-03 (ADR-0025, DEC-031). The lead decides, plans, builds, tests,
  debugs, researches, and reviews; the mentor teaches and reviews the code it teaches. A change
  flows plan -> build and verify (lead) -> merge on green CI -> notice to the mentor. The learner
  reviews the verified code instead of typing it (ADR-0023). Reports to the user open with the
  bottom line (principle 12). The engineer's and research's offices are in
  [`archive/offices/`](../../archive/README.md); the research record is
  [`research/`](research/CATALOG.md).
- **Library:** the lead's alone to write and curate, in five categories (ADR-0024). Redirects stay
  at `PEDAGOGY.md` and `TECH_RADAR.md` until the mentor updates its links (BACKLOG).
- **Repo:** each role has its own worktree and branch (ADR-0019): `D:/Repos/lce-lead`,
  `lce-mentor`, each with its own `.venv` and `.env`; the main checkout is a clean `main` that
  takes no edits. The ownership guard, worktree routing, and message awareness are live
  (ADR-0020); the lead owns every path except the mentor's. Branch protection isn't available on
  GitHub Free for a private repo, so "main only by pull request" is policy, backed by the guard
  and the Messages report.

## Open messages

- **Mentor:** LD-032 (R0 closed), LD-033 (R1 topics 1 and 2 built; topic 3 pending). LD-031
  answers MN-017 (done).

Details in [OUTBOX.md](OUTBOX.md).

## Build queue (taken over from the engineer, ADR-0025)

R0 is closed (ADR-0026, DEC-032). The `decision_model` seam is built and live-verified
(DEC-033), and the P1 design card is written (DEC-035). **Now: R1's reference implementation,**
which the stage needs before the mentor can teach it (Definition of Ready), in this order:

Built and verified 2026-10-05 (topics 1 and 2 of R1): `read_page` and the claim table (the
agent writes a `ResearchDraft`, code builds the `ResearchReport`), the claim check on
`decision_model` with the LLM escalating and never raising a verdict, the 5-search budget, the
34-case labeled set with Jev's numbers ([EV-2026-10-05-claim-check-jev](research/evidence/EV-2026-10-05-claim-check-jev/README.md)).
Left:

1. **The stop condition** (`evidence_enough@1`, a `noul` over the claims so far) inside the budget.
2. **The LLM half of the measurement,** and a live end-to-end run of the agent: both wait for
   GapGPT, unreachable from this machine on 2026-10-05 (`evals/claim_check_eval.py --only llm`).
3. **Grow the claim-check set from 34 to 50** (then 200 before fitting thresholds), and fit
   `SUPPORTS_THRESHOLD` and `CONTRADICTS_THRESHOLD` from the numbers.
4. A topic-3 notice to the mentor with the core code when the stop condition is merged.

Other open items: record the consolidator reconciliation (research queue below).

## Live code issues

Program-level debt is the [BACKLOG](BACKLOG.md); these are the code's.

- **Coordinator shell has no approval step:** approvals raised inside a subagent aren't surfaced
  to the CLI; the banner states it. Fix: P6-B3.
- **RAG index must be rebuilt:** `.chroma_index` predates the restructure and holds Gemini's
  vectors; the embedding model is now 1536-dimensional, so the old index can't answer queries.
  The corpus list also names different files now. Rebuild in R2 (paced; minutes); the paced
  batch size and delay were sized for Gemini's free quota, and GapGPT's limits are unmeasured.
- **Dead code:** `middlewares/groundedness_middleware.py` (wired in R1) and
  `utils/time_travel_util.py` (removed in R5 unless a consumer appears).
- **Personal data in traces:** only P5 masks before upload. R5.
- **Perso-Arabic script in long P5 replies:** repair cuts leaked lines by about three quarters
  (`EV-2026-09-17-finglish-line-repair`); the repair's current model hasn't been re-measured. The
  root cause is the assistant model.
- **`local` tier is opt-in only:** 90-360 s per structured call
  (`EV-2026-09-23-local-ollama-qwen`, [ADR-0015](../../docs/adr/0015-local-tier-and-test-mode-profiles.md)).
- **Retries stack in hosted chat calls:** the OpenAI SDK retries twice by default, so a call can
  take up to three timeouts (3 x 120 s) per provider before the fallback switches. Pick a number
  (SDK `max_retries` per spec).
- **`_TimeoutSearchWrapper`** (`tools/web_search_tool.py`) replaces langchain-tavily 0.2.18's two
  request methods because the library sets no timeout. Remove it once the library takes one;
  `tests/test_timeouts.py` shows what to check.

## Research queue (taken over from research, ADR-0025)

Not started; the lead measures and records in [`research/`](research/CATALOG.md).

- **Upstream watch:** a weekly routine over the pinned stack's releases and the radar's watched
  items, written as a procedure first, then scheduled (was LD-003, LD-015).
- **BR-002's measurements,** and LangSmith Sandboxes for P4 (R4, E1) (was LD-005).
- **The Jev follow-ups** and decision-accuracy techniques (state shaping, question wording,
  decomposition, answer-set design), measured on our labeled sets (was LD-021). Replaying our own
  sessions to measure development-loop gates needs the user's yes.
- **The consolidator records disagree** (ADR-0014's erratum: 3/3 vs 0/3 in ADR-0012, not 6/6 vs
  4/6; `EV-2026-09-19-consolidator-model-comparison`): reconcile them.
- **Teaching-method questions** from MN-013 and the mentor's audit MN-012 (was LD-028):
  [synthesis, section 5](../mentor/artifacts/teaching-research/synthesis.md#5-open-questions-worth-a-verified-study).
  ADR-0023 rests on the evidence for question 1; a weak finding reopens it.

## The Jev file

Decided 2026-09-28: the user accepted the lead's [dossier](artifacts/jev-dossier.md) in full
(DEC-022 to DEC-025, ADR-0021, roadmap v4.2). The rules live in
[`library/architecture/decision-models.md`](../../library/architecture/decision-models.md). First
code: the eval harness's decision datasets (done), then the `decision_model` seam when R1 is made
ready.

## Reserved for the user

- The explicit yes before a development-loop hook sends session content to a hosted decider, or a
  replay reads past transcripts (DEC-025); asked when the first such hook is ready.
- Trust the project's hooks once when Claude Code asks.

## Agenda for the next lead session

1. R1's remaining build (the stop condition; the LLM half once GapGPT answers); verify the mentor's replies to LD-032 and LD-033.
2. Write the P2-P4 design cards before their stages (R2-R4).
3. Create the weekly upstream-watch routine once its procedure is written.
4. At every phase and project boundary: curate the library (ADR-0024).
5. Every session: inbox, dependency drift and Dependabot pull requests, docs lint.

## Session log

- **2026-09-26, session 1 (as "the office").** The office was established: charter,
  principles, pedagogy, roadmap v4, architecture, radar, backlog re-triage, risks, DEC-001 to
  DEC-010, ADR-0016 and ADR-0017, six directives, `CLAUDE.md` as a role router.
- **2026-09-26, session 2.** Stack upgraded to the latest releases (`0d27fa8`). Restructured
  into three offices, the library, and the archive (DEC-015, ADR-0018); CI, Dependabot,
  `scripts/check_docs.py`, and `scripts/inbox.py` (DEC-016); LangChain, LangSmith, and
  knowledge-graph findings decided (DEC-011 to DEC-013); research's outbox dispositioned
  (DEC-014); messages LD-001 to LD-009. Moved mid-session from the local machine to a cloud
  session.
- **2026-09-27, session 3 (local).** Synced local `main` with the cloud merge; kept the mentor's
  `AGENTS.md` hunk; fixed `check_docs.py` paths on Windows; merged Dependabot #2 after verifying
  `uv build`; recorded the per-role worktree, hooks, and `/handoff` plan (backlog items a-e) for
  the user's go-ahead, and the Jev-related library placement as a held decision.
- **2026-09-27, session 4 (local).** Merged the mentor's pull request #3 (R0 topic 2, mentor
  office). Built ADR-0019: one worktree and branch per role, `scripts/setup_worktrees.py`,
  session hooks, `/handoff`, and an inbox that reads role branches; decided MN-002 (DEC-018);
  closed LD-001, LD-002, LD-007, LD-009; sent LD-010 to LD-013.
- **2026-09-27, session 5 (local).** On the user's direction: archived `docs/ROADMAP.md`;
  retired `handoff/local-snapshot` as the tag `archive/handoff-local-snapshot` and archived its
  handoff record; built ADR-0020 (ownership guard over a machine-read Roles column, worktree
  routing and `/mentor`, a prompt hook, `/inbox`, the Messages workflow; DEC-019 to DEC-021);
  sent LD-014 and LD-015. The lead now merges without asking.
- **2026-09-27 to 28, session 6 (local).** Opened and closed the Jev file: read research's whole
  dossier and the user's sources, wrote the lead's dossier, and after the user accepted it
  recorded DEC-022 to DEC-025 and ADR-0021 (roadmap v4.2, stage D1, design card point 17, the
  library entry, the `decision-points` skill). Founded the engineer role on the user's direction
  (DEC-026, ADR-0022); new mandates for the mentor and research (LD-020, LD-021); reports open
  with the bottom line (DEC-027). The learner reviews instead of typing (DEC-028, ADR-0023), and
  the library became the lead's alone, in five categories (DEC-029, ADR-0024).
- **2026-10-03, session 7 (local).** Decided MN-013 (DEC-030): accepted the rebuilt `teach`
  skill, the pedagogy's reconciliation clause, an ownership row for `.claude/skills/teach/`,
  rejected a shared drop-zone folder; sent LD-027; verified and closed LD-010 and LD-023.
- **2026-10-03, session 8 (local).** On the user's direction, collapsed four roles into two
  (DEC-031, ADR-0025): the lead owns every path but the mentor's; `ROLES` is lead and mentor
  in the scripts and tests; the engineer and research skills, offices, worktrees, and branches
  are gone (offices archived, the research record moved to `offices/lead/research/`); open
  messages to them closed or withdrawn; the engineer's pull request #15 merged in (its CI had
  been fixed in `b2c8b37`); LD-030 to the mentor.
- **2026-10-05, session 9 (local).** Verified and closed LD-027 and LD-030 (MN-015, MN-016); merged the mentor's PR #18 through this branch, with the one broken link in LD-028 fixed.
- **2026-10-05, session 9 continued.** On the user's go-ahead: R0 closed (ADR-0026, DEC-032); the `decision_model` seam built and live-verified, Jev direct at TypeSafe with `jev-1.13.0` (DEC-033, `langchain-typesafe` in the lock); principle 12's Persian-lessons exception (DEC-034); the P1 design card (DEC-035); LD-031 and LD-032 to the mentor.
