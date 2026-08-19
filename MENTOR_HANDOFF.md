# Mentor Handoff

**Read this file first, every session, before touching code.** It exists because a mentor's context
window fills up eventually and the thread loses track of what's going on. Update it — don't just
append to it — at the end of every session, or as soon as you notice your own context getting long.

## Your role

You are acting as a hands-on mentor for a developer who has completed LangChain Academy's
LangChain/LangGraph/DeepAgents courses and now wants **practical, production-track project work**,
not more tutorials. Read `ROADMAP.md` for the full curriculum shape before anything else — it defines
six projects (P1–P6), each with a Phase A (baseline) → B (growth) → C (professional) arc, building
toward P6, a capstone that composes Phase-C pieces from P1–P5.

The stated goal is to reach **production-grade** competence, not just "it runs once." That means:
real error handling boundaries, tests that actually run (`uv run pytest`), docs that match reality,
and code the mentee could defend in a review — not scaffolding for its own sake.

### How to mentor here

- Move step by step, phase by phase — don't dump an entire phase in one message. Send one
  meaningful chunk of code at a time with explanation of *why*, not just what.
- Explain the non-obvious parts: framework API shape, why a middleware/interrupt/checkpoint
  works the way it does, what would break without it. Skip explaining things a course grad
  already knows.
- Point out real repo issues when you find them (stale docs, broken tests, dead imports) —
  don't silently fix things that affect the mentee's own in-progress work without saying so.
- Verify claims: run the tests, run `py_compile`/import checks, actually read library source
  under `.venv/Lib/site-packages/` when unsure of an API shape — don't guess from training data.
  This project's history includes real bugs from guessed API shapes; see "Known issues" below.

## Current status snapshot — 2026-08-19

| Project | Status |
|---|---|
| **P1 — Research Agent** | Phase A ✅, Phase B ✅, Phase C 🔶 in progress (see below) |
| P2 — RAG Agent | Not started |
| P3 — Code Review & Test Gen Agent | Not started |
| P4 — Sandbox/Interpreter Agent | Not started (`tools/db_ops.py`, `tools/file_ops.py` were scaffolded early then intentionally deleted — rebuild them here, not before) |
| P5 — Memory-Rich Personal Assistant | Not started |
| P6 — Capstone | Not started |

### P1 — Research Agent — detailed state

**Working today:** `src/app.py` builds a `deepagents.create_deep_agent` with:
- `lite_model` (Gemini) as the orchestrator model
- `web_search` (Tavily) as the only top-level tool
- `retry_on_failure` middleware — retries once on a fallback model (`luna_model`, GapGPT-routed) if the primary call raises
- `search_approval` middleware — `HumanInTheLoopMiddleware` interrupts on every `web_search` call for approve/edit/reject, requires the `InMemorySaver` checkpointer to resume across the interrupt
- `response_format=ResearchReport` — structured, cited final output
- `subagents=[researcher_subagent]` — a scoped sub-researcher (`src/subagents/researcher.py`) that answers one sub-question at a time and returns structured `ResearchFindings`, so the orchestrator can delegate distinct sub-questions instead of doing everything in one long context

This is Phase A + Phase B complete, and the "research subagents per topic scope" bullet of Phase C
is now wired in.

**Phase C remaining (pick up here next session):**
1. **LangSmith tracing** — `.env` already has `LANGSMITH_API_KEY`, `LANGSMITH_ENDPOINT`,
   `LANGSMITH_PROJECT`, `LANGSMITH_TRACING` provisioned. This is likely just enabling tracing and
   doing a first traced run + look at the trace together — a good next lesson, low setup cost.
2. **Evaluation datasets** — not started.
3. **SDK-exposed multi-session service** — not started.
4. **Optional RAG overlay** — not started, explicitly optional per roadmap.
5. Memory for recurring research preferences (a Phase B item) was also explicitly deferred — still open, lower priority than the Phase C items above.

**Not yet done, worth doing before the next feature:** the mentee has never confirmed a full
end-to-end run of the current agent (with real API calls) since the subagent rewiring landed — the
`while "__interrupt__" in result` loop in `app.py` has only been exercised for import/compile
correctness in this session, not a live run. Good first move next session: run it together, watch
the HITL prompt actually appear, approve it, and see a `ResearchReport` come back with the
researcher subagent's findings folded in.

## Known issues fixed this session (2026-08-19) — read before assuming these are still broken

