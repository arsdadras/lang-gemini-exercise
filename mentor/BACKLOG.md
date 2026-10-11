# Backlog

Every candidate that isn't a stage's hard concept, triaged by the mentor. **E** = essential,
**N** = nice-to-have. An item is either scheduled into a named stage (the Definition of Ready
pulls it in) or parked behind a concrete trigger. The live code issues stay in the
[state](STATE.md); new ideas are triaged here.

Re-triaged from the handoff backlog on 2026-09-26 under [principles](../library/governance/principles.md) 2-3:
priorities were re-judged at production load, and items that are already a stage's hard concept
were dropped from this list (the roadmap owns them).

## Scheduled

**Now**
- **E:** Design cards for P2-P4 with point 16 (production path), each before its R stage
  (DEC-006); P1's is written (DEC-035).
- **N:** Add point 16 (production path) to the P5 design card.

**R1, P1 (remaining nice-to-have)**
- **N:** Finglish repair on P1's report (Perso-Arabic leaked in a `lab-brief` run).

- **N:** From an outside review (Gemini, 2026-10-11), triaged:
  - A read document's text lives three times in a research run's checkpoints: the tool
    message's content, its artifact, and `ResearchState.documents`. A content-addressed
    document store (state keeps ids, the claim check resolves text) removes the copies.
    Trigger: a durable production checkpointer (P7), or a checkpoint DB over 100 MB.
  - Shadow mode for the Jev model router (ADR-0031): log its pick beside the tier actually
    used, to calibrate before it routes. Scheduled with D1.
  - Step counts in eval-lite (searches, rewrites, review rounds) to catch loop drift inside
    the budgets. Scheduled with D1.
  - Pre-write claim-to-section mapping in P6's outline node (`OutlineSection.claim_indices`),
    so parallel `Send` section writers receive only their assigned `supported` claims and don't
    repeat facts across sections. Scheduled with P6-B2.
  - Built in R1->R2 hardening (2026-10-11): `mypy src/agentlab` in CI; P3 sandbox verification
    against `refactored_code`; R1 `page_window` around cited passages past 12k chars and claim
    deduplication in `_merge`; `ModelRouter.runnable()` for LCEL chains; `lab-research --depth`
    and `verify_research` claim cap; `CHAT_MODEL_MAX_RETRIES = 1`; `prune_checkpoints` in
    `sqlite_db_data.py`.
  - Not taken: an `interrupted` envelope status (already P7-B3); a 2-5 s decider timeout
    (measured p95 reaches 8-10 s, so a tighter cut would fail open on healthy calls).

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
| Move a call site to `model_router` (first candidates: the RAG answer, the research report) | E | `evals/model_route_eval.py` is run on the real decider, the thresholds are fitted, and a shadow run (router vs the fixed tier) has been read |
| Route by specialty (code, writing, research) as well as difficulty | N | R2's catalog calibration measures which provider of a tier is better at which work |
| Add `opensource` to the router's tiers | N | The `opensource` measurement above is done (RSK-08) |
| Measure the `opensource` tier on this repo's structured-output schemas and tool calling | E | Requested from research (LD-005); required before any more call sites move to that tier |
| Embedding-provider failover (Gemini 3072-dim vs OpenAI 1536-dim collections) | N | A composed workflow must survive an embeddings outage (review at P6-B2) |
| Grow the P5 security guard into a policy-parameterized security agent | N | A second consumer needs tools in its judgment: documents in P7, action permissions in P8 or P11 |
| DeepAgents harness profiles | N | A fallback model needs different prompts or tool descriptions than the primary |
| Semantic search over memory (per fact, index kept in sync on every write) | N | Memory that can't load whole: episodic memory, or customer context at support scale (P8-B1); plan it as its own stage then |
| HITL "edit" decision for sandbox commands | N | A stage whose approvals need argument edits rather than approve/reject |
| Sandbox filesystem snapshots alongside checkpoints | N | Time travel over side effects is taught (Term E, E1) |
| Session-scoped or remote sandbox workspaces | N | Term E, E1 |
| A weekly cloud routine running the upstream watch (DEC-020) | E | The watch procedure is written (research queue in STATE) |
| Development-loop hooks, advisory: document health, a done gate, shell edits and ownership, meaning-level conventions (DEC-025) | N | The build queue after R1; the user's explicit yes before a hook sends session content or a replay reads transcripts |
| Rename `TIER_CASCADE_ORDER` to a fallback order (DEC-025) | N | The quality escalation lands (D1) |
| `repo_insight` grows from a relay into a codebase orchestrator: the RAG agent, code review, the interpreter, and repository history behind one goal (ADR-0030) | N | P8 A2's RAG role agent exists; until then its relay prompt is known debt |

## Deep-dive candidates

None yet ([pedagogy](../library/teaching/pedagogy.md#digressions-and-deep-dives)).

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
  `library/architecture/decision-models.md`, the facts stay in the research record's landscape (DEC-025).
- **Surface approvals raised inside subagents:** the hard concept of P6-B3.
- **R1 stop condition (`EvidenceStopMiddleware`) and coordinator `researcher` subagent over `run_research`:** built and taught in R1 (closed 2026-10-11).
- **`mypy src/agentlab` in CI and `prune_checkpoints` for SQLite DBs:** built 2026-10-11 in R1->R2 hardening.
