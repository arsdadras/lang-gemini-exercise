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

- **The exact workflow for new lesson code, pinned down on 2026-08-19 after two failed attempts:**
  1. Break the work into small stages.
  2. At the start of each stage, send the real working code for that stage as **code blocks in the
     chat message — never write/edit it directly into the mentee's repo files.** They apply it
     themselves.
  3. Calibrate explanation depth: brief for ordinary/simple parts; fuller and clearer for important
     or complex parts; deeper and more precise for general/strategic matters — architecture, design
     decisions, why-this-not-that (not limited to just those two, but that's the shape).
  4. One stage at a time — don't send the next stage until this one has landed.

  What this replaced: first attempt was writing a complete feature end-to-end myself with no pause
  point (repo's own git history already had multiple `revert: remove AI-authored X` commits from an
  earlier mentor session doing exactly that — the signal was there and got missed). Second attempt
  overcorrected into bare skeletons with blanks for the mentee to fill in solo, which also isn't
  right — the mentee wants to see real code, just delivered in small stages via chat, not silently
  placed in their repo. If future drift happens either direction, re-read this and the exchange it
  came from.
- **Session 0, pinned down 2026-08-20:** before Phase A of any *new* project (P3, P4, P5, P6 when
  their turn comes), give a short briefing first — problem statement, what each phase (A/B/C) adds,
  what frameworks/patterns come in, how it feeds P6 — no code, just orientation, same depth as the
  P2 walkthrough that opened the "P2 — RAG Agent" section below. Purpose is purely so the
  mentee knows the road ahead before stage-by-stage work starts.
- **Check repo-wide impact, 2026-08-23:** before presenting any stage's code, grep the whole repo (not just the file being changed) for stale references to the old behavior and other code that now needs to adapt — fix/update both, don't scope the check to only the new/edited code. Exception: `alireza/` is the mentee's own separate scratch/practice area (e.g. `alireza/P2_RAG/` — a parallel, independently-named exploration of the same concepts) — out of scope for this check, not something to keep in sync with `src/`.
- **Phase/project bookends, 2026-08-24 (refined same day):** short intro before each phase (A/B/C)
  starts — the phase's **overall goal**, roughly what stages, and **explicit in/out-of-scope
  boundaries** (what this phase covers vs. what's deferred to a later stage or out of the course
  entirely) — not just a bare stage-name list, that left the mentee unsure mid-phase and caused the
  very scope-clarifying questions the intro should've prevented. Not too long either — land between
  "just names" and a long essay. Short summary after each phase ends — what got built, what was
  learned, what's carried forward. Same at project level (P1, P2, ...) but higher-altitude: the
  project's overall problem/shape, not stage detail — project-start intro is essentially "Session 0"
  (see below); project-end summary is the same altitude in reverse.
- **Delivery ordering flipped, 2026-08-23:** the workflow above (break into stages, code as chat blocks) still stands, but two things changed: (1) verify each stage's code yourself before sending it — temporarily apply it to the real files, run it, then revert those files back before sending the chat-block version, so what lands in chat is already known to work; (2) send the explanation *first*, in its own message with no code, then send the code only after the mentee has either asked their questions (answer those first) or shown no questions and understood. After the code, suggest test scenarios framed as the mentee's own exploration, not mentor-side verification — you already verified it. Any note that follows the code must be Python syntax/mechanics only (e.g. a stdlib quirk); architecture/design reasoning belongs solely in the pre-code explanation, never repeated after.
- **Architecture vs. polish, clarified 2026-08-20:** the deferred-scope decision below (LangSmith/
  eval/tests/deploy) is about *production hardening*, not about *architecture*. System-design growth
  (checkpointing, time-travel, subgraphs, `CompiledSubAgent` composition, hybrid retrieval, guardrails)
  is the roadmap's actual point and is NOT deferred — it's taught every phase, per `ROADMAP.md`'s
  Advanced Features Map. Don't undersell architecture teaching thinking it's in the deferred bucket.
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

**Explicit scope decision (2026-08-19):** the mentee wants to prioritize code/syntax/technique/
strategy/design/architecture across projects for now. **LangSmith, evaluation datasets, formal
test-writing, and SDK/deploy exposure are deliberately deferred** to a dedicated session later —
don't proactively push those in during regular project work; wait until the mentee asks for that
dedicated round. Manually running/demoing an agent end-to-end to see the architecture work live is
fine and encouraged — that's different from writing a formal test suite.

## Current status snapshot — 2026-08-19

| Project | Status |
|---|---|
| **P1 — Research Agent** | Phase A ✅, Phase B ✅, Phase C ✅ for current scope (see below) |
| **P2 — RAG Agent** | ✅ Phase A ✅ Phase B (4/4 stages, verified 2026-08-24; Stage 5/LangSmith deliberately deferred) — Phase C next (see below) |
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

**Phase C remaining — deliberately deferred, not forgotten:**
1. **LangSmith tracing** — `.env` already has `LANGSMITH_API_KEY`, `LANGSMITH_ENDPOINT`,
   `LANGSMITH_PROJECT`, `LANGSMITH_TRACING` provisioned, ready to wire in whenever the
   observability/eval/deploy session happens.
2. **Evaluation datasets** — deferred, same session as above.
3. **SDK-exposed multi-session service** — deferred, same session as above (deploy-scoped).
4. **Optional RAG overlay** — explicitly optional per roadmap; likely superseded by P2 anyway.
5. Memory for recurring research preferences (a Phase B item) — still open, low priority.

**Verified 2026-08-19:** the mentee ran P1 end-to-end live (own initiative, before this note) —
HITL interrupt fires, approval loop works, `ResearchReport` comes back with the researcher
subagent's findings folded in. P1 is done for current scope; **now moving to P2.**

### P2 — RAG Agent — detailed state (2026-08-20, updated same day after Phase A finished)

**4-stage Phase A plan — all done, verified end-to-end:**
1. `state/rag.py` — `RAGState` TypedDict (`question`, `documents`, `generation`) — ✅ mentee applied it
2. `retrieval/index.py` + `retrieval/__init__.py` — offline ingest (chunk+embed+persist to Chroma) and
   `get_retriever()` for query-time — ✅ mentee applied it, one self-authored bug found+fixed
   (see below), `.chroma_index/` builds cleanly
3. `graphs/rag/` — retrieve → grade_documents → conditional-edge → generate/no_relevant_docs graph
   (`build_rag_graph()`) — ✅ mentee applied it (own initiative: split node prompts out into
   `prompts/rag.py` rather than keeping them inline in the graph file — fine, matches the project's
   existing pattern of `prompts/research.py` holding P1's prompt). Originally landed as a single flat
   `graphs/rag.py`; restructured into a `graphs/rag/` package on 2026-08-23 — see the Phase B note below,
   this path is stale in any older note that still says `graphs/rag.py`.
4. `apps/rag.py` — entry point, originally `src/rag_app.py`, moved to a root-level `apps/`
   directory (sibling of `src/`) on 2026-08-24 and renamed to match the repo's dir=kind/file=project
   convention (`apps/rag.py`, `apps/research.py` — same shape as `state/rag.py`, `schemas/rag.py`).
   `src/research_app.py` moved to `apps/research.py` at the same time. See the "Entry points moved
   to `apps/`" note below — this path is stale in any older note that still says `src/rag_app.py` or
   `src/research_app.py`. — ✅ mentee applied it

**Verified live 2026-08-20:** ran `uv run python src/rag_app.py` twice — a corpus-relevant question
returned a grounded, source-cited answer; an irrelevant question (`"what is the capital of France?"`)
correctly fell through `route_after_grading` to the `no_relevant_docs` fallback instead of hallucinating.
**Phase A is done.**

**Phase B, Stage 1 — corrective-RAG loop — done, verified 2026-08-23.** `RAGState` gained `search_query`
(mutable, defaults to `question` via `state.get("search_query", state["question"])`) and `retries`
(counter, absent from state until first increment — always read via `state.get("retries", 0)`).
`route_after_grading` now three-ways: docs survived → `generate`; empty & `retries < MAX_RETRIES` (2) →
`query_rewrite` (LLM reformulates the query, increments `retries`) → loops back to `retrieve`; retries
exhausted → `no_relevant_docs`. Verified: a corpus-relevant question skips the loop entirely; a fully
unrelated question exhausts both retries and correctly falls to the fallback; note that a *partially*
relevant one can exit the loop after just 1 retry via `generate` answering "I don't know" instead of
reaching `no_relevant_docs` — both are legitimate anti-hallucination paths (one code-level, one
prompt-level honesty), not a bug, and which one fires depends on the (deliberately lenient) grader.

**Standing architecture convention set 2026-08-23 — nodes vs. graph-wiring split, for every raw
`StateGraph`-based module (not DeepAgents-based ones like P1, which has no direct analog):** node
functions live in `graphs/<name>/nodes.py`, graph assembly (`add_node`/`add_edge`/routing functions/
`build_*_graph()`) lives in `graphs/<name>/graph.py`, package `__init__.py` re-exports the builder.
`graphs/rag.py` was restructured into `graphs/rag/{nodes.py, graph.py, __init__.py}` under this
convention. **Rationale, worth remembering because the mentor initially got this wrong:** the mentor's
first instinct was to reject the split using the same "only split when there's actual reuse" reasoning
used earlier for the retrieval/embedding file question — the mentee correctly pushed back: (1) that
reuse-only lens doesn't fit here, this split is about separating business logic from orchestration/
wiring, a legitimate scale-independent boundary, not a reuse-driven one; (2) one of the project's
explicit goals is practicing production-grade structuring habits, so "our current scale doesn't need
it" is the wrong criterion to reject a convention on; (3) this repo is one system spanning P1–P6, not N
independent toy projects, so a structural convention should be decided once, consistently, while it's
still cheap — not per-project by size. The mentor was convinced and did the refactor directly (mentee
had explicitly authorized "do the cleanup if convinced" for this one). **Apply this convention forward
to every new raw-StateGraph graph without re-litigating it** — P2 Phase B/C's later nodes, P3's review
graph, etc. Don't retrofit P1 — different framework, no nodes/wiring duality to split.

**Phase B, Stage 2 — checkpointing — done, verified 2026-08-24.** `build_rag_graph()` compiles with
`checkpointer=InMemorySaver()` (matches P1's `middleware/hitl.py` pattern). `apps/rag.py` now loops
on a fixed `thread_id`, one `invoke()` per question. Because `RAGState`'s `search_query`/`retries`
have no reducer, every `invoke()` call explicitly resets them (`{"question": q, "search_query": q,
"retries": 0}`) — otherwise they leak across turns on the same thread (verified with a manual
`update_state` seed test: a stale `search_query` from a prior turn silently overrode the new turn's
real question). Discussed with the mentee why a reducer doesn't fix this: a reducer only defines how
two values *merge*, it can't distinguish "new conversational turn" from "mid-turn retry loop" —
that distinction only exists in what the caller passes at `invoke()` time. Reducers are the right tool
for genuinely cross-turn *accumulating* state (e.g. a `messages` list with `add_messages`), not for
per-turn scratch fields like these — `RAGState` doesn't have cross-turn state yet, so no reducer is
needed for now.

**Entry points moved to `apps/`, 2026-08-24.** `src/rag_app.py` → `apps/rag.py`, `src/research_app.py`
→ `apps/research.py` — a new root-level `apps/` directory, sibling of `src/`, one file per project
(matches the existing dir=kind/file=project convention). This exposed a real, previously-latent gotcha:
the project resolves `from graphs...`/`from nodes...`-style absolute imports two ways — (1) when an
entry script sits directly inside `src/`, Python puts the script's own directory on `sys.path[0]`,
which happens to equal `src/`, so it resolves by accident; (2) the editable-installed `agent` package
(`pyproject.toml`'s `package-dir = {"" = "src"}`), which resolves regardless of the script's location
but only if its `top_level.txt` is current. Found that `top_level.txt` was **stale** — missing `nodes/`
and `configs/` (dirs the mentee had just added) — because `uv sync` doesn't always rebuild the editable
finder on its own. Fixed with `uv sync --reinstall-package agent`, then verified an entry file *outside*
`src/` entirely (`apps/rag.py`) imports and runs correctly end-to-end (multi-turn, no state leakage).
**Standing gotcha to remember:** any time a new top-level package directory is added under `src/`
(like `nodes/`, `configs/` were), run `uv sync --reinstall-package agent` (or equivalent) before
relying on imports from outside `src/` — otherwise the editable install silently doesn't know about it.

**`nodes/`, `configs/` restructure, 2026-08-24 (mentee's own follow-up on the nodes/graph split):**
mentee replaced the mentor's originally-delivered `graphs/rag/{nodes.py, graph.py, __init__.py}`
nested-package shape with `nodes/rag.py` + flat `graphs/rag.py` — i.e. applied the repo's
*pre-existing* dir=kind/file=project convention (already used by `state/`, `schemas/`, `prompts/`)
to the nodes/graph split instead of introducing a new dir=project/file=role shape. **Mentor agrees
this is the better call** — it's more consistent with a convention the repo already had before this
whole split discussion started, not a competing second convention. This supersedes the
`graphs/rag/` package-shape convention recorded below (still shown for history/rationale, but the
concrete shape is now dir=kind/file=project, applied to `nodes/`+`graphs/`+`configs/` alike).
Also added `configs/rag.py` (`MAX_RETRIES = 2`) as a separate module-level-constant file, imported by
`graphs/rag.py` — reasonable, same "hardcoded but isolated for easy tuning" pattern. The dead duplicate
`MAX_RETRIES` in `nodes/rag.py` has since been removed by the mentee — confirmed gone.

**`configs/` briefly moved outside `src/`, then reverted, 2026-08-24.** Mentee tried moving `configs/`
to a root-level dir (sibling of `src/`, like `apps/`) reasoning "separate from business logic" the same
way `apps/` was separated. Different from `apps/`: `configs/rag.py` is *imported by* other `src/`
modules (`graphs/rag.py`), not an executed entry point — moving it outside `src/` breaks packaging, not
just dev convenience. Proved concretely with `uv build --wheel`: the built wheel contains `nodes/` and
`graphs/rag.py` but not `configs/` when `configs/` sits outside `src/` (`packages.find` only scans
`src/`+`alireza/`) — installing this package for real (non-editable) would `ModuleNotFoundError` on
`from configs.rag import MAX_RETRIES`. Reverted back to `src/configs/`. **Rule for future structure
calls:** anything *executed directly* (entry scripts) can live outside `src/` (`apps/`); anything
*imported by* code inside `src/` must live inside `src/` — the package must be self-contained for a
real (non-editable) install to work. Also hit a red-squiggle-only false alarm in VS Code/Pylance after
the back-and-forth moves (runtime resolution was fine both times, verified via `uv run python` — the
editor's own index was just stale; `Developer: Reload Window` / `Python: Restart Language Server`
clears it). Not a PyCharm issue — mentee confirmed PyCharm wasn't even open, this repo runs in VS Code.

**Phase B, Stage 3 — streaming — done, verified 2026-08-24.** `apps/rag.py` uses
`graph.stream(..., stream_mode="updates")` instead of `graph.invoke()` — prints each node's own
returned delta live as it fires (doc counts, rewritten query, final generation). Control flow
unchanged, just visibility.

**Phase B, Stage 4 — time-travel/replay — done, verified 2026-08-24.** `apps/rag.py` gained two REPL
commands: `history` (lists `graph.get_state_history(config)` snapshots, index 0 = most recent) and
`replay <index>` (`graph.invoke(None, config=snap.config)` — resumes from that exact checkpoint,
re-running only what's left per `snap.next`). Verified: replaying from the checkpoint right before
`generate` re-ran only `generate`, not `retrieve`/`grade_documents`. One real bug caught in the
mentee's own `except` clause — `except ValueError, IndexError:` (Python 2 syntax) — surprisingly this
*parses* on the project's actual interpreter (Python 3.14.6, confirmed via `ast.parse`: it becomes
`except (ValueError, IndexError):` under the hood), but `pyproject.toml` declares
`requires-python = ">=3.12"` and it's unconfirmed whether 3.12/3.13 accept the same comma form —
fixed to the unambiguous `except (ValueError, IndexError):` for portability. Worth remembering as a
"verify on the actual interpreter, don't assume from training data" case that cut the other way this
time (looked like a Python 2 bug, actually ran fine on 3.14 — still fixed for portability, not because
it was currently broken).

**Phase B, Stage 5 — LangSmith tracing per node — deliberately skipped, 2026-08-24, mentee's call.**
Asked the mentee to decide given the scope conflict noted above; their reasoning (confirmed correct):
unlike checkpointing/streaming/time-travel, LangSmith tracing doesn't teach a new graph-execution
pattern — it's env-var + run-metadata plumbing, squarely observability/MLOps, no distinct architecture
lesson at this stage. Staying deferred to the dedicated observability session, and naturally folds into
`P6`'s own Phase B ("Full LangSmith observability across all agents and subgraphs" per `ROADMAP.md`) —
not lost, just deferred to where it fits system-wide. **P2 Phase B is done as of this note: Stage 1
(corrective-RAG loop), Stage 2 (checkpointing), Stage 3 (streaming), Stage 4 (time-travel/replay) —
all done and verified. Next up: P2 Phase C** (`ROADMAP.md`: hybrid retrieval with web fallback, wrap
compiled graph as `CompiledSubAgent`, domain-specific retrieval skills, middleware guardrails/response
validation) — whenever the mentee is ready.

**Phase C, Stage 1 — hybrid retrieval (web fallback) — done, verified 2026-08-24.** `no_relevant_docs`
replaced by `web_search_fallback`: when the corrective-RAG loop exhausts retries with zero relevant
local docs, falls back to a live Tavily `web_search` call (same tool P1 uses) + a dedicated
`_generate_from_web_prompt` (`prompts/rag.py`) that explicitly labels the answer as web-sourced, not
from the local corpus. `route_after_grading`'s exhausted-retries branch now returns
`"web_search_fallback"` instead of `"no_relevant_docs"` — full replace, not a toggle (dead code avoided
on purpose, consistent with the `MAX_RETRIES` duplicate cleanup earlier this session; old behavior
still recoverable from git history if ever needed). Deliberately does **not** re-grade/filter web
results yet, and does **not** guard against out-of-scope/nonsensical questions (e.g. "what's my dad's
name?" — tested, the LLM currently answers honestly via prompt-level instruction rather than
hallucinating, but this isn't an architectural guarantee) — both explicitly deferred to Phase C Stage 4
(middleware guardrails/response validation), not solved here. One bug found+fixed in the mentee's own
code: `response.get("results, []")` — comma inside the string literal (should be
`response.get("results", [])`) — meant `.get()` always missed and returned `None`, so the fallback
silently never used real web results, always emitting the canned "couldn't find anything" message
regardless of what Tavily returned. Verified end-to-end (`who is the current president of iran` —
exhausted 2 retries, correctly fell to `web_search_fallback`, got a real cited web answer).
Considered and rejected `langgraph.prebuilt.ToolNode` for this: it's built for `messages`-based,
LLM-decided tool-calling (ReAct-style), and `RAGState` has no `messages` key — our control flow is
code-deterministic (always call `web_search` here, no LLM decision), so a plain function calling
`web_search.invoke(...)` directly is the right fit, same reasoning as the original raw-`StateGraph`-
over-DeepAgents choice for P2.

**`schemas/` renamed to `output_schemas/`, 2026-08-24 — real name collision, not a style choice.**
`chromadb` (a P2 dependency via `langchain-chroma`) ships its own `site-packages/schemas/` directory
(embedding-function JSON files — unrelated to this repo). Since that name exactly matched our own
top-level `src/schemas/` package, Python merged them as a PEP 420 namespace package the moment
resolution happened purely via the editable install (no `src` on `sys.path`) — and namespace packages
never execute `__init__.py`, so `from schemas import ResearchFindings` (top-level re-export style)
silently broke while `from schemas.rag import GradeDocument` (submodule-direct style) kept working by
luck, since the real file was still reachable through the merged namespace's contributed portion.
Confirmed for real: `apps/research.py` actually crashed (`ImportError: cannot import name
'ResearchFindings' from 'schemas' (unknown location)` — the `(unknown location)` was the tell: a
namespace package has no `__file__`). Fixed by renaming the package to `output_schemas` (checked
against `site-packages` first — no collision) and updating every importer (`nodes/rag.py`,
`subagents/research.py`, `apps/research.py`, `output_schemas/__init__.py` itself) plus
`uv sync --reinstall-package agent` to refresh the editable install's `top_level.txt`. Verified via
pure editable-install resolution (no `sys.path` tricks): `output_schemas` top-level import, `pytest`,
`apps/research.py` import, and `apps/rag.py` full run all pass. **Lesson for future top-level package
names in this repo:** before naming a new `src/` top-level directory, check it doesn't collide with an
already-installed dependency's own package/data directory in `site-packages` — generic single-word
names (`schemas`, `config`, `utils`, `types`) are the highest-risk ones; this collision existed
silently since P2 Phase A (whenever `chromadb` was first installed) and only surfaced now because it
took an import path that bypassed the `src`-on-path convenience trick.

**Phase C, Stage 2 — CompiledSubAgent wrap — done, verified 2026-08-24.** `subagents/rag.py`:
`rag_subagent` (a `CompiledSubAgent` dict) wraps the compiled P2 graph behind a `RunnableLambda`
adapter (`_run_rag_subagent`) that extracts the question from `state["messages"][-1]`, invokes the
existing graph with a fresh `uuid4()` thread_id per call (each delegation is a one-shot query — no
reason to persist a subagent-level thread across calls), and returns `{"messages": [AIMessage(...)]}`.
`RAGState`/`build_rag_graph()` themselves untouched — the `messages`-key requirement `CompiledSubAgent`
imposes (confirmed from `deepagents` source: raises `ValueError` without it) is purely an
integration-boundary concern, kept out of the graph's own task-shaped state. Considered and rejected
`ToolNode` (built for LLM-decided tool-calling on `messages` state; our control flow is
code-deterministic) and `RunnableGenerator` (only matters if the caller streams; `deepagents`' `task`
tool always calls `.invoke()`, never `.stream()`). Verified end-to-end: direct `runnable.invoke()`, and
a real `create_deep_agent(subagents=[rag_subagent])` call that delegates through the `task` tool and
gets a correct grounded answer back.

**Real finding, not a code bug: delegation reliability depends heavily on system-prompt structure.**
Reproduced empirically (3+ runs): a one-line system prompt ("delegate corpus questions to rag_subagent
via the task tool.") produces **flaky** orchestrator behavior — sometimes delegates cleanly, sometimes
wanders through its own built-in `glob`/`ls` filesystem tools first (which compete with `rag_subagent`
for the same kind of question) and occasionally gives up entirely ("no repository present..." — the
mentee hit this exact failure live). `rag_subagent` itself never failed when actually invoked — the
unreliability is entirely in the parent's tool-choice policy. Fix verified reliable (1 clean `task`
call, no wasted exploration): a structured system prompt via the existing `build_system_prompt()`
template (same one `prompts/research.py`'s `build_research_prompt()` already uses for P1), with an
explicit `tools` section stating the decision heuristic — not a rigid "always delegate" rule, but
*why*: `rag_subagent` for questions about corpus **content/meaning**, filesystem tools for a **specific
known file's** exact structure/content. **General principle, not model-strength-specific:** explicit
tool-choice structuring is standard production practice regardless of model capability — a stronger
model reduces failure *frequency* but doesn't remove the need (variance + wasted-tool-call cost exist
regardless of model tier).

**Follow-up strategic question, resolved:** for a large document where the goal is holistic
understanding (not a single targeted fact) and context-window/efficiency is a real constraint, the
right approach is neither pure RAG nor pure full-file-read alone — it's RAG-as-coarse-filter (find the
relevant section cheaply) followed by full-context reading of just that narrowed section
("retrieve then read"). Teaching an agent this decision policy generically (not hardcoded per-scenario)
is exactly what `ROADMAP.md`'s P5 "Skills library" is for — **out of scope for P2**, correctly deferred;
for now, a well-reasoned `tools` section in the system prompt (heuristic, not rigid rule) is the right
altitude of investment. Note: P2 Phase C's own Stage 3 bullet is "Skills for domain-specific retrieval
behavior" — worth clarifying with the mentee before starting it whether that's a lighter, RAG-scoped
customization or expected to reuse P5's actual `/skills/` DeepAgents mechanism; the Advanced Features
Map table and the P5 section text also disagree slightly on whether Skills is P5-A or P5-B (table says
A, P5's own Phase B bullet list has it) — minor drift, same class as the earlier HITL table/section
mismatch, not urgent to fix but note it if it causes confusion.

**Architecture already taught for this stage:** raw LangGraph `StateGraph` chosen over DeepAgents for
P2 because RAG's control flow (retrieve→grade→generate) is deterministic and bounded — it shouldn't
be LLM-decided the way P1's open-ended research delegation is. Vector store: `langchain-chroma` over
`langchain_community`'s FAISS wrapper — the latter emits a `DeprecationWarning` on import
("being sunset and no longer actively maintained"); Chroma is standalone, actively maintained, and
auto-persists via `chromadb.PersistentClient` (no manual `.persist()` needed). Embeddings:
`GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")`. Grading is N separate LLM calls
(one per retrieved doc, each via `lite_model.with_structured_output(GradeDocument)`), not one batched
call — trades latency/cost for per-doc grading precision; Phase B's corrective-RAG loop is the planned
place to revisit this trade-off.

**Bug found+fixed 2026-08-20 in the mentee's own `retrieval/index.py`:** `_embeddings()` called
`GoogleGenerativeAIEmbeddings(model_name=EMBEDDING_MODEL)` — the pydantic field is `model`, not
`model_name`; the unrecognized kwarg was silently dropped, then the required `model` field failed
validation. Root-caused by running the script directly (`uv run python -c "..."`) to surface the
traceback the mentee's PowerShell session wasn't showing. Fixed by the mentee to `model=EMBEDDING_MODEL`.
If embeddings-related `ValidationError: Field required` shows up again anywhere, check for this same
kwarg-name mistake first.

**Bug found+fixed 2026-08-20 in `src/graphs/rag.py`'s `generate` node:** `response.content` on
Gemini-3.x models can come back as a list of content blocks (text + a `signature` block for
thought-signing), not a plain string — printing it raw showed the Python list repr instead of clean
text. Fixed by routing through the project's own `utils.text.get_text(message)` helper (handles both
the plain-`str` and list-of-content-blocks cases) instead of reading `.content` directly. **Use
`get_text()` any time an `AIMessage.content` needs to be read as plain text, project-wide — this
isn't Gemini-specific, other providers/models can return structured content too.**

**Repo-wide bug found+fixed 2026-08-20, unrelated to P2 (mentee's own mid-session refactor of `prompts/`):**
the mentee split `prompts/builder.py` + `prompts/template.py` into a `prompts/template/` package
(`template.py` + `builder.py` inside it) and added `prompts/rag.py` for P2's node prompts, but
`prompts/__init__.py` still pointed at the old flat module paths (`prompts.builder`, `prompts.template`),
which broke every import of the `prompts` package repo-wide (`ModuleNotFoundError: No module named
'prompts.builder'`). The mentee fixed `prompts/__init__.py` themselves once it was pointed out — now
correctly imports from `prompts.template.builder` and `prompts.template.template`.

**Standing instruction from the mentee (2026-08-20):** going forward, reuse the system-prompt-template
builder (`prompts/template/builder.py`'s `build_system_prompt()` + `prompts/template/template.py`'s
`SYSTEM_PROMPT_TEMPLATE`/`DEFAULTS`) for new prompts **where it's actually applicable and fits** —
don't force it. It's built for a full agent-persona system prompt (identity/mission/style/policy
sections), which is what P1's `build_research_prompt()` uses it for. P2's `grade`/`generate` node
prompts in `prompts/rag.py` are small, single-purpose task instructions via `ChatPromptTemplate` —
not a persona — so they correctly do *not* use the builder; don't retrofit them just for consistency.
It becomes relevant again if/when a project phase wraps a graph as a persona-bearing agent (e.g. P2
Phase C's `CompiledSubAgent` wrapping, or any DeepAgents-based system prompt in P3+).

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
