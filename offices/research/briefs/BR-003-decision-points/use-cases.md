# BR-003 › Use cases: three loops, and where a decider doesn't belong

Supports [BR-003](README.md) version 2. Code read on 2026-09-27; roadmap per the lead's
[ROADMAP](../../../lead/ROADMAP.md) v4. Everything is judged at production load, with the rubric
in the [design guide](../../landscape/decision-models/design-guide.md#choose-the-backend).
Verdicts are advice; the lead decides, and each stage's measurement settles it.

## 1. The product loop: our agents and graphs

### Around the models (harness decisions)

| Decision point | Today | Evidence | Proposal | Stage |
| :--- | :--- | :--- | :--- | :--- |
| **Which specialist takes a request**: the coding coordinator's subagents, the repo-insight coordinator, P6's workflow, and P12's control tower | The coordinator LLM chooses through tool calling | Routing spike 32/32 × 3, with vague requests correctly sent to "clarify", where two LLM tiers scored 30/32 **[V]**; MetaTool abstention 87.0% vs 50.4% **[T]** | A decider pre-routes, with low confidence falling back to the LLM. At P6-C1, compared as a third control style, with the decider at the workflow's branches | P6 (A1, C1), P12 (A1, C1) |
| **Which model tier takes a turn** (`LLMRegistry`) | A static tier per call site (ADR-0014) | Model routing is a recurring pattern **[S][T]**; ModelRouterMiddleware has no confidence gate | Difficulty routing with a gate, as a contender when tiers are compared by measurement | P9-B2, E2 |
| **Which skills load**: the P5 assistant's skills and the repo-insight skill | DeepAgents lists skills in the prompt | Skill suggestion: wrong loads 16.8% → 7.3% **[C]** | Rank and re-check once the skill count grows past a handful; with two skills today, record it as a trigger | Trigger: more skills than an agent's prompt lists legibly (P5 teaching pass or later) |
| **May this tool call run**: search approval (P1), `execute` (P4), the coordinator's unapproved shell | Static HITL on every call, or no approval at all | Gate patterns **[S]**; 147/200 authority-claiming injections succeeded **[T]** | **Escalate, never approve.** Static rules first, and the decider only adds "ask a person". Anything that loosens a control needs P7-C3's red-team set | P6-B3 (static plus escalation), P8-B3, C1, P11-B1 |
| **Which tool results stay in context** | Everything stays until DeepAgents summarizes | Verbatim compaction, tool-result guardrails **[T]** | A keep-or-drop pass before summarizing, measured on long P4 and P1 sessions | P12-B2 (context budgets), E1 |
| **Did a specialist really succeed**: the envelope's `ok`, `partial`, or `failed`, and its provenance | Typed by the specialist itself (R0) | Done-claim checks at AUROC 0.976 **[T]** | Parents verify a claim of `ok` against the evidence before they trust it, as an escalation | P6-A1, B2 |
| **Is a remembered fact stale; should a write be allowed** (P5 memory) | Consolidator LLM; security guard LLM | Staleness 59/60, with thin margins on implied changes **[V]**; guard 8/8 designed, no unsafe error **[V]** | A staleness pre-pass that proposes, while the consolidator still writes (ADR-0012), with implied cases escalated. The guard gets a tightening ensemble beside the LLM | P5 teaching pass |
| **Evaluation**: eval-lite scenarios, LangSmith online evals | Hand-written checks; LLM judges where used | LangSmith: 100% agreement on 5 traces; Langfuse: 91.5% agreement with Claude **[C][T]** | The same typed checks run on saved traces and as guardrails | R0's shared eval harness onward; P8-C2 |

### At the graph's branches (P2 and its successors)

| Decision point | Today | Evidence | Proposal | Stage |
| :--- | :--- | :--- | :--- | :--- |
| `grade_documents_node`: is each document relevant | One sequential LLM call per document | 6/6, and 5-6/6 batched in ~0.45 s **[V]**; reranking tied with Cohere on 14 datasets **[T]** | A batched decider, which can also rerank, with low margins escalated | R2 |
| `check_hallucination_node`, and the groundedness middleware | LLM (`low`) | 6/6 on single-claim cases **[V]**; draft, verify, escalate **[C]** | The verifier in R2's reroute: when unsupported, reroute or escalate | R1 (LLM, logged), R2 |
| Citation support (R1's claim provenance) | Planned | TypeSafe's citation cookbook **[S]** | The LLM in R1, with every decision logged as labels; a decider measured from R2 on | R1, R2 |
| Security guard verdicts | LLM | As above | A tightening ensemble; never alone | P5 teaching pass |

## 2. The development loop: the Claude sessions working on this repo

Every item below would need the lead's decision, because `.claude/` and `scripts/` are the lead's.
Hooks that change what a session may do are security settings, so they are the user's call.

| Decision point | Today | Evidence | Proposal |
| :--- | :--- | :--- | :--- |
| **"Done" without verification** (principle 5) | The rule is written in the principles; nothing checks it | jev-belay: AUROC 0.976 on 100 labeled stops **[T]** | A Stop hook that escalates when files changed and no check ran, advisory first |
| **Conventions no linter can express**: Principle 3's rule of three, one fact in one file, the ownership boundaries described in prose, `AGENTS.md` conventions 1-11 | Human review; `check_docs.py` handles links | Our lint spike: AUROC 1.0 on meaning-level rules, weak on syntax-level rules **[V]**; Abide: 10 of 39 real flags confirmed **[T]** | Syntax rules go to the AST, `ruff`, or `check_docs`. Meaning rules go to an advisory decider in CI or a hook, never blocking until replay-measured |
| **Scope and intent**: an edit outside what was asked, or edits made when only a question was asked | Human review | jev-gates **[T]** | An advisory gate, measured on our own session replays |
| **Commit honesty**: does the message match the diff; conventional-commit type | Human | jev-commit **[T]** | An advisory pre-commit check |
| **Which rules a session loads** | `CLAUDE.md` loads `AGENTS.md`, the principles, the protocol, and the mentor charter in every session | jev-rules **[T]** | Measure first: do sessions miss rules because of volume? If they do, select the rules per task |
| **Research operations** | Manual | This office classified 551 builds for $0.03, at 19/19 agreement at confidence ≥ 0.9 **[V]** | Use inside the research office for sorting sources and bulk triage. No approval needed; it is our own work |

## 3. The learning loop: teaching this learner

Proposals for the lead's pedagogy and the mentor's procedure; details in
[curriculum.md](curriculum.md#teach-with-it-the-learning-loop). Formative only; the learner's
private scratch area is never read.

| Decision point | Proposal |
| :--- | :--- |
| Which misconception a learner's typed code or answer shows | Choose the matching hint or re-teach step; the mentor words it |
| Whether the learner is stuck or tired: signals in the conversation | Offer a stop point or a smaller step, which the charter already asks for, decided consistently |
| How well-calibrated the learner's predictions are | The learner states a probability with each prediction question; track calibration over time |
| Teach-back coverage (DEC-008) | A rubric of atomic questions ("explained why the gate fails closed?") gives the mentor a consistent checklist; the mentor still judges |
| Item analysis across stages | Which concepts keep coming back as gaps, which becomes review items (PEDAGOGY's assessment) |

## Where it doesn't belong

- **Generation:** answers, reports, rewrites, review text, skill drafts, the Finglish repair's
  output.
- **Code-decidable checks:** syntax, script detection (the Finglish detector is a regex),
  arithmetic, dates, schema validity.
- **A sole security gate,** or anything that grants on the decider's say.
- **Grades or any summative judgment about the learner.**
- **Any decision point without a labeled set.**
- **Implied-condition decisions without escalation:** memory staleness on implicit changes, and
  conflicts the consolidator resolves.
