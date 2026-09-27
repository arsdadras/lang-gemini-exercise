# Backlog

Every candidate that isn't a stage's hard concept, triaged by the lead. **E** = essential,
**N** = nice-to-have. An item is either scheduled into a named stage (the Definition of Ready
pulls it in) or parked behind a concrete trigger. The mentor's live code issues stay in its
[state](../mentor/STATE.md); new ideas arrive as request or notice messages and are triaged here.

Re-triaged from the handoff backlog on 2026-09-26 under [principles](../../library/governance/principles.md) 2-3:
priorities were re-judged at production load, and items that are already a stage's hard concept
were dropped from this list (the roadmap owns them).

## Scheduled

**Lead, now**
- **E:** Design cards for P1-P4 with point 16 (production path), each before its R stage: P1
  before R1, P2 before R2, P3 before R3, P4 before R4 (DEC-006).
- **E:** Record the R0 specialist contract as an ADR when R0 closes, from the mentor's state.
- **N:** Add point 16 (production path) to the P5 design card.

**Lead, when the user says the working tree is clean** (user direction 2026-09-27; the mentor
and research have committed their current work first; recorded in DECISIONS.md with an ADR when
implemented; then `git-policy.md`, `dev-environment.md`, `protocol.md` "Sessions", `AGENTS.md`,
and `CLAUDE.md` follow, and LD messages tell the mentor and research how to move in; verified on
Windows)
- **E: (a) One worktree and branch per role.** `../lce-lead`, `../lce-mentor`, `../lce-research`
  on branches `lead`, `mentor`, `research`, each with its own `.venv`; every role reaches `main`
  by pull request, CI gates, the lead merges. Removes the shared working tree (RSK-01, RSK-11)
  and the shared-`.venv` breakage. To settle while building it:
  - `.env` is copied into each worktree (gitignored); never a parent-directory `.env`, which
    `load_dotenv()`'s upward search would also hand to sibling projects.
  - Runtime data is per checkout (`out/`, `.chroma_index/`, P5's SQLite): the mentor's worktree
    takes over the current `out/state/` and index; lead and research start empty.
  - The learner types exercises in the mentor's worktree, so the IDE opens it; `alireza/`
    stays in the main checkout, which stays on a clean `main` and runs no session.
  - `scripts/inbox.py` reads every role's outbox from `origin/<role>` as well as `main`, so a
    message doesn't wait for a merge.
  - Verify in the Claude Code docs whether auto-memory is shared across a repo's worktrees or
    keyed by path; the mentor's memories must stay reachable from its worktree.
  - Shared files with more than one writer (`AGENTS.md` sections, `uv.lock`) are the only
    expected merge conflicts; keep role paths disjoint.
- **E: (b) Identity in role files, not sessions.** Sessions are short and disposable; each
  starts with `/lead`, `/research`, or the mentor default and rebuilds context from its
  `STATE.md` and inbox, instead of one long session compacted again and again.
- **E: (c) Hooks in `.claude/settings.json`** (verify the hook API in the Claude Code docs; test
  on Windows). SessionStart prints `git status`, the head of the role's `STATE.md`, and its
  inbox, taking the role from the worktree's branch; Stop warns about uncommitted changes and
  never blocks (the mentor's exercise state is uncommitted on purpose). Hook commands run a
  Python script through `uv run` so they behave the same on every shell.
- **E: (d) A `/handoff` skill** for a session's end: update `STATE.md`, commit (a `wip:` commit on
  the role branch if unfinished), push, and print a three-line summary. Pull requests are
  squash-merged, so `wip:` commits never reach `main`. Switching between local and cloud then
  needs only a pull.

**R0, the specialist contract** (mentor-direct)
- **E:** Shared eval-lite harness; first consumer R1.
- **E:** Chat prompts split from worker prompts (the chat template reaches every agent today).
- **E:** Per-app checkpoint databases, so `list` stops mixing apps' threads.
- **E:** Untrack and delete the old `src/data/dbs/checkpoints.db` (needs the user's OK: deleting
  data).
- **E:** An explicit timeout on every external call: models, embeddings, search, HTTP. A call
  that can hang forever never produces a failure the contract can classify (LD-006).
- **E:** Evidence IDs in code comments that carry measurements (LD-008).

**R1, P1**
- **E:** The unused groundedness middleware wired in for citation checks.
- **E:** A search budget replaces approving every search.
- **N:** Finglish repair on P1's report (Perso-Arabic leaked in a `lab-brief` run).
- **N:** Decide whether the coordinator's `researcher` becomes a `CompiledSubAgent` over
  `run_research`, once the budget exists.

**R2, P2**
- **E:** Incremental re-index with stale-source detection; rebuild the stale index; index the
  agents and apps as well.
- **E:** Ungrounded answers rerouted to query rewrite or web search instead of a disclaimer.
- **E:** The groundedness check on the web fallback path too.
- **N:** Batch document grading.
- **E:** Hybrid retrieval (BM25 + vector + reranker) as the first change judged by R2's metrics
  (DEC-013).

**R3, P3**
- **E:** Diff and multi-file input.

**R4, P4**
- **N:** Carry the typed envelope into a DeepAgents coordinator's state, not only its text (extra
  state keys from a `CompiledSubAgent` reach the parent).

**P5 teaching pass**
- **E:** Compare assistant models in C2: script leakage per line, false "saved" claims, guard
  agreement. The Finglish repair only mitigates the leak.

**R5, close**
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
| A TypeSafe API key, so Jev can be measured against the other deciders | N | Before P8-C2 closes; a user action (research's OB-07) |
| Embedding-provider failover (Gemini 3072-dim vs OpenAI 1536-dim collections) | N | A composed workflow must survive an embeddings outage (review at P6-B2) |
| Grow the P5 security guard into a policy-parameterized security agent | N | A second consumer needs tools in its judgment: documents in P7, action permissions in P8 or P11 |
| DeepAgents harness profiles | N | A fallback model needs different prompts or tool descriptions than the primary |
| Semantic search over memory (per fact, index kept in sync on every write) | N | Memory that can't load whole: episodic memory, or customer context at support scale (P8-B1); plan it as its own stage then |
| HITL "edit" decision for sandbox commands | N | A stage whose approvals need argument edits rather than approve/reject |
| Sandbox filesystem snapshots alongside checkpoints | N | Time travel over side effects is taught (Term E, E1) |
| Session-scoped or remote sandbox workspaces | N | Term E, E1 |
| (e) Automatic awareness of new messages: the SessionStart inbox hook; a `/loop` in a long-running session that checks the inbox every N minutes; scheduled cloud routines (research's upstream watch); a GitHub Actions job listing new open messages on each push to `main` | N | (a)-(d) have run for a week without coordination trouble |
| Library placement of research's `library/engineering/decision-models.md` (written outside its office, not in the index; its content is untouched until then) | E | The user opens the Jev file ("parvande-ye Jev ro shoru konim"); the placement is a lead decision |

## Deep-dive candidates

None yet ([PEDAGOGY.md](PEDAGOGY.md#digressions-and-deep-dives)).

## Closed in triage

- **Wire `rag_subagent` into the researcher:** superseded by P6-A1, where the workflow composes P1
  and P2 instead.
- **System-1 decision layer:** now a planned stage, P8-C3 (DEC-004).
- **Surface approvals raised inside subagents:** the hard concept of P6-B3.
