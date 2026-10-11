# Product Enhancement Proposals: 10 New Product Ideas & 5 Concrete Refinements

---

### Important Disclaimer & Non-Binding Notice

> [!IMPORTANT]
> **To the Developer / Reader:**
> This document was prepared by Gemini upon the user's request to propose product-focused expansions and technical refinements for `agentlab` (strictly focusing on the software product and system capabilities, independent of the pedagogical/teaching layer).
>
> **The developer has zero obligation to accept, adopt, or implement any of the ideas or refinements below.** They are provided strictly as optional architectural inspiration.

---

## Part I: 5 Concrete Refinements to Current Implementations & Designs

### 1. P3 Code Review: Differential Sandbox Verification (`code_review_node.py`)
- **Current State:** In `src/agentlab/nodes/code_review_node.py` (`execute_tests_node`, line 104), the generated pytest suite is executed solely against `state["code"]` (the original *buggy* input code). If `generate_tests_node` writes a regression test that exposes the bug identified in `review_code_node`, the test fails against `state["code"]`, and `fix_tests_node` (line 111) rewrites the test so that it passes on the buggy code. Meanwhile, `review.refactored_code` is never executed or verified in the sandbox—neither before `approved_refactor_node` interrupts the user for approval nor after `apply_refactor_node`.
- **Proposed Refinement:**
  - Run the generated test suite against **`review.refactored_code`** to verify that the proposed refactor is syntactically valid and passes all unit and regression tests.
  - Optionally run the suite against `state["code"]` as well to produce a **Differential Test Report** (showing which tests failed on the original code and now pass on the refactored code).
  - Include this verification status in the `interrupt()` payload in `approved_refactor_node` so the human reviewer knows whether the refactored code actually passes the tests before approving it.

### 2. R1 Claim Check & Merge: Passage-Window Verification, Contradiction Penalty & Summary Synthesis (`claim_check_node.py`)
- **Current State:** Inspection of `src/agentlab/nodes/claim_check_node.py` reveals three edge cases in multi-sub-question research runs:
  1. **Raw Summary Concatenation (`_merge`, line 236):** `summary=" ".join(draft.summary for draft in drafts)` concatenates sub-question summaries verbatim without synthesis, and identical claims discovered independently by two sub-questions are not deduplicated before claim checking.
  2. **12k Prefix Cut vs. Passage Window (`check_pair_group`, line 105):** The decider is given `page[:MAX_PAGE_CHARS]` (the first 12,000 characters of `documents[url].text`). When a corpus file or joined document exceeds 12,000 characters (noted in `STATE.md`), claims citing passages past character 12,000 are marked `unsupported`—even though `DraftClaim.evidence` already contains `evidence.passage`.
  3. **Unilateral Contradiction & Flat Confidence (`_status`, line 139 & `derive_confidence`, line 126):** If 3 sources return `supports` and 1 source returns `contradicts`, `_status` marks the claim `contradicted` while still populating `supporting_urls`. Furthermore, `derive_confidence` scores both `unsupported` and `contradicted` as `0.0`, giving a report with contradicted claims the exact same confidence score as one with merely unverified claims.
- **Proposed Refinement:**
  - Verify that `evidence.passage` occurs inside `documents[url].text` and slice a window centered around the matched passage(s) when building the decider input for long documents.
  - Distinguish pure `contradicted` (no supporting sources, at least one contradicting) from `disputed` (both supporting and contradicting sources exist), or apply a negative weight to `contradicted` claims in `derive_confidence`.
  - Add a lightweight synthesis or claim deduplication pass in `_merge` when `len(drafts) > 1`.

### 3. Jev Model Router (`ADR-0031`): LCEL Runnable Composition & Dynamic Prompt-Size Floor (`router_model.py`)
- **Current State:** In `src/agentlab/models/router_model.py` (`ModelRouter.chain`, line 232), routing requires passing `task: str` eagerly when constructing the chain (`model_router.chain(task, structured=Schema)`). However, nodes across `agentlab` (`rag_node.py`, `code_review_node.py`, `memory_consolidation_node.py`) use LCEL composition (`PROMPT | llm_model.chain(...)`) invoked with a dictionary of template variables. If a caller passes only the short question string as `task`, `len(task) > LARGE_TASK_CHARS` (line 185) never accounts for large injected contexts (e.g., retrieved RAG chunks or large source files).
- **Proposed Refinement:**
  - Add `model_router.runnable(*, structured=None, floor=None, task_key: str | None = None) -> Runnable` so call sites can write `PROMPT | model_router.runnable(structured=Schema)`.
  - At invocation time, inspect the total rendered `PromptValue` length to enforce `LARGE_TASK_CHARS` accurately while passing the concise `task_key` (or `_excerpt` of the rendered prompt) to the Jev decider.