- **Unresolved merge conflict markers committed to `main`.** Commit `6140cfb` landed with raw
  `<<<<<<<`/`=======`/`>>>>>>>` markers still in 9 files (middleware, models, prompts, schemas,
  subagents) — a merge was accepted/committed without resolving conflicts. This was already pushed
  to `origin/main` before being caught. Fixed in commit `05ab606`. **If you see markers like this
  again, it means the same VS Code Source-Control workflow mistake happened again** — the fix is to
  resolve conflicts properly before committing, not to `git reset --hard`.
- **HITL interrupt silently never firing.** `middleware/hitl.py`'s `interrupt_on` key was
  `"search_web"` but the tool is registered as `"web_search"` (`tools/search.py`) —
  `HumanInTheLoopMiddleware` matches by exact tool name, so the mismatch meant approval was silently
  skipped and the agent ran unattended. This got fixed once, then **reintroduced by the same bad
  merge above** as one side of a conflict, then fixed again during conflict resolution. Currently
  correct (`"web_search"`). If HITL stops pausing again, check this key first.
- **`KeyError: 'tool_call'` when printing interrupt info.** `app.py` read
  `request['tool_call']['name']`/`['args']`, but `HumanInTheLoopMiddleware`'s `ActionRequest`
  TypedDict is flat (`{name, args, description}`, no nested `tool_call`) — see
  `.venv/Lib/site-packages/langchain/agents/middleware/human_in_the_loop.py:38-48`. Fixed by reading
  `request['name']`/`request['args']` directly.
- **Duplicate subagent implementations.** The bad merge left two competing subagent modules:
  `subagents/research.py` (`topic_researcher` dict, no structured output) and
  `subagents/researcher.py` (`researcher_subagent` dict, with `response_format=ResearchFindings`).
  The mentee had already started migrating `app.py` to the better one (`researcher_subagent`) before
  this session — that migration is now finished: `subagents/research.py` deleted, `app.py` wired to
  `researcher_subagent`.
- **`tools/db_ops.py`, `tools/file_ops.py`, `data/guidelines.py` deleted** (by the mentee, mid-session,
  uncommitted at the time) — these are P4-scope, not needed for P1. `data/__init__.py` still imported
  the deleted `data.guidelines`, which would `ImportError` the moment anything imported the `data`
  package; fixed to a plain placeholder docstring.
- **Test suite was fully broken — 0 tests could even collect.** `tests/test_tools.py` imported
  `tools.db_ops` (deleted) and `FileData`/`create_file`/etc. from `tools` (never existed in `tools/__init__.py`
  as currently written); `tests/test_models.py` imported `from state import ...` but `src/state/` doesn't
  exist. Both were stale tests for the P4-scope modules above and were deleted (confirmed with the
  mentee first — this is a real destructive action, always confirm before deleting tests/data).
  `tests/test_prompts.py` also failed: `from prompts import DEFAULTS` — `prompts/__init__.py` never
  re-exported `DEFAULTS` from `prompts/template.py`. Fixed. **`uv run pytest` is green again (5 passed)**
  as of this session — verify it's still green before adding new code on top.
- Removed dead imports from `app.py`: `anthropic.types.anthropic_beta_param` (unused, looked like
  IDE-autocomplete debris), `os`, `flash_model` (unused at call-site level).

## Environment / secrets present in `.env`

Google Gemini (`GOOGLE_API_KEY`), Tavily (`TAVILY_API_KEY`), GapGPT proxy
(`GAPGPT_API_KEY`, `GAPGPT_BASE_URL` — OpenAI-compatible, used for `luna_model`/`terra_model`
fallback routes), and LangSmith (`LANGSMITH_API_KEY`/`ENDPOINT`/`PROJECT`/`TRACING`) are all already
configured. Don't ask the mentee to go set up LangSmith from scratch — it's ready to wire in.

## Working agreements (from `AGENTS.md` — read the full file too)

- `uv run pytest` must pass before declaring anything done — paste real output.
- Confirm before: schema/migration changes, `git push --force`/history rewrite/branch deletion,
  prod config/secrets changes, deleting/truncating data (tests included, per this session).
- Verify LangChain/LangGraph API shapes via the `docs-langchain` MCP server or by reading
  `.venv/Lib/site-packages/` source — don't assume an API shape from training data. Several bugs
  fixed this session trace back to unverified assumptions.
