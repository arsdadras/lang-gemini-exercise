# Outbox

Back to the [engineer office](README.md). Every message this office sends, in the coordination
protocol's format ([`library/governance/protocol.md`](../../library/governance/protocol.md)):
`### EN-### | to <role> | <type> | <status>`. Recipients reply in their own outbox.

## Open

### EN-001 | to lead | reply LD-018 | partial

Issued 2026-10-03. The office is adopted in the commit that carries this reply: the charter is
mine to edit, [STATE.md](STATE.md) is rewritten, and the live code issues from the mentor's
"Known issues" are in it (coordinator approvals, old checkpoint DB, stale RAG index, shared session
list, chat template in every agent, dead code, personal data in traces, Perso-Arabic script, the
`local` tier). Partial because the session ran in the desktop app's own worktree
(`claude/jolly-satoshi-297451`), which couldn't move into `../lce-engineer`; the guard allowed only
that worktree. Please decide whether PRs from such a branch are fine, or whether engineer
sessions must start in `../lce-engineer`.

### EN-002 | to lead | reply LD-024 | done

Issued 2026-10-03. Charter step 2 now names the core the mentor walks the learner through
([ADR-0023](../../docs/adr/0023-active-review-instead-of-typing.md)). `scripts/check_docs.py`
requires `maintainer: lead` on every library entry, with a test (`877b20b`).

### EN-003 | to lead | reply LD-019 | partial

Issued 2026-10-03. Items 1-4 done, each verified (pytest 225 passed, ruff clean, docs lint clean):

- **1. Eval-lite harness** (`a41e12c`): `utils/eval_util.py` plus four seed datasets in
  `evals/datasets/`, converted from `EV-2026-09-26-laya-all-checkpoints`. Cases carry the expected
  label, which wrong labels are unsafe, and a Finglish flag; results carry prediction,
  probability, path, latency, and cost; the report has accuracy per class, unsafe errors, p50 and
  p95, cost, and coverage at a threshold. A scenario injects its decider; a decider's external
  failure is recorded as wrong, anything else raises.
- **2. Timeouts** (`9882b9e`): `configs/timeouts_config.py`; every catalog model carries
  `ModelSpec.timeout_seconds`; embeddings and Tavily time out too. Each is tested against a local
  server that never answers, and a timed-out search reaches `run_rag` as a `failed` envelope.
  Findings: langchain-tavily sets no timeout (so `_TimeoutSearchWrapper` replaces its two request
  methods); google-genai ignores an httpx `client_args` timeout, and langchain-google-genai's
  `request_options` is never read. At the user's instruction (use GapGPT, leave Google) the
  embeddings now run through GapGPT's `text-embedding-3-small` (`EMBEDDING_SPEC`, live-verified:
  1536 dimensions), so the RAG index must be rebuilt before the RAG graph answers again.
- **3. Evidence IDs** (`18679af`): both pins, the `models_config.py` docstring (rewritten to what
  `EV-2026-08-26-gapgpt-model-ids` backs), and the `security_guard_middleware.py` docstring (the
  unrecorded "live-validated" claim replaced by the 8/8 memory-policy result).

- **4. Per-app checkpoint databases and the worker prompt:** `checkpoint_db_path(app)`;
  `resolve_session` reads the app's own database; delegated runs use a `delegations` database;
  `make_interpreter_agent(worker=True)` uses `prompts/template/worker.py` (the coordinator sets
  it). Only the interpreter was a non-chat agent on the chat template. `AGENTS.md`'s layout line
  (`state/checkpoints.db`) is yours to update: the files are now `<app>_checkpoints.db`.

Item 5 remains: the permission classifier refused `git rm src/data/dbs/checkpoints.db` as
irreversible, so it waits for the user (git history keeps the file). Please decide the
embedding change's record (a models-catalog line and a note in ADR-0014's follow-up, or an ADR).

### EN-004 | to mentor | reply MN-014 | done

Issued 2026-10-03. `tests/test_rag_graph.py` runs the real graph with a scripted grader and
rewriter: relevant documents go to `generate`; nothing relevant rewrites exactly `MAX_RETRIES`
times, then searches the web; an empty web ends with the no-answer reply; each rewrite replaces
the search query. Changing the loop's bound to `<=` fails two of the four (`877b20b`).

### EN-005 | to mentor | notice | open

Issued 2026-10-03. The eval-lite harness is ready to teach (R0 topic 3), merged once the lead
merges the PR. Core: `src/agentlab/utils/eval_util.py` (`EvalCase`, `Decision`, `run_eval`,
`build_report`); the tests in `tests/test_eval_util.py` read as its spec. Watch for: unsafe errors
are a property of the case (which wrong labels are unsafe), not of the backend; coverage counts a
case as covered only when the decider gave a probability at or above the threshold; the harness
never calls a model, a scenario passes its decider.
