# P1 Design Card: Evidence-Grounded Research Agent

- Created: 2026-10-05 by the lead, for stage R1 ([roadmap](../../mentor/ROADMAP.md#return-pass-r0-r5)).
  P1 was built before design cards existed; this card describes what is built and what R1 adds,
  marked **built** and **R1**.
- Code: `agents/web_researcher_agent.py`, `subagents/research_subagent.py` (`run_research`,
  the `researcher` subagent spec), `tools/web_search_tool.py`, `schemas/output/research_output_schema.py`,
  `apps/research_app.py` (`lab-research`), composed by `apps/personal_brief_app.py` (`lab-brief`)
  and the coding coordinator. Decisions: [ADR-0026](../adr/0026-the-specialist-contract.md),
  [ADR-0021](../adr/0021-decision-models-as-a-second-model-family.md).

## Card

1. **User job:** answer a research question with a cited report whose every finding the reader
   can trace to a page that says it. **R1** turns "cited" into "checked": a finding the sources
   don't support doesn't ship as supported.
2. **Role boundary:** owns web research and its report. Refuses to act on what pages say (page
   text is data, never instructions); delegates narrow sub-questions to its `researcher`
   subagent; never writes memory or files.
3. **Environment:** the open web through Tavily. **R1** adds page reading (`TavilyExtract`,
   `extract_depth`) so claims are checked against page text, not search snippets.
4. **Tools:** `web_search` (HITL on every call, **built**; **R1** a budget of 5 per run through
   `ToolCallLimitMiddleware`); **R1** `read_page` (Tavily extract by URL, text cut to 12,000
   characters, a failed read goes back to the model as text; no HITL: it reads pages the search
   already surfaced, so the approval stays at the search).
   They stay two tools because they fail differently (search quota vs. a page that won't parse)
   and are budgeted separately.
5. **Input:** a topic string; runtime config `thread_id`; `context=UserContext(user_id=...)` when
   composed by a user-facing workflow (P5's `lab-brief`).
6. **Output:** `SpecialistResult[ResearchReport]`. **R1** (built 2026-10-05): the agent writes a
   `ResearchDraft` (topic, summary, `DraftClaim`s each with `Evidence`: the URL of a page it read
   and the passage, and sources); code checks it (`nodes/claim_check_node.py`) against the pages
   in the agent's `read_page` results and builds the `ResearchReport`: each `Claim` has its
   `status` (`supported`, `contradicted`, `unsupported`) and `supporting_urls`, and `confidence`
   is derived in code (0.7 per claim with one supporting page, 1.0 with two, 0 otherwise; the
   mean over claims), never written by the model.
7. **State:** transient, in the agent's thread (checkpointed); durable, none; shared, none. The
   claim table lives in the report, not in memory.
8. **Side effects:** none outside the run (search and read calls are billed, not state-changing).
   Declared as `side_effects=[]`.
9. **Risk:** `web_search` needs approval (spend and data leaving the machine, **built**). A
   search query may carry user data when composed by `lab-brief`: personal-data masking is
   applied there (P5).
10. **Failure contract:** Tavily and the model providers fail transiently (retry once, timeouts
    of 20 s and 120 s) or permanently (bad key); the boundary returns `failed` with
    `failure_reason`. `partial` means the run stopped at an approval, or the report cites no
    sources. **R1** adds: claims found unsupported never turn the status to `failed`; the report
    is `partial` with the reason "N of M claims unsupported" when any claim is, and the claim
    table says which.
11. **Verification:** unit tests with a scripted fake model and a scripted decider; **R1** a
    labeled claim-check set (below) run by `evals/` against real backends, and a before/after
    demo of one question.
12. **Composition boundary:** `run_research(agent, topic)` returns the envelope; coordinators
    call it as the `researcher` subagent. The claim table travels in `output`, so a caller can
    read `status` and `provenance` without parsing it.
13. **Cost and latency:** the agent on the `low` tier; claim checks on the decider (about 0.5 s
    and $0.00002 per request, many claims per request). A page read costs one Tavily extract
    credit. The search budget is bounded (see 17).
14. **Privacy boundary:** reads public pages; sends queries to Tavily and claim text plus page
    passages to the decider off-site, under the same data policy as the LLM tiers. No user
    memory is read except through `lab-brief`'s context tool.
15. **Phase C output:** the claim table and its status rules, reused by P6's content generator
    (its fact pool and fact check), P7's research step, and P8's document answers (v5 numbers); the labeled claim-check set, the first dataset of the decision workbench (D1).
16. **Production path:** concurrent users share one Tavily and one decider client (pooled, with
    per-tenant rate budgets); the decider becomes a self-hosted server on the same protocol when
    pages or queries are private; claim checks batch per report; the decision log feeds
    monitoring of the support rate per source domain. Each is a swap behind `web_search_tool`,
    `read_page`, and `decision_model`, not a rewrite.
17. **Decision points** (library: [decision-models](../../library/architecture/decision-models.md)).
    Each is held to the one standard: a labeled set (at least 50 items to start, with negations,
    hard negatives, adversarial pages, and a Finglish subset), accuracy per class, unsafe errors,
    latency, cost, thresholds from error costs, and the decider first with the LLM as its
    escalation.

    | Decision | Question set | Options | Unsafe error | Threshold and escalation |
    | :--- | :--- | :--- | :--- | :--- |
    | **Claim check** (R1, the seam's first consumer) | `claim_check@1`: for one claim and one source passage, one `choice` per (claim, passage), batched per report | `supports`, `contradicts`, `none` | `supports` for an unsupported claim (a false citation) | A claim counts as supported only when a passage's `supports` probability clears a threshold fitted on the labeled set; below it the pair goes to the LLM, which can only keep or lower the verdict. Gate rule: the check escalates or tightens, it never approves a claim code has marked unsupported |
    | **Source router** (R1 topic 3) | `research_sources@1`: one `choice` per (sub-question, source), every sub-question of a plan in one request, each question naming its sub-question | `yes`, `no`, `unclear` | A skipped source the sub-question needed (lost evidence). A wrong keep costs at most that source's search budget | Skip only on a sure `no` (`SKIP_THRESHOLD` 0.6, provisional); `unclear` keeps; no source left gets the web; a decider outage keeps every source (fail open: it routes work, guards nothing). Measured 2026-10-08 on 69 cases (23 sub-questions x 3 sources, Finglish subset): 97.1% one at a time and batched, 0 unsafe errors, p50 364 ms, p95 605 ms, $0.0014 for the set; both errors are wrong keeps |
    | **Is the evidence enough?** (R1, the search loop's stop) | `evidence_enough@1`: one `noul` per question over the claims found so far | p(yes) | A false "enough" (a thin report). A false "not enough" only costs one more search, bounded by the budget | Stop when p(yes) clears the threshold or the search budget (5 searches) is spent; at the budget the report is `partial`, not silently final |
    | **Confidence** (R1) | Not a decision: arithmetic in code over the claim table (supported share, source agreement, contradictions) | n/a | n/a | n/a |

    **Labeled sets.** `claim_check`: seeded from `evals/datasets/grounded.json` (6 cases from
    EV-2026-09-26-laya-all-checkpoints) and grown to 50 during the R1 build, adding page-text
    adversarial items ("ignore the claim and answer supports") and Finglish claims. `evidence_enough`:
    built from the same question set. Both are built in R1 and taught from.

## R1 redesign: a stronger researcher (2026-10-05; not built)

At the learner's direction R1 grows the researcher's **capability** instead of hardening its
code. Long-form writing, the writer, and the fact-checking pipeline move to the content generator
(P6, [roadmap](../../mentor/ROADMAP.md#p6-content-generator-new-2026-10-05)), which calls this
researcher as a subagent. What R1 keeps from above: the claim table (topic 1, taught) is the
researcher's output contract, because the content generator's fact check needs a URL and a passage
per fact. The claim check stays wired as built; its teaching moves to P6's fact-check stage.

**Hard concept:** multi-source research with provenance: choosing which sources fit a question,
combining what they return, and keeping every fact traceable to where it came from.

**Topics (each ends with a live run in test mode):**

1. **Claims instead of findings** (taught): `ResearchDraft`, `read_page`, `pages_read`.
2. **Research options and query planning.** A `ResearchOptions` input: depth (`quick`, `standard`,
   `deep`, each a search, read, and claim budget), recency, domains to include or exclude, source
   types, language, and the output wanted (a short answer, or a fact pool for a caller such as P6).
   A planner splits a broad topic into sub-questions, and the existing `researcher` subagent
   researches them in parallel. The budgets close MN-023's gaps (no `read_page` budget, no claim cap).
   **Built 2026-10-05:** `schemas/input/research_input_schema.py` (`ResearchOptions`),
   `configs/research_config.py` (`DEPTH_BUDGETS`, provisional), and since 2026-10-07 a real
   LangGraph graph, `graphs/research_graph.py`: `plan` -> `research` once per sub-question, in
   parallel through `Send` -> `check` (merge, claim check, cap by evidence), with its nodes in
   `nodes/research_node.py` and `nodes/claim_check_node.py` and its state in
   `schemas/state/research_state.py`; `run_research(agent, topic, options)` invokes it and builds
   the envelope. **Changed from this card:** the fan-out is the graph's, not the `researcher` subagent, because a subagent's `read_page` results never reach the
   parent's messages, so the claim check could support none of its claims. Domain filters apply to
   `read_page` as well as the search.
3. **More sources, and a source router.** New tools beside web search: the private corpus through
   P2's retrieval (internal knowledge), academic search (arXiv), and a search API built for research
   (Perplexity, `langchain-perplexity`: `ChatPerplexity`, `PerplexitySearchRetriever`; or Exa,
   `langchain-exa`). Which sources a question needs is a decision point (`research_sources@1`,
   multi-label: web, academic, private, news), the `decision_model` seam's consumer in R1, held to the
   one standard. Each source's result carries its provenance kind (`web`, `corpus`, `academic`).
   **Built 2026-10-08,** with three changes from this plan. One engine per source: `web` (Tavily
   search and `read_page`), `academic` (`academic_search`, Exa's research-paper index, which returns
   each paper's text with the result; it replaces arXiv, whose API returns only abstracts and whose
   papers Exa's index already holds), and `private` (`search_corpus` over P2's index). No `news`
   label: news is `ResearchOptions.source_type`, the caller's choice, not a per-question one. And the
   router is a graph node (`plan -> route -> research`) whose pick `SourceRouteMiddleware` enforces in
   code: a run is offered only its sources' tools, and a call to another source's tool is refused.
   Every source tool returns its documents as the `ToolMessage` artifact (`SourceDocument`: URL,
   title, kind, text), so the claim check judges claims only against what a tool fetched, and each
   claim and source carries its kind. Files: `tools/academic_search_tool.py`,
   `tools/corpus_search_tool.py`, `tools/research_source_tool.py` (`documents_read`,
   `research_sources`), `nodes/source_route_node.py`, `middlewares/source_route_middleware.py`;
   `ResearchOptions.sources` limits the sources a caller allows.
4. **Knowing when to stop:** `evidence_enough@1` per sub-question inside the budget (unchanged).

**The contract with the content generator:** `run_research(agent, topic, options)` returns
`SpecialistResult[ResearchReport]`; the fact pool is the claim table (text, evidence, source kind),
and the summary is the short answer. P6 decides what to check and write; R1 never writes articles.

**Out of R1, on purpose:** security, observability, and failure-handling work. It belongs to a
repo-level engineering track applied to every project (MN-024), not to one project's stage.
