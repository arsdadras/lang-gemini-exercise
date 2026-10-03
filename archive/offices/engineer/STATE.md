> Archived 2026-10-03 by lead. The engineer role was folded into the lead ([ADR-0025](../../../docs/adr/0025-two-roles-lead-and-mentor.md)); the lead's office, [offices/lead/](../../../offices/lead/README.md), carries its work.

# Engineer State

Read first in every engineer session; rewrite it, don't append. Seeded by the lead on
2026-09-28 ([ADR-0022](../../docs/adr/0022-engineer-role-and-division-of-labor.md)); the
engineer owns it from its first session (2026-10-03).

## Now

- **Session 1 (2026-10-03)** adopted the office, did LD-024, MN-014, and LD-019 items 1-3. It ran in
  the desktop app's own worktree (branch `claude/jolly-satoshi-297451`), because that session
  couldn't move into `../lce-engineer`; the ownership guard allowed only the session's own
  worktree. Later sessions should start in `../lce-engineer` (branch `engineer`), which only
  fast-forwarded to `origin/main` and holds no work.
- **Verified at handoff:** `uv run pytest` 225 passed, `ruff check` and `ruff format --check`
  clean, `check_docs.py` 0 problems; embeddings and Tavily answered live.
- **Build queue (LD-019):** items 1-4 are done. **Item 5 is left:** untrack and delete
  `src/data/dbs/checkpoints.db` (3.7 MB, tracked, so git history keeps it). The permission
  classifier refused the `git rm` in session 1 as irreversible local destruction, so the user
  has to run `git rm src/data/dbs/checkpoints.db` (or allow it); nothing else references it.

## Built, awaiting the mentor

- **Eval-lite harness** (`utils/eval_util.py`, seeds in `evals/datasets/`): LD-019 item 1,
  announced in EN-005. Decision-point scenarios inject their decider; R1 is the first consumer.
- **Per-app checkpoint databases and the worker prompt** (LD-019 item 4): `checkpoint_db_path(app)`
  in `paths_config.py`; `resolve_session` lists and resumes from the app's own database; delegated
  runs (the coordinator's interpreter worker, the code-review subagent) use the `delegations`
  database. `make_interpreter_agent(worker=True)` takes `prompts/template/worker.py`'s lean prompt
  (English, no user profile, Finglish, or response modes). Core: `session_util.resolve_session`
  and `worker.py`. Old sessions in `out/state/checkpoints.db` are no longer read.
- **Real-graph RAG routing test** (`tests/test_rag_graph.py`, helper `scripted_rag` in
  `tests/fakes.py`): MN-014.

## Live code issues

Taken over from the mentor's state (LD-018). Program-level debt is the lead's
[BACKLOG](../lead/BACKLOG.md).

- **Coordinator shell has no approval step:** approvals raised inside a subagent aren't surfaced
  to the CLI; the banner states it. Fix: P6-B3.
- **Old checkpoint DB still tracked:** `src/data/dbs/checkpoints.db` (a consistent copy is at
  `out/state/checkpoints.db`). LD-019 item 5, waiting on the user.
- **RAG index must be rebuilt:** `.chroma_index` predates the restructure, and its vectors are
  Gemini's; the embedding model is now GapGPT's `text-embedding-3-small` (1536 dimensions), so
  the old index can't answer queries. The corpus list also names different files now. Rebuild in
  R2 (paced; minutes); the paced batch size and delay were sized for Gemini's free quota and
  GapGPT's limits are unmeasured.
- **Dead code:** `middlewares/groundedness_middleware.py` (wired in R1) and
  `utils/time_travel_util.py` (removed in R5 unless a consumer appears).
- **Personal data in traces:** only P5 masks before upload. R5.
- **Perso-Arabic script in long P5 replies:** repair cuts leaked lines by about three quarters
  (`EV-2026-09-17-finglish-line-repair`); the repair's current model hasn't been re-measured
  (research, LD-005). The root cause is the assistant model.
- **`local` tier is opt-in only:** works end to end but takes 90-360 s per structured call
  (`EV-2026-09-23-local-ollama-qwen`, [ADR-0015](../../docs/adr/0015-local-tier-and-test-mode-profiles.md)).
- **New, from item 2:** `utils`' retry story is one layer per call, but the OpenAI SDK retries
  twice by default, so a hosted chat call can take up to three timeouts (3 x 120 s) per provider
  before the fallback switches. Worth a number the lead picks (SDK `max_retries` per spec).
- **New, from item 2:** `_TimeoutSearchWrapper` (`tools/web_search_tool.py`) replaces
  langchain-tavily 0.2.18's two request methods, because the library sets no timeout. Remove it
  once the library takes one; the tests in `tests/test_timeouts.py` show what to check.