### 4. P1 CLI Entry Points (`lab-research` & `lab-brief`): Wiring Through `build_research_graph` (`research_app.py`, `personal_brief_app.py`)
- **Current State:** Both `src/agentlab/apps/research_app.py` (line 65) and `src/agentlab/apps/personal_brief_app.py` (line 74) invoke `make_researcher_agent` directly as a single agent run and then call `verify_research(result)`, bypassing `build_research_graph` (`plan` -> `route` -> `Send` fan-out -> `check` with `_cap`). As a result, interactive CLI users do not get query planning, source routing (`SourceRouteMiddleware`), or post-check claim capping.
- **Proposed Refinement:**
  - Expose `--depth {quick,standard,deep}` on `lab-research` and `lab-brief`.
  - Wire the researcher agent into `research_graph` as a native compiled subgraph sharing the parent checkpointer (so HITL interrupts propagate directly to `run_with_hitl` / `stream_with_hitl`), allowing CLI runs to execute the full R1 graph pipeline.

### 5. P6 Content Generator Architecture: Pre-Write Claim-to-Section Allocation & Section-Local Grounding (`mentor/ROADMAP.md`)
- **Current State:** In `mentor/ROADMAP.md` (lines 156–165), the P6 pipeline runs: `outline -> section writing (parallel Send in B2) -> grounding check (sentence_grounded@1) -> editorial passes`. Checking every sentence of the full article against the entire fact pool after all sections are written increases quadratic (sentence $\times$ fact) context size and allows ungrounded claims or cross-section repetition to enter the draft before gating.
- **Proposed Refinement:**
  - **Claim-to-Section Mapping in the Outline Node:** Have the outline schema assign specific `supported` claim IDs from the fact pool to each section (`SectionPlan.assigned_claim_ids: list[int]`).
  - **Section-Local Grounding Gate:** Run `sentence_grounded@1` inside each parallel section branch against only that section's assigned claims (plus a 1-retry local rewrite) *before* sections are merged for the editorial pass.

---

## Part II: 10 New Product Ideas (Improving & Expanding the Core Product)

### Idea 1: Epistemic Staleness & Link-Rot Watchdog ("Living Research Briefs")
- **Product Value:** Research reports (`ResearchReport`), P6 articles, and P7 decision briefs degrade over time as cited web pages change, disappear (404), or are superseded by newer evidence.
- **System Design:** Add a `lab-verify <report.json>` command and background watchdog node. Given a saved `ResearchReport`, it re-fetches only the `supporting_urls`, compares content hashes against the original run, and—only for pages whose text changed—re-runs `claim_check@1` on the affected claims. It outputs an **Epistemic Drift Report** highlighting which claims remain `supported`, which suffered link-rot, and which are now `unsupported` or `contradicted` by updated page content.

### Idea 2: Structured Epistemic Conflict & Authority Resolution Engine
- **Product Value:** In real-world research and enterprise RAG, sources frequently disagree (e.g., an internal P2 design doc vs. a public web post vs. an Exa academic paper). Treating any conflict as a flat `contradicted` failure hides critical nuance.
- **System Design:** When a claim receives both `supports` and `contradicts` verdicts across different URLs, route the conflicting `(claim, doc_A, doc_B)` tuple to a **Conflict Analyzer** that classifies the disagreement:
  - *Temporal Supersession* (newer source updates an older metric/API),
  - *Authority Asymmetry* (primary/corpus/academic source vs. secondary web source), or
  - *Genuine Domain Controversy* (unresolved debate).
  Surface these explicitly in `ResearchReport.disputed_claims` so decision-makers see *why* sources disagree.

### Idea 3: First-Class FinOps Ledger & Dynamic Budget Circuit Breakers (`BudgetContext`)
- **Product Value:** Current budgets bound tool call counts (`ToolCallLimitMiddleware`), not actual monetary spend or cumulative token consumption across multi-agent delegations.
- **System Design:** Attach a thread-safe `CostLedger` to `SpecialistResult` (`cost_usd: float`, `input_tokens: int`, `output_tokens: int`, `external_credits: dict[str, int]`) calculated from model registry specs and Jev's `ClassifierResponse.usage`. When a composed workflow (P6, P7, P14) is invoked with a `max_budget_usd` cap:
  - At 75% spend, `model_router` automatically lowers its ceiling to `low` tier and sets research depth to `quick`.
  - At 100% spend, the workflow gracefully halts further fan-outs and synthesizes a `partial` result from evidence gathered so far.

### Idea 4: Verified Multi-File Patch & PR Specialist (`lab-patch`)
- **Product Value:** P3 reviews a single code snippet and prints refactored text; P4 executes arbitrary commands in a sandbox. Combining them into a **Verified Patch Producer** turns `agentlab` into an actionable software engineering tool.
- **System Design:** Given an issue description or failing test, the workflow uses P2 to locate relevant repo files, creates an isolated temporary git worktree inside the P4 sandbox, applies multi-file edits, runs `ruff check`, `pytest`, and P3's review gate, and outputs a clean, git-applyable `.patch` file accompanied by a signed `VerificationReceipt` (lint status, test pass count, diff stat).

