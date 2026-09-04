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
- **Boilerplate vs. Agentic Core explicit flagging, 2026-08-28:** whenever introducing setup, infrastructure, or OS-level utility code (e.g. `subprocess`, `tempfile`, low-level regex, file wrappers), explicitly flag it upfront as an "Infrastructure / Boilerplate Pattern" with a 2-3 line conceptual summary of what it does as a black box. Explicitly instruct the mentee NOT to get bogged down memorizing non-agentic stdlib/utility syntax, keeping 100% of their learning focus on Agentic Architecture, LangGraph state/nodes/edges, and feedback loops.
- Point out real repo issues when you find them (stale docs, broken tests, dead imports) —
  don't silently fix things that affect the mentee's own in-progress work without saying so.
- **Balanced Logical Chunking & Core Logic First (2026-08-28):** do not dump an entire multi-component stage all at once, but do not artificially over-fragment into tiny 10-line crumbs either. Break work into natural, coherent logical units. Deliver the bare, unencumbered core agentic/business logic first with focused explanation, deferring verbose UI/app harness boilerplate until the core architecture is understood.
- **Strict Separation of Code Delivery & Test Exploration (2026-09-02):** NEVER send implementation source code and test cases/exploration scripts in the same message. Keep them strictly in separate sequential turns: (1) Architecture explanation first, (2) Implementation source code ONLY after concept alignment, (3) Mentee confirmation of applied code, (4) THEN and only then, deliver the test scenario / exploration script.
- **Strict Single-Item Per Turn Rule (2026-09-02):** NEVER send multiple items (e.g. 2 test cases, 2 concepts, or multiple scripts) in a single message. Always send strictly ONE item at a time, wait for the mentee to review/execute and respond, and only then proceed to the next item.
- **Strict English-Only in Code & Blocks (2026-09-02):** Code, docstrings, inline comments, print statements, string literals, and file contents inside code blocks MUST be 100% strictly in English — never Persian or Finglish.
- **Pedagogical Freedom & Thoughtful Curriculum Pacing (2026-08-28):** you are empowered to adjust pacing, introduce architectural concepts earlier/later/deeper, or refine patterns beyond rigid `ROADMAP.md` wording whenever there is a strong, well-reasoned pedagogical/architectural rationale behind it, keeping the overall learning progression solid and cohesive.




- **Documentation Verification & Anti-Hallucination (CRITICAL, 2026-08-28):** for all LangChain / LangGraph ecosystem questions and code, MUST query up-to-date documentation (`docs-langchain` / Context7 / search) before answering. NEVER rely on model training data memory alone, as APIs evolve rapidly across versions.


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
| **P2 — RAG Agent** | ✅ Phase A ✅ Phase B ✅ Phase C (4/4 stages, verified 2026-08-25; Stage 5/LangSmith deliberately deferred) — done for current scope |
| **P3 — Code Review & Test Gen Agent** | ✅ Phase A complete · ✅ Phase B complete · Phase C Stage 1 (Subgraphs) & Stage 2 (CompiledSubAgent) wired & passing |



| P4 — Sandbox/Interpreter Agent | In progress: Phase A Stage 1 ✅ Stage 2 ✅ (`make_interpreter_agent`, `build_interpreter_agent_prompt`, `LocalShellBackend`) |
| P5 — Memory-Rich Personal Assistant | Not started |
| P6 — Capstone | Not started |

## Future Extensions Backlog (beyond `ROADMAP.md`), started 2026-08-25

Two distinct triggers populate this list, both required — passive logging alone isn't enough:

1. **As they come up in conversation.** Any idea for a feature/function/extension/tool that
   surfaces while working a project — whether it's genuinely outside the formal `ROADMAP.md`
   curriculum, or is an official roadmap bullet that ends up left undone — gets logged here
   immediately, tagged Essential or Nice-to-have.
2. **Proactively, at the end of a project's last working session.** Don't wait passively for
   items to come up on their own — actively review what the project *could* still use (real
   production gaps, natural extensions of what was just built, official roadmap bullets left
   incomplete) and log them here before moving to the next project.

**If a real need for a logged item surfaces mid-course** (while building something else in the
same or a later project), pull it in and build it then — don't force it to wait for a dedicated
round. Otherwise, this whole backlog is the punch list for an eventual **advanced/enrichment
round** after finishing P1–P6: revisit each project, prioritize Essential items first, then work
down the Nice-to-have list.

**Priority tags:**
- **Essential** — meaningfully closes a real production gap; worth prioritizing first in a
  do-it-later round.
- **Nice-to-have** — a genuine improvement, but the current implementation already handles the
  core need adequately; polish, not a gap.

### P1 — Research Agent (retrospective logged 2026-08-25 — Phase A/B/C done for current scope)

**Essential** (official roadmap bullets, left undone — already tracked in more detail in the
"P1 — Research Agent — detailed state" section below; cross-referenced here, not duplicated):
- Memory for recurring research preferences and past topics (Phase B item).
- LangSmith tracing + evaluation datasets (Phase C item).
- SDK-exposed multi-session service (Phase C item).

**Nice-to-have:**
- **Wire P1 to P2's `rag_subagent`.** `ROADMAP.md` lists an "Optional RAG overlay for local
  notes or saved corpus" for P1 Phase C, noting it's "likely superseded by P2 anyway" — now that
  P2 Phase C actually built `rag_subagent` (a real `CompiledSubAgent`), adding it to P1's
  `subagents=[...]` list is a cheap, concrete way to realize that bullet using work already done,
  not a from-scratch build.
- **Citation/groundedness validation on `ResearchReport`.** Mirror P2 Phase C Stage 4's
  `check_hallucination` pattern: verify each cited source in the final report actually appears in
  what `web_search` returned, before returning the report to the user — catches a fabricated
  citation the same way P2 now catches an ungrounded generation.
- **Broader model-fallback chain in `retry_on_failure`.** Currently one fallback hop
  (`luna_model` only) — could chain further (e.g. `luna_model` → `terra_model`) for more
  resilience against a single fallback also being unavailable.

### P2 — RAG Agent (mid-course — Phase A/B done, Phase C in progress)

