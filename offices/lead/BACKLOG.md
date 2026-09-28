# Backlog

Every candidate that isn't a stage's hard concept, triaged by the lead. **E** = essential,
**N** = nice-to-have. An item is either scheduled into a named stage (the Definition of Ready
pulls it in) or parked behind a concrete trigger. The live code issues stay in the engineer's
[state](../engineer/STATE.md); new ideas arrive as request or notice messages and are triaged here.

Re-triaged from the handoff backlog on 2026-09-26 under [principles](../../library/governance/principles.md) 2-3:
priorities were re-judged at production load, and items that are already a stage's hard concept
were dropped from this list (the roadmap owns them).

## Scheduled

**Lead, now**
- **E:** Design cards for P1-P4 with point 16 (production path), each before its R stage: P1
  before R1, P2 before R2, P3 before R3, P4 before R4 (DEC-006).
- **E:** Record the R0 specialist contract as an ADR when R0 closes, from the mentor's state.
- **N:** Add point 16 (production path) to the P5 design card.

**R0, the specialist contract** (built by the engineer, LD-019; taught by the mentor)
- **E:** Decision points as first-class datasets in the eval harness (LD-019, was LD-016).
- **E:** Shared eval-lite harness; first consumer R1.
- **E:** Chat prompts split from worker prompts (the chat template reaches every agent today).
- **E:** Per-app checkpoint databases, so `list` stops mixing apps' threads.
- **E:** Untrack and delete the old `src/data/dbs/checkpoints.db` (needs the user's OK: deleting
  data).
- **E:** An explicit timeout on every external call: models, embeddings, search, HTTP. A call
  that can hang forever never produces a failure the contract can classify (LD-006).
- **E:** Evidence IDs in code comments that carry measurements (LD-008).

**R1, P1**
- **E:** The unused groundedness middleware wired in for citation checks: the claim check, the
  first consumer of the `decision_model` seam (ADR-0021).
- **E:** "Is the evidence enough?" as the search loop's stop condition, inside the search budget.
- **E:** A search budget replaces approving every search.
- **N:** Finglish repair on P1's report (Perso-Arabic leaked in a `lab-brief` run).
- **N:** Decide whether the coordinator's `researcher` becomes a `CompiledSubAgent` over
  `run_research`, once the budget exists.

**R2, P2**
- **E:** Incremental re-index with stale-source detection; rebuild the stale index; index the
  agents and apps as well.
- **E:** Ungrounded answers rerouted to query rewrite or web search instead of a disclaimer.
- **E:** The groundedness check on the web fallback path too.
- **E:** Grading and reranking in one decider request; the entry questions at once; per-claim
  verification (ADR-0021).
- **E:** Reference answers in R2's labeled set; tier routing and the model catalog measured on it.
- **E:** Hybrid retrieval (BM25 + vector + reranker) as the first change judged by R2's metrics
  (DEC-013).

**R3, P3**
- **E:** Diff and multi-file input.
- **E:** The review triangle: `ruff` and the AST find issues, a decider labels severity,
  category, and score, the LLM explains.

**R4, P4**
- **E:** A risk label on the `execute` approval prompt; the approval itself unchanged.
- **N:** Carry the typed envelope into a DeepAgents coordinator's state, not only its text (extra
  state keys from a `CompiledSubAgent` reach the parent).

**P5 teaching pass**
- **E:** The guard as three checks combined fail-closed; the staleness pre-pass; recall ranking;
  the schema compiler at its third consumer (ADR-0021).
- **E:** Compare assistant models in C2: script leakage per line, false "saved" claims, guard
  agreement. The Finglish repair only mitigates the leak.

**R5, close**
- **E:** The coordinator's pre-router, measured on a labeled routing set.
- **E:** Secret redaction and trace masking in every app, and one LangSmith project per app.
- **E:** One CLI approval loop (`run_with_hitl` and `stream_with_hitl` overlap).
- **N:** Remove `utils/time_travel_util.py` unless a consumer appears.
- **N:** Clearer approval prompts; the approved tool call printed twice after an HITL resume.
- **N:** Study guides for P1 and P2.

**P6-B2, failure by error class**
- **N:** A typed failure class on the envelope (`transient | permanent`), once a caller branches
  on it.
- **N:** Model-output errors (structured output failing validation) as a recoverable class.
- **N:** Model callers of `web_search` still get Tavily errors as text; revisit with the
  recoverable class.

## Parked

| Item | Priority | Trigger |
| :--- | :--- | :--- |
| Measure the `opensource` tier on this repo's structured-output schemas and tool calling | E | Requested from research (LD-005); required before any more call sites move to that tier |
| Embedding-provider failover (Gemini 3072-dim vs OpenAI 1536-dim collections) | N | A composed workflow must survive an embeddings outage (review at P6-B2) |
| Grow the P5 security guard into a policy-parameterized security agent | N | A second consumer needs tools in its judgment: documents in P7, action permissions in P8 or P11 |
| DeepAgents harness profiles | N | A fallback model needs different prompts or tool descriptions than the primary |
| Semantic search over memory (per fact, index kept in sync on every write) | N | Memory that can't load whole: episodic memory, or customer context at support scale (P8-B1); plan it as its own stage then |
| HITL "edit" decision for sandbox commands | N | A stage whose approvals need argument edits rather than approve/reject |
| Sandbox filesystem snapshots alongside checkpoints | N | Time travel over side effects is taught (Term E, E1) |
| Session-scoped or remote sandbox workspaces | N | Term E, E1 |
| A guard against direct pushes to `main`: a pre-push hook through `core.hooksPath`, installed by `scripts/setup_worktrees.py` (GitHub can't protect a private repo's branch on the Free plan) | N | A direct push to `main` happens |
| A weekly cloud routine running research's upstream watch on branch `research` (DEC-020) | E | Research replies to LD-015 with its watch procedure |
| Development-loop hooks, advisory: document health, a done gate, shell edits and ownership, meaning-level conventions (DEC-025) | N | The engineer's queue after R1; the user's explicit yes before a hook sends session content or a replay reads transcripts |
| Rename `TIER_CASCADE_ORDER` to a fallback order (DEC-025) | N | The quality escalation lands (D1) |
| Remove the redirects at `offices/lead/PEDAGOGY.md` and `offices/lead/TECH_RADAR.md` (DEC-029) | E | The mentor and research have updated their links (LD-023, LD-025) |

## Deep-dive candidates

None yet ([pedagogy](../../library/teaching/pedagogy.md#digressions-and-deep-dives)).

## Closed in triage

- **A TypeSafe API key to measure Jev:** obsolete 2026-09-27; the user's OpenRouter key reaches
  Jev, and research measured it that way (RS-007 withdrawn, `EV-2026-09-27-jev-openrouter`).
- **Automatic message awareness (item e):** built 2026-09-27: prompt hook, `/inbox` and `/loop`,
  the Messages workflow (DEC-020, ADR-0020); the research routine is parked above.
- **Per-role worktrees, identity in role files, session hooks, `/handoff` (items a-d):** built
  2026-09-27 (DEC-017, ADR-0019).
- **Wire `rag_subagent` into the researcher:** superseded by P6-A1, where the workflow composes P1
  and P2 instead.
- **System-1 decision layer:** superseded 2026-09-28: decision points from R1 and a stage, D1
  (DEC-022 to DEC-024).
- **Library placement of research's design guide:** done 2026-09-28; the rules moved to
  `library/architecture/decision-models.md`, the facts stay in research's landscape (DEC-025).
- **Surface approvals raised inside subagents:** the hard concept of P6-B3.