### Idea 5: Tiered Episodic Memory with Decider-Driven Recall (`memory_recall@1`)
- **Product Value:** In P5 (`lab-assistant`), loading all user memory files into the prompt scales poorly once a user accumulates months of preferences, project notes, and history.
- **System Design:** Split P5's per-user memory into three tiers:
  1. **Pinned Core Profile (`profile.md`):** Always injected (capped at ~50 lines).
  2. **Topical Memory Modules (`/memories/topics/*.md`):** On each turn, a fast Jev decider call (`memory_recall@1`) scores the user's message against the list of memory module titles/summaries and injects only the relevant 1–2 files for that turn.
  3. **Cold Archive:** Automatically compacted historical notes searchable via a read-only tool.

### Idea 6: Cross-Run Verified Evidence & Document Vault (Zero-Cost Knowledge Reuse)
- **Product Value:** When a user researches related topics across multiple sessions (e.g., running `lab-research`, then `lab-brief`, then P6 content generation on the same domain), the agent repeatedly pays Tavily/Exa credits and asks for HITL search approvals for URLs it already fetched and verified hours earlier.
- **System Design:** Persist fetched `SourceDocument` objects and `supported` `Claim` records into a local SQLite evidence vault (`out/state/evidence_vault.db`) indexed by URL, domain, and `fetched_at` timestamp (with configurable TTLs per source kind: e.g., 30 days for `academic`, 24 hours for `web`). Outbound search and `read_page` tools check the vault first; cache hits require no external API call and no HITL interrupt.

### Idea 7: Adversarial "Devil's Advocate" & Falsification Node for Decision Workflows
- **Product Value:** LLM researchers and planners exhibit strong confirmation bias—if a user asks *"Why is architecture X better than Y?"*, search queries disproportionately retrieve arguments favoring X.
- **System Design:** Add a `falsify: bool = True` option in `ResearchOptions` (and make it mandatory in P7's Research-to-Decision workflow). For any thesis or candidate decision, the planner generates a dedicated **Counter-Hypothesis / Pre-Mortem Sub-Question** tasked exclusively with finding failure cases, benchmarks, or counter-evidence. The final report separates confirmatory claims from falsification findings.

### Idea 8: Reversible PII Pseudonymization Vault (Two-Way Safe Execution)
- **Product Value:** Currently, `redact_secrets` and `PIIMiddleware` destructively replace emails, IPs, and identifiers with `[REDACTED]`. While safe for research, in operational workflows (P9 Customer Support, P12 API Operations) the agent often needs to pass a real customer email or order ID to an authorized downstream tool without ever exposing that PII to hosted LLMs or LangSmith traces.
- **System Design:** Replace destructive redaction with a session-scoped **Pseudonymization Vault**:
  - Inbound middleware replaces `alireza@example.com` with deterministic token `<PII_EMAIL_01>` before checkpointing, tracing, or calling the LLM.
  - The LLM reasons over and emits `<PII_EMAIL_01>` in tool arguments.
  - At the authorized tool execution boundary (after HITL approval), the vault rehydrates `<PII_EMAIL_01>` back to the real value exclusively for the outbound API call.

### Idea 9: Rich Terminal Dashboard & Interactive Diff Approval UI (`RichHITLRunner`)
- **Product Value:** All eight `lab-*` CLI apps currently rely on plain `input()` and `print()`, making parallel `Send` branches, multi-claim verification tables, and code/memory diffs hard to inspect during HITL pauses.
- **System Design:** Build a clean terminal presentation adapter in `utils/console_util.py` (using `rich`):
  - **Side-by-Side / Unified Color Diffs** when prompting the user to approve P3 code refactors or P5 memory edits.
  - **Live Status Tree** during `research_graph` execution showing each sub-question's routed sources (`web`, `academic`, `corpus`) and progress.
  - **Formatted Evidence Table** rendering `ResearchReport` claims with color-coded status badges (`SUPPORTED`, `CONTRADICTED`, `UNSUPPORTED`), source kinds, and confidence score instead of raw JSON dumps.

### Idea 10: Lightweight Structured-Output & Tool-Call Self-Healing (`SchemaRepairRunnable`)
- **Product Value:** When a model produces a high-quality analytical response that fails Pydantic validation due to a minor formatting or enum mismatch, `with_fallbacks` currently discards the entire response and re-runs the whole prompt on a backup provider—doubling latency and token cost.
- **System Design:** In `llm_model.chain(tier, structured=Schema)`, catch Pydantic / output-parsing `ValidationError` exceptions separately from network/provider errors (`failure_kind`). Feed the malformed payload plus the exact Pydantic error message into a fast, minimal repair prompt on the `low`/`free` tier before triggering a full provider fallback.