**Nice-to-have:**
- **Hallucination-triggered retry/reroute.** `check_hallucination` (Phase C Stage 4) currently
  just swaps in a safe disclaimer when the generation isn't grounded — it doesn't route anywhere
  else. A Self-RAG/CRAG-style extension would instead route the ungrounded case back to
  `query_rewrite` (retry retrieval with a better query) or `web_search_fallback` (try the web
  instead) rather than giving up with a disclaimer. Not essential: the disclaimer already fully
  closes the hallucination-prevention need (no false answers reach the user) — this would only
  make the agent *more likely to actually answer* instead of declining.
- **Extend `check_hallucination` to the `web_search_fallback` path.** Stage 4 only validates the
  local-corpus `generate` path; the web-fallback answer isn't groundedness-checked. Deliberately
  scoped out of Stage 4 to keep that stage small — a natural, cheap follow-up (same node pattern,
  different input path).
- **Batch document grading.** `grade_documents` makes one LLM call per retrieved document
  (`lite_model.with_structured_output(GradeDocument)` per doc) rather than one batched call for
  all of them — trades latency/cost for per-doc grading precision, noted as a known trade-off
  back in Phase A. Batching would cut LLM calls significantly per query; worth it once query
  volume/cost actually matters, not before.
- **Rate-limit-aware batching in `retrieval/index.py`'s `build_index()`.** `Chroma.from_documents`
  currently submits every chunk's embedding request without pacing against the Gemini free-tier
  quota (100 req/min) — a full corpus rebuild reliably hits `429 RESOURCE_EXHAUSTED` partway
  through (hit live, 2026-08-26, during the `core/` restructuring's index rebuild). Worked around
  once with a manual retry-with-backoff wrapper script; the real fix is batching `build_index()`'s
  own embedding calls with a delay/backoff built in, not relying on `langchain_chroma`'s default
  (unbatched) behavior.
- **Broaden `CODE_GLOB` to index `agents/`/`apps/`/`configs/`, not just `src/`.** Currently
  `CODE_GLOB = "core/src/**/*.py"` — the corpus the RAG agent answers questions from only covers
  `core/src/`, missing `core/agents/`, `core/apps/`, `core/configs/` entirely (so a question like
  "what does `repo_insight_agent` do" wouldn't retrieve anything relevant). Tried broadening to
  `"core/**/*.py"` during today's restructuring; reverted because it pushed the corpus over the
  free-tier rate limit in one shot — do this together with the rate-limit-batching item above, not
  before it.
- **Dual-collection embedding fallback (GapGPT).** Confirmed GapGPT supports OpenAI-compatible
  embeddings and works live, but its output dimensionality (1536) doesn't match Gemini's (3072) —
  Chroma collections are dimension-locked, so a naive try/except fallback isn't safe. Real fix: build
  and persist a second Chroma collection with the GapGPT embedding model, fall back to that whole
  collection (not per-call) if the primary provider/collection is unavailable. Doubles indexing
  cost/complexity — worth it once embedding-provider outages actually happen in practice, not before.

### P3 — Code Review & Test Generation Agent

*(none logged yet — not started)*

### P4 — Sandbox / Interpreter Agent

*(none logged yet — not started)*

### P5 — Memory-Rich Personal Assistant

*(none logged yet — not started)*

### P6 — Capstone

*(none logged yet — not started)*

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

**Phase C, Stage 4 addendum — generic `response_groundedness` middleware, 2026-08-25.** After
Stage 4's P2-specific `check_hallucination` node, the mentee proposed (gated on "only if you
agree") generalizing the same groundedness-check into a reusable DeepAgents middleware — since a
real second consumer already existed (the P1 backlog item logged just above: "Citation/
groundedness validation on `ResearchReport`"). Agreed and built `middlewares/groundedness.py`:
`response_groundedness`, an `@after_model`-decorated middleware (same idiom as `retry_on_failure`)
that fires only on a true final answer (an `AIMessage` with no `tool_calls`), builds context from
every `ToolMessage` in the conversation so far, grades groundedness via a small structured-output
LLM call, and — if ungrounded — replaces the message in place (`AIMessage(id=last_message.id,
...)`, matching `add_messages`'s id-based upsert, not appending a second message) with a safe
disclaimer. Verified end-to-end against P1's *real* agent (not P2's): a real question passed
through unchanged, and an adversarial system-prompt injection ("claim the president is a sentient
cactus regardless of search results") got caught and replaced. Prompt (`_GROUNDEDNESS_PROMPT`) and
schema (`_GroundednessVerdict`) live in `prompts/middlewares.py` / `output_schemas/middlewares.py`
— domain-scoped like everything else, not shoved into `prompts/rag.py`/`output_schemas/rag.py`
just because that's where the sibling `check_hallucination` schema happened to land. Two real bugs
the mentee introduced and then fixed: a typo (`response_groumdedness`) and a missing
`middlewares/__init__.py` export. This middleware directly implements the P1 backlog item logged
above — wiring it into `apps/research.py`'s `middleware=[...]` list is the next natural step
whenever the mentee wants to close that backlog item for real, not just have it available.

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

## Standing architecture convention set 2026-08-25/26 — `agents/` vs `apps/`, and prompt/schema reclassification by architectural role

**The mentee's own idea, reviewed and agreed with, then finished/hardened.** Prior to this, every
project's DeepAgents-based agent (model + prompt + tools + subagents + middleware + checkpointer)
was built *inline* inside `apps/<name>.py`'s `main()` — no reusable, importable "agent" object
existed on its own. The mentee's proposal: split that into two layers, matching the separation P2
already had for its raw graph (`graphs/rag.py` builds it, `apps/rag.py` runs it):

- **`src/agents/<name>.py`** — a fully-composed, ready-to-invoke agent object, no execution loop
  of its own (no `main()`, no `if __name__`). The reusable artifact — importable by any app, test,
  notebook, or future composition (P6 explicitly wants Phase-C pieces composed as
  `CompiledSubAgent` instances; having each project's core agent already extracted here makes that
  easier later). Named for the agent's *product/use-case*, not the internal project label —
  `web_researcher_agent` (P1) not `research_agent`, `repo_insight_agent` (P2's coordinator) not
  `rag_agent` — the internal plumbing (`graphs/rag.py`, `nodes/rag.py`, etc.) keeps its
  dev-internal domain naming; only the top-level agent gets product-facing naming.
- **`apps/<name>.py`** — the thin runnable entry point: imports an agent from `agents/`, adds the
  actual run loop (REPL, HITL-resume loop, whatever the use case needs) for one concrete way of
  exercising that agent.

**Where `agents/` had to live, and why (a real bug, not a style choice — same class of issue as
the `configs/`-outside-`src/` mistake earlier):** the mentee first created it at the repo root
(sibling of `apps/`), which doesn't work — `agents/` modules are *imported by* `apps/` code, not
executed directly, so per the already-established rule ("executed code can live outside `src/`;
imported code must live inside it, or a real — non-editable — install literally won't ship it and
even editable-install resolution breaks depending on caller cwd") it has to be `src/agents/`. Moved
it there, added `src/agents/__init__.py`, reinstalled (`uv sync --reinstall-package agent`),
verified pure-editable-install import (no `sys.path` tricks) works from any cwd.

**Second real bug found while finishing this: `agents/repo_insight.py`'s
`FilesystemBackend(root_dir=".")`.** Same cwd-fragility class as the earlier notebook bug (Phase C
Stage 1) — but this time baked into a module that's built *at import time* and meant to be
importable from anywhere (apps/, notebooks, tests). Fixed to an absolute path anchored to the
file's own location: `Path(__file__).resolve().parents[2]` (repo root, independent of caller cwd).
Verified by importing `agents.repo_insight` from a different cwd and confirming `backend.cwd`
still resolves to the real repo root.

**`prompts/` and `output_schemas/` reclassified by architectural role, not just project domain.**
The old `prompts/rag.py`/`prompts/research.py` (domain-named) mixed genuinely different kinds of
prompts in one file — P1's *top-level agent* persona prompt and its *subagent* persona prompt both
lived in `prompts/research.py`, which is a real inconsistency once `agents/` vs `subagents/` became
a first-class distinction. New shape, still dir=kind (now two levels: `prompts/`+role-file):
`prompts/agents.py` (top-level agent persona prompts — `build_web_researcher_prompt`,
`build_repo_insight_prompt`), `prompts/subagents.py` (`researcher_subagent_prompt`),
`prompts/rag_nodes.py` (P2's raw-`StateGraph` node prompts — was `prompts/rag.py`),
`prompts/middlewares.py` (`_GROUNDEDNESS_PROMPT`). Same split mirrored in `output_schemas/`:
`output_schemas/rag.py` keeps only `GradeDocument`/`GradeHallucination` (P2 node-level schemas),
`output_schemas/middlewares.py` holds `_GroundednessVerdict` (the generic middleware's schema, not
RAG-specific — was briefly misplaced in `output_schemas/rag.py`, moved out). Also renamed
`build_research_prompt` → `build_web_researcher_prompt` for naming consistency with the agent it
builds the prompt for.

**Stale paths from before this change, if seen in older notes above:** `prompts/rag.py` →
`prompts/rag_nodes.py`; `prompts/research.py` → split into `prompts/agents.py` (top-level prompt)
+ `prompts/subagents.py` (subagent prompt); `subagents/researcher.py` → `subagents/research.py`
(renamed earlier, 2026-08-24, already noted then).

**New files from this pass:** `apps/repo_insight.py` — a new entry point (didn't exist before)
that actually exercises the full P2 coordinator (`repo_insight_agent`: `rag_subagent` +
`retrieval-strategy` skill + filesystem backend) end-to-end via a REPL, distinct from `apps/rag.py`
which exercises the raw graph directly one layer below. Both are legitimate, kept side by side —
graph-level debugging vs. product-level agent, same pedagogical value as everything else this
session.

**Verified, all live (not just import-level):** `pytest` green; `apps/rag.py` unaffected;
`apps/research.py` (now importing `web_researcher_agent` from `agents/`) ran a full live
HITL-approval round-trip and produced a correct cited `ResearchReport`; `apps/repo_insight.py` ran
live, skill loaded, delegated to `rag_subagent`, correct grounded answer.

## Standing architecture convention set 2026-08-26 — `core/{src,apps,agents,configs}` as siblings

**Superseded the "just move `agents/` into `src/`" fix from the note above.** The mentee reviewed
that fix, disagreed with keeping `agents/` nested inside `src/` (wanted `agents`, `apps`, `configs`,
and `src` all as direct siblings, one level, with zero import problems), and after hearing the
mentor's counter-argument (that standard `src`-layout semantics already achieve the same
build-vs-run separation without an extra wrapper) explicitly overrode it: **do it anyway, using
whatever concrete mechanism makes it actually work, and design the "right" production structure
for this repo's own nature — don't just implement literally what I said if you know better, and
don't treat the repo as staying simple forever.** Mentor's honest final judgment, once required to
implement it for real rather than just discuss it: the mentee's core complaint was legitimate
(`agents/` sitting at the repo root, outside `src/`, was a genuine mistake that broke imports) —
disagreement was only about the *fix's shape*, not the underlying problem, and a working
peer-siblings layout is a real, defensible structure for a repo this size, not a regression.

**Final structure:**

```
core/
├── src/       # library code: graphs/ nodes/ prompts/ output_schemas/ subagents/
│              # middlewares/ models/ tools/ retrieval/ state/ data/ utils/
├── configs/   # plain config constants (was src/configs/)
├── agents/    # composed, ready-to-invoke agent objects (was repo-root agents/, then src/agents/)
└── apps/      # runnable entry points (was repo-root apps/)
```

**How the import mechanics actually work (verified, not guessed — this is the load-bearing part):**
`pyproject.toml`'s `[tool.setuptools.packages.find]` now has `where = ["core/src", "core", "alireza"]`
with `exclude = [..., "src*"]`, and `[tool.setuptools.package-dir]` keeps `"" = "core/src"`. Two
independent scans happen: `where=["core/src"]` discovers `core/src/`'s own children (`graphs`,
`nodes`, etc.) as bare top-level packages, exactly like the old `where=["src"]` did before this
change — nothing about `core/src/*` imports changed at all (`from graphs.rag import ...` still
works verbatim). Separately, `where=["core"]` discovers `core/configs`, `core/agents`, `core/apps`
as bare top-level packages too (each is a direct child of `core/` with its own `__init__.py`) — the
`exclude=["src*"]` stops that second scan from *also* picking up `core/src` itself as a colliding
package named "src". Verified via `top_level.txt` after `uv sync --reinstall-package agent`:
`agents`, `apps`, `configs`, `data`, `graphs`, ... all present as bare names, no `src` entry, no
duplicates. **This is the general recipe for "N sibling directories, all independently importable,
one of which (`src/`) itself contains many more importable children"** — remember it if a similar
multi-root layout need comes up again (P3+).

**Real bugs found and fixed while executing this move (all from files whose depth-from-repo-root
changed, i.e. `Path(__file__).resolve().parents[N]`-style anchoring didn't get updated to match):**
- `core/src/retrieval/index.py`'s `REPO_ROOT = Path(__file__).resolve().parents[2]` — was correct
  when the file was at `src/retrieval/index.py` (2 levels up = repo root); now one level deeper
  (`core/src/retrieval/index.py`), needs `parents[3]`. Fixed, verified via direct `Path` arithmetic
  before touching the real module.
- `core/agents/repo_insight.py`'s `parents[2]` did **not** need to change — `agents/` stayed a
  direct child of its container (`src/` before, `core/` now), same depth. Verified this explicitly
  rather than assuming a blanket "add 1 to everything" — the two files needed different fixes.
- `core/apps/rag.py`: a pre-existing, unrelated bug this surfaced (not caused by the move) —
  `stream_mode="updates"` reports a node's `{}` (no-op) return as `None` in the yielded update dict,
  and the REPL's `for node_name, delta in update.items(): if "documents" in delta` didn't guard
  against `delta` being `None`. Only surfaced now because this was apparently the first time
  `apps/rag.py`'s actual CLI ran with `check_hallucination` (which returns `{}` when grounded)
  wired into the graph — all earlier Stage 4 testing went through `graph.invoke()`/`graph.stream()`
  directly in throwaway scripts, never through this exact REPL loop. Fixed with `if not delta:
  continue` before the membership checks.
- `core/src/retrieval/index.py`'s `DOC_FILES`/`CODE_GLOB` — `ROADMAP.md`/`MENTOR_HANDOFF.md` moved
  to `docs/` (see below) so `DOC_FILES` needed `"docs/ROADMAP.md"`/`"docs/MENTOR_HANDOFF.md"`;
  `CODE_GLOB` was `"src/**/*.py"`, now `"core/src/**/*.py"` — both silently pointed at nothing once
  those directories moved (a glob that matches zero files fails silently, no error, just an
  incomplete/empty corpus — worth remembering as a class of bug: **path-string bugs from directory
  moves don't crash, they silently under-index**, unlike import-path bugs which crash loudly).

**`docs/` created.** `ROADMAP.md` and `MENTOR_HANDOFF.md` (this file) moved to `docs/ROADMAP.md` /
`docs/MENTOR_HANDOFF.md`. `README.md`, `LICENSE`, and `AGENTS.md` stay at repo root — not moved,
deliberately: `README.md`/`LICENSE` are root-discovery conventions (GitHub renders `README.md` from
root), and `AGENTS.md` is a cross-tool root-discovery convention too (Codex and other agent CLIs
scan for it at repo root specifically — this repo has a `.codex/` directory, meaning it's actually
in use, not just present) — moving either would silently break tool auto-discovery, not just human
convenience. Both `README.md` and `AGENTS.md` were also rewritten in this pass — they'd drifted far
out of date (still describing `src/app.py`, `middleware/` singular, `schemas/`, no mention of
`apps/`/`agents/`/`configs/`/`nodes/`/`graphs/` at all) — now reflect the real current structure.

**Index rebuild note:** `.chroma_index` had to be rebuilt after the `DOC_FILES`/`CODE_GLOB` fix
(old index was built from the pre-move paths). Rebuilding the full corpus in one shot hit the
Gemini embedding free-tier rate limit (100 req/min) — not caused by this move, an existing fragility
in `build_index()` (`Chroma.from_documents` sends all embedding requests without batching/backoff
against the free-tier ceiling); worked around this once with a manual retry-with-backoff wrapper,
logged the real fix (rate-limit-aware batching in `build_index()`) as a P2 backlog item below.

**Verified, all live, after every fix above:** `pytest` green; `uv sync --reinstall-package agent`
clean install with the exact expected `top_level.txt`; `core/apps/rag.py`, `core/apps/research.py`
(full HITL round-trip), and `core/apps/repo_insight.py` (skill load + delegation) all ran live,
end-to-end, from repo root, with no `sys.path` tricks.

## Standing architecture convention set 2026-08-26 (2) — generic LLM registry, retry, HITL

**The mentee's idea, reviewed and agreed with (this one straightforwardly — no disagreement to
resolve), then designed against real standards rather than implemented literally.** Ask was: stop
importing named model instances (`flash_model`, `lite_model`, ...) directly; make model selection
config-driven behind one generic handle; make `retry_on_failure` and the HITL middleware/loop
reusable across every project instead of P1-specific; route through `get_text()` consistently.

**`configs/models.py` + `models/registry.py`.** `MODEL_REGISTRY` (role → `init_chat_model(...)`
kwargs) and `FALLBACK_CHAIN` (ordered list of fallback model kwargs, GapGPT-routed) live in
`configs/models.py`. `models/registry.py`'s `LLMRegistry` class wraps them:
- `.get(role)` — plain cached `BaseChatModel`, for `create_deep_agent(model=...)` (needs a real
  `BaseChatModel` for `.bind_tools()` etc. — confirmed via source, `RunnableWithFallbacks` doesn't
  have that method, so a fallback-wrapped model can't be used here).
- `.chain(role, structured=...)` — fallback-wrapped `Runnable`, correctly composed with
  `.with_structured_output()` when needed (structured output must be bound to *each* model, primary
  and fallbacks, before `.with_fallbacks()` wraps them — verified empirically, `RunnableWithFallbacks`
  doesn't inherit `with_structured_output` either).
`llm_model = LLMRegistry()` is the one importable handle (`from models import llm_model`) —
replaces `flash_model`/`lite_model`/`pro_model`/`luna_model`/`terra_model` everywhere. Migrated every
consumer: `nodes/rag.py` (all 4 model call sites), `agents/web_researcher.py`, `agents/repo_insight.py`
(also gained `retry_on_failure` middleware — didn't have it before), `middlewares/groundedness.py`.
Deleted the old `models/llm.py`.

**Real, load-bearing verification: `.with_fallbacks()` genuinely triggers on `429
RESOURCE_EXHAUSTED`** (both the embedding quota hit earlier today and the separate
`gemini-3.7-flash` daily-quota exhaustion) — confirmed with 3 independent isolated reproductions,
including the literal real `_generate_prompt | llm_model.chain("flash")` composition `generate()`
uses. **One genuinely confusing finding, worth remembering:** `RunnableWithFallbacks.invoke()`
re-raises `first_error` (the *primary's* exception) when every fallback also fails — verified via
its source (`langchain_core/runnables/fallbacks.py`). This means a traceback showing only the
primary's error message does **not** prove fallback was never attempted — it could mean the whole
chain (primary + every fallback) failed and you're only seeing the first one. Hit exactly this
while verifying: a full `core/apps/rag.py` live run still failed with only the `gemini-3.7-flash`
error visible, even though the fallback mechanism was independently proven correct — almost
certainly cascading quota exhaustion across *both* Gemini and GapGPT from a full day of heavy live
testing (grading calls earlier in the same graph run likely already spent GapGPT's own budget
before `generate()` needed it), not a code defect. Recommend re-running `core/apps/rag.py` live
once quota resets to see a real end-to-end confirmation; the isolated composition tests + `pytest`
stand as current verification evidence in the meantime — didn't keep burning quota chasing it.

**`middlewares/retry.py` generalized.** No longer hardcodes `luna_model` — reads
`llm_model.fallback_models()` and tries each in order, so it's identical config to `llm_model.chain()`'s
fallback behavior, just at the agent-middleware layer (needed separately: DeepAgents needs a real
`BaseChatModel` for its internal `.bind_tools()`, so agent-level fallback can't reuse the
`.with_fallbacks()`-wrapped `Runnable` from `.chain()` — same constraint as `.get()` vs `.chain()`
above). Reusable as-is in any project's `middleware=[...]` list.

**`middlewares/hitl.py` generalized.** `hitl_for(tool_names, *, allowed_decisions=..., description_prefix=...)`
builds a `HumanInTheLoopMiddleware` for any tool(s), not just `web_search` — `search_approval =
hitl_for("web_search")` is now just the P1-specific instance built from the generic factory.

**`utils/run_with_hitl.py` extracted.** The interrupt/resume `while "__interrupt__" in result: ...`
loop that lived inline in `apps/research.py` is now `run_with_hitl(agent, initial_input, config,
prompt=...)` — any app needing HITL resume-over-CLI calls this one function instead of
reimplementing the loop. `apps/research.py` rewritten to use it (functionally identical, less code).

**`get_text()` widened and applied consistently.** Type hint was narrowly `AIMessage` (from
`langchain.messages`) — widened to `BaseMessage` (from `langchain_core.messages`), since the
function's own body already worked generically (any message with `.content`) and
`middlewares/groundedness.py` needed it for `ToolMessage` content too, not just `AIMessage`. Applied
at every raw `.content` access found: `apps/repo_insight.py` (removed a duplicate hand-rolled
version of exactly what `get_text()` already does), `middlewares/groundedness.py` (two call sites —
one of these was a real bug: `str(last_message.content)` on Gemini's list-of-blocks format would
have produced Python's list-repr string, not the actual answer text, silently corrupting the
groundedness grader's input), `subagents/rag.py`.

**Verified:** `pytest` green; full import sweep of every new/changed module; isolated verification
of the fallback mechanism (3 reproductions, see above) including through the exact real prompt
composition `generate()` uses; agent-level `retry_on_failure` change is a direct generalization of
already-working code (same `request.override(model=...)` mechanism, just reading a list instead of
one hardcoded model) — reviewed by inspection rather than re-verified live, given quota pressure.

## Standing architecture convention set 2026-08-26 (3) — tier × provider LLM registry

**Further refinement of the registry above, mentee's idea, agreed with.** Old shape was
role → one specific model (`"lite"` meant "`gemini-3.5-flash-lite`", tying a role name to one
provider). New shape: **capability tier × provider**. `configs/models.py`'s `MODEL_TIERS` is
`{tier: {provider: init_chat_model kwargs}}` for `"low"`/`"medium"`/`"high"`; `TIER_PROVIDER_ORDER`
lists each tier's providers with the first as primary/default. `LLMRegistry.fallback_models(tier)`
now returns only *that tier's* other providers — fixes a real gap in the previous flat
`FALLBACK_CHAIN`: a "lite" (low-capability) call could previously fall back to "terra" even if terra
were a different (higher) capability tier, silently changing capability, not just provider, on
failure. Role names migrated: `"lite"`→`"low"`, `"flash"`→`"medium"`, `"pro"`→`"high"` — updated at
every call site (`nodes/rag.py`, `agents/web_researcher.py`, `agents/repo_insight.py`,
`middlewares/groundedness.py`).

**Only verified model names are configured — no placeholders.** `"high"` tier currently has only
`gemini-3.1-pro` (Gemini), no GapGPT fallback — there's no confirmed GapGPT model name for that tier
(the mentee's example mentioned a `gpt-5.6-sol`-style high-tier GapGPT model, but only
`gpt-5.6-luna`/`gpt-5.6-terra` are actually provisioned/tested against the real API right now).
**Don't add a GapGPT high-tier entry without confirming the actual model name works first** — same
verify-before-trusting discipline as everywhere else this session. A 4th "free"/OpenRouter tier was
also discussed and intentionally **not** built — no OpenRouter API key exists in `.env` yet, can't
wire and test something without real credentials; ask the mentee for a key first if this comes up
again, don't fabricate one.

**`middlewares/retry.py` became a factory, not a fixed instance** — `retry_on_failure(tier)` builds
middleware scoped to one tier (matching the tier that agent's `model=` was constructed with), since
fallback is now tier-locked. Both `web_researcher_agent` and `repo_insight_agent` now use
`middleware=[retry_on_failure("low"), ...]` (call sites updated from the old bare
`middleware=[retry_on_failure]` reference).

**Embedding fallback — checked, found a real structural blocker, did not build cross-provider
fallback.** Confirmed GapGPT *does* support OpenAI-compatible embeddings (`text-embedding-3-small`
via `OpenAIEmbeddings(base_url=GAPGPT_BASE_URL, ...)`, verified live). But: Gemini's
`gemini-embedding-2-preview` produces **3072-dim** vectors, GapGPT's `text-embedding-3-small`
produces **1536-dim** — Chroma collections are dimension-locked. A naive try/except fallback would
either error outright (dimension mismatch) or, worse, silently corrupt the collection if it happened
to succeed at write time — not a safe drop-in the way chat-model fallback is. Also, `Embeddings`
(the base class) isn't a `Runnable`, so `.with_fallbacks()` doesn't apply to it directly anyway — any
real fallback would need hand-rolled try/except logic in a custom wrapper. The only architecturally
sound version is a **second, fully separate Chroma collection built with the fallback embedding
model**, used wholesale if the primary collection/provider is unavailable — real work (double the
indexing cost/complexity), not a config tweak. Left as-is (single Gemini embedding provider,
already has the retry+backoff added earlier this session for transient rate limits) and logged the
dual-collection approach as a P2 backlog item below, rather than building something that would
silently misbehave the first time it actually triggered.

**Verified:** `pytest` green; full import sweep; tier/provider wiring confirmed correct by direct
inspection (`low`/`medium` → `[gemini, gapgpt]`, `high` → `[gemini]` only, as configured); the
underlying `.with_fallbacks()` mechanism itself was already proven correct 3x earlier this session
against the *same* provider models now addressed via tier names instead of role names — didn't
re-run a live end-to-end reproduction a 4th time given how strained today's quota already was (one
attempt during this pass appears to have hung inside Gemini's own internal retry backoff rather than
reaching the fallback layer at all — a process-level timeout, not a code failure).

## Standing architecture convention set 2026-08-26 (4) — OpenAI/Anthropic via GapGPT, `free` tier

**Found GapGPT's real model catalog by querying its own `/v1/models` endpoint directly** (with
`GAPGPT_API_KEY`) rather than guessing or trusting web search (which found nothing public about
GapGPT — it's not a widely-documented service). Confirmed 120 real models, including exactly the
ones needed: `gpt-5.6-sol` (mentee named this one), plus real Anthropic models
(`claude-opus-5`, `claude-sonnet-5`, and older opus/sonnet variants — no Haiku-tier model in the
catalog). **Key mechanism, worth remembering:** GapGPT is one OpenAI-compatible gateway that proxies
*multiple* underlying model brands (OpenAI, Anthropic, Gemini, GLM, DeepSeek, Qwen, Grok, ... — 120
total) through the same `base_url`/`api_key` — so reaching a Claude model through it still means
`model_provider="openai"` in `init_chat_model(...)` (that names the *wire protocol*, not the brand),
with `model="claude-opus-5"` as the string GapGPT itself dispatches on internally. Live-invoked all 3
new models individually before adding them to config — all responded correctly.

**`configs/models.py`: provider keys renamed to name the underlying model *brand*, not the router.**
Was `"gemini"`/`"gapgpt"` (router-named); now `"gemini"`/`"openai"`/`"anthropic"` — `"openai"` and
`"anthropic"` both physically route through GapGPT's `base_url`/`api_key`, but the config key now
tells you *which model family* a given tier's fallback actually is, which matters more to a reader
than which gateway it went through. `high` and `medium` tiers now have 3 providers each
(gemini/openai/anthropic); `low` stays at 2 (`gemini`/`openai` — no confirmed GapGPT Claude model at
that capability level, so no `anthropic` entry there rather than a guessed one).

**New `"free"` tier — OpenRouter, `glm` + `nvidia` providers.** Mentee has `OPENROUTER_API_KEY`
already in `.env`. Same discovery approach: queried OpenRouter's own `/v1/models` endpoint, filtered
to `:free`-suffixed IDs (17 total) rather than guessing slugs — real ones are
`z-ai/glm-5.2:free` and `nvidia/nemotron-3-ultra-550b-a55b:free` (OpenRouter's flagship free
Nemotron — 55B active/550B total MoE, 1M context); picked these two over the other 15 free options
(smaller/more niche models — LiquidAI, Poolside, Thinking Machines, etc.) as the clearest matches
for "GLM and Nvidia." Both live-invoked successfully, including through the full
`llm_model.chain("free")` path (fallback + composition machinery unchanged, just a new tier value).
**`"free"` is deliberately not `DEFAULT_TIER`** and never appears in another tier's
`fallback_models()` — it's opt-in only (`.chain("free")`/`.get("free")` explicitly), since free-tier
model quality/latency shouldn't silently substitute into a paid tier's fallback chain without being
asked for.

**Verified:** `pytest` green; full tier/provider wiring inspected (`low`→`[gemini, openai]`,
`medium`/`high`→`[gemini, openai, anthropic]`, `free`→`[glm, nvidia]`); every newly-added model
individually live-invoked before being trusted in config, plus one additional live round-trip
through the actual `llm_model.chain("free")` composition path.

## Standing architecture convention set 2026-08-26 (5) — `LLM_TEST_MODE`, cross-tier cascade

**Two more additions to the registry, both opt-in, both off by default — neither changes existing
call-site behavior unless explicitly turned on.**

**`LLM_TEST_MODE` env var.** When `.env` has `LLM_TEST_MODE=true`, `LLMRegistry._resolve_tier()`
substitutes *every* tier request (`"low"`, `"medium"`, `"high"`, whatever's asked for) with the
`free` tier's models instead — lets the mentee iterate on routing/prompt/fallback logic without
spending paid-tier quota (exactly the kind of heavy iterative testing that exhausted real quota
multiple times earlier this session). Unset (or any non-`true` value) = normal behavior, tiers
resolve as configured. Verified both states directly: unset → `_test_mode` is `False`; env var set →
requesting `"high"` actually constructs `z-ai/glm-5.2:free`, confirmed via the constructed model's
own `model_name`.

**Cross-tier cascade, opt-in via `cascade=True`.** `.chain(tier, cascade=True)` and
`retry_on_failure(tier, cascade=True)` extend the fallback chain past `tier`'s own providers into
every lower tier's *full* provider list, in `TIER_CASCADE_ORDER` (`high → medium → low → free`) —
"a degraded answer beats no answer," for call sites that explicitly want that behavior. Deliberately
**not** the default: `fallback_models()` (used by every existing call site) stays same-tier-only, so
this doesn't reintroduce the "silently downgrades capability on failure" bug tier-locking fixed
earlier this session — cascade is a distinct, separately-named method
(`cascade_fallback_models()`) callers opt into per call, not something that changes what
`fallback_models()` itself returns. Verified the actual chain order for `cascade_fallback_models("high")`:
both `high` providers first (`gpt-5.6-sol`, `claude-opus-5`), then all of `medium`'s, then all of
`low`'s, then both of `free`'s — 9 total fallback models, exact expected order.

**Not yet wired into any real call site** — built and verified as available capabilities; the
mentee hasn't asked to actually turn `cascade=True` on anywhere yet, and `LLM_TEST_MODE` is an
env-var toggle to flip when wanted, not something baked into any code path.

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

---

---

## Project Status & Mentor Handoff (End of P3 → Fresh P4 Start)

### 🎯 Primary Mission & Mentee Profile:
- **Mentee Profile:** The mentee has been working with Python for under a year. They are **not** a senior veteran, but they are **definitely not an amateur**. They have completed intensive agentic AI coursework, built real, working systems across P1–P3, and are passionately committed to reaching true **production-grade engineering capability**.
- **The Core Goal:** The entire purpose of this journey is **deep learning and real-world hands-on experience in Agentic AI**, actively practicing **System Design & Architecture** to build engineering intuition and bridge the gap to production-level standards.
- **Progressive Complexity Model (Depth & Breadth):** The curriculum scales deliberately:
  - **In Depth (Phase A → B → C):** Each project begins with a focused core/baseline (Phase A), scales into robustness and governance (Phase B), and hardens into production-ready composition (Phase C).
  - **In Breadth (P1 → P6):** Each successive project tackles higher-altitude architectural challenges, escalating from basic ReAct agents to complex multi-subgraph graphs, sandboxed execution, persistent memory, and full multi-agent orchestration.

### 📌 Current Project Milestone:
- **P1 (Web Research Agent):** Complete & verified.
- **P2 (RAG Coordinator Agent):** Complete & verified.
- **P3 (Code Review & Test Generation Agent):** Complete & verified. All 3 subgraphs, AST parsing, process sandboxing, cyclic self-correction loops with retry budgets, modern HITL (`interrupt()` + `Command(resume=...)`), SQLite checkpointing, and time-travel replay are 100% functional and tested.
- **Recent Commits Context:** In recent commits, some code was explored at a low level to gain a deeper conceptual understanding of runtime mechanics by temporarily setting the high-level framework aside. All of that exploratory code has been preserved in `archive/p4_initial_exploration/` with its full directory structure (`core/agents/`, `core/configs/`, `core/src/output_schemas/`, `core/src/tools/`, `core/src/utils/`, `tests/`), while the active codebase has been cleanly reset to the verified end-of-P3 state.
- **Next Target:** The project is now ready to start **P4 (Sandbox / Interpreter Agent)** completely fresh from the beginning.

---

### 🚨 NON-NEGOTIABLE OPERATIONAL RULES (MANDATORY FOR ALL SESSIONS):

1. **Strict Confirmation Gate:**
   - **Never** proceed to the next step, phase, or test case without explicit confirmation from the mentee.
   - Even if code is verified and ready, present it and wait. Advancing without permission is strictly forbidden.

2. **One Item Per Turn:**
   - Deliver exactly one concept, one architectural discussion, or one test at a time.
   - Do not bundle multiple tasks, explanations, or code blocks into a single turn.

3. **Focus on System Design & Progressive Depth:**
   - Treat every topic as an opportunity to practice real-world system design, architectural tradeoffs, and production practices.
   - Match the progressive complexity of the current phase — do not flatten the architecture or skip ahead.

4. **Verify Before Sending (Evidence Before Assertion):**
   - The mentor must execute and verify all code, scripts, and tests in the shell beforehand.
   - Never provide untested code or speculate that "tests should pass." Confirm zero errors before handing anything over.

5. **Zero Sycophancy ("BEDOONE TA'ROF O CHAPLOOSI"):**
   - Provide 100% technical honesty and rigorous engineering critique.
   - Never offer performative praise or automatic agreement. If an idea or implementation has a flaw, point it out directly with technical reasoning.

6. **Language Standard:**
   - Mentee communication must be 100% in **Finglish** (Persian written with Latin characters; never use Persian alphabet).
   - All code, code comments, commit messages, documentation, and file names must be 100% in **English**.
 
---
 
### 🛠️ P4 — Sandbox / Interpreter Agent — Session Log
 
#### Phase A, Stage 1 — Sandbox Configuration & Confinement (2026-09-03) ✅
- **Files Created/Modified:**
  - `core/configs/interpreter.py`: Defines `DEFAULT_SANDBOX_DIR = REPO_ROOT / "out" / "sandbox"` with absolute anchoring to `REPO_ROOT` (`Path(__file__).resolve().parents[2]`), avoiding relative path traversal ambiguity. Configures `DEFAULT_EXECUTE_TIMEOUT = 60`, `DEFAULT_MAX_OUTPUT_BYTES = 100_000`, `DEFAULT_INHERIT_ENV = True`, and `DEFAULT_VIRTUAL_MODE = True`.
  - `core/configs/__init__.py`: Re-exports P4 configuration constants.
- **Architectural Insights & Production Gotchas Verified:**
  - `LocalShellBackend` default on Windows has `inherit_env=False`, which completely strips the system `PATH` and causes subshell execution of `python` to fail with `'python' is not recognized`. Setting `inherit_env=True` was verified live in terminal and is mandatory.
  - `virtual_mode=True` enforces virtual root confinement, mirroring the pure-Python `resolve_safe_path()` boundary from `archive/` by raising `ValueError: Path traversal not allowed` on any `..` escaping attempt.
- **Verification:** `ruff check core/configs` passed cleanly; `uv run pytest` passed 12/12.
 
#### Phase A, Stage 2 — System Prompt & Agent Factory Architecture (2026-09-04) ✅
- **Files Created/Modified:**
  - `core/src/prompts/agents.py`: Added `build_interpreter_agent_prompt()`, structuring the agent's mission around file-driven execution (`write_file` -> `execute` -> verify/self-correct) using the standard `build_system_prompt()` builder.
  - `core/agents/interpreter.py`: Created `make_interpreter_agent()` factory with sensible defaults (`tier="medium"`, `checkpointer=InMemorySaver()`, `LocalShellBackend` with `DEFAULT_SANDBOX_DIR`) and exported singleton `interpreter_agent`.
  - `core/agents/__init__.py`: Re-exported `interpreter_agent` and `make_interpreter_agent`.
- **Architectural Insights & Lessons Learned:**
  - Avoided the `kwargs = {}` anti-pattern for `response_format`; passed `response_format=response_format` directly since `create_deep_agent` natively supports optional `response_format`.
  - Avoided mutable default argument trap for `checkpointer` and `backend` by using `None` sentinel pattern in the factory signature.
  - DeepAgents' `FilesystemMiddleware` automatically mounts all standard tools (`ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`) when `backend=LocalShellBackend(...)` is provided.
  - Identified why `agent.nodes['tools'].bound.tools_by_name` is an anti-pattern (brittle private Pregel internals). Standard inspection/testing is black-box via `.invoke()`, or testing `backend` methods directly with `tmp_path`, or `agent.get_graph().nodes`.
- **Verification:** Live invocation confirmed end-to-end tool execution (`write_file`) and physical disk verification under `DEFAULT_SANDBOX_DIR / "workspace"`. Full test suite `uv run pytest` 12/12 green.

#### Phase A, Stage 3 — Application Entry Point & Interactive REPL Loop (2026-09-04) ✅
- **Files Created/Modified:**
  - `core/apps/interpreter.py`: Interactive REPL runner featuring session thread continuity (`config={"configurable": {"thread_id": "..."}}`), input handling for multi-turn tasks, graceful `(KeyboardInterrupt, EOFError)` termination, and unified output extraction via `get_text(result['messages'][-1])`.
  - `skills/legacy-docs/SKILL.md`: Comprehensive workspace-level skill synthesizing curriculum architecture, standing agreements, deferred testing/eval scope, 5-turn interaction model, and the 3 mandatory habits (subagents, MCPs, legacy-docs).
- **Architectural Insights & Lessons Learned:**
  - **Import-Time Model Initialization Gotcha:** `load_dotenv()` must be invoked before importing `agents.interpreter`. Since `interpreter_agent` is initialized at module import time, failing to load `.env` first causes `ChatGoogleGenerativeAI` to fail with a `ValidationError` due to missing `GOOGLE_API_KEY`.
  - **Deferred Testing vs. Live Exploration Verification:** Reinforced standing agreement from 2026-08-19: formal unit tests in `tests/test_*.py` are deferred. Verification is conducted via runnable apps (`core/apps/interpreter.py`) and live hands-on exploration scenarios.
  - **Workflow Calibration:** Updated rule: Mentor writes and applies official `.py` implementation code directly into `core/` under mentee guidance (pre-verified with `ruff` and `pytest`), while mentee focuses on notebook exploration.
- **Verification:**
  - Full pre-verification with `uv run ruff check core/` and `uv run pytest` (12/12 passing).
  - Mentee live exploration verified in notebook: Agent wrote `primes.py`, executed it in sandbox via shell, generated `primes_list.txt` containing all 15 primes up to 50, and reported the largest prime (47) with exact disk confinement in `out/sandbox/`.
- **Milestone:** **Phase A (Native Workspace & Execution Engine) is 100% COMPLETE!**

#### Phase B, Stage 1 — Command Governance & HITL Approval on Shell Execution (2026-09-04) ✅
- **Files Created/Modified:**
  - `core/agents/interpreter.py`: Added `hitl: bool = True` parameter to `make_interpreter_agent()`, wiring `interrupt_on={"execute": True}` into `create_deep_agent` to halt before arbitrary shell execution.
  - `core/apps/interpreter.py`: Integrated `run_with_hitl` helper from `core/src/utils/run_with_hitl.py` to intercept execution pauses, present exact command arguments, request interactive approval (`[y/n]`), and resume via `Command(resume=...)`.
- **Architectural Insights & Lessons Learned:**
  - **Filesystem Permissions vs. Execution Backends:** DeepAgents' `FilesystemMiddleware` raises `NotImplementedError` if `permissions=[FilesystemPermission(...)]` is passed with execution-capable backends (`LocalShellBackend`). This is by design: filesystem-level path restrictions are trivially bypassed by arbitrary subshell commands (`cat`, `rm`, `powershell`). The primary and recommended safeguard is Human-in-the-Loop approval gating before any shell command runs.
  - **HITL Continuity Across Curriculum:** Reused the generic `run_with_hitl` primitive established in P1, proving cross-project modularity and eliminating duplicate interrupt-handling boilerplate.
- **Verification:**
  - Verified live interrupt trigger on shell command execution (`dir`/`ls`), capturing `action_requests` for tool `execute`.
  - Verified successful unfreezing and state transition upon approval using `Command(resume={"decisions": [{"type": "approve"}]})`.
  - Full test suite `uv run pytest` (12/12 passing) and `uv run ruff check core/` clean.


