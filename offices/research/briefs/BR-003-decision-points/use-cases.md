# BR-003 › Use cases: where a decision model fits, and where it doesn't

Supports [BR-003](README.md). Code read on 2026-09-27 (R0 was in progress in another session);
roadmap per the lead's [ROADMAP](../../../../offices/lead/ROADMAP.md) v4. Everything is judged at
production load, with the rubric in
[design guide](../../landscape/decision-models/design-guide.md#choosing-the-backend).

The **verdict** column is advice. The lead decides; the measurement at each stage settles it.

## Today's AI steps

| Site | What it decides | Rubric reading | Evidence | Verdict | Stage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `nodes/rag_node.grade_documents_node` | Is each retrieved document relevant? Today one sequential LLM call per document (`opensource`) | A closed yes/no; low cost of error, because the rewrite loop recovers; an English corpus; R2 brings the labeled set | Jev 6/6 one at a time, and 5-6/6 with all six in one ~0.45 s request **[V]**; Laya 5/6 | **Strong candidate:** one batched request per question, with low-margin documents escalated to the LLM | R2 |
| `nodes/rag_node.check_hallucination_node` | Is the answer grounded in the documents? (`low`) | Closed; a high cost of error, since it is P2's trust gate; multi-claim answers need one question per claim | Jev 6/6 on single-claim cases **[V]** | **Candidate as the verifier** in a draft-verify-escalate loop, the decision R2's rerouting will branch on | R2 |
| `middlewares/groundedness_middleware` | The same check over all tool outputs (`low`) | Closed; a large state, so context rot and the 32k limit apply | As above | The LLM stays in R1, where the middleware gets wired in for citations; a decider is measured from R2 on | R1 (LLM, decisions logged), then R2 onward |
| `middlewares/security_guard_middleware`, with `MEMORY_WRITE_POLICY` and `SKILL_PUBLISH_POLICY` | Allow, ask, or block, a category, and a sentence for the user (`low`; `classifier=` injectable) | The verdict is closed, the sentence is generation. The highest cost of error, and the content is untrusted | Jev: 7/8 plain, 8/8 as three named checks with the policy in the state, and none of 48 decisions unsafe **[V]**. Laya failed open | **Tightening only:** run beside the LLM guard and take the stricter verdict. Named checks can supply the category; the sentence stays generated or templated | Measure in the P5 teaching pass (C2's guard-agreement item); code later |
| `middlewares/finglish_output_middleware` | Nothing: detection is a regex, and the repair is generation | Code decides | n/a | **Not a candidate** | n/a |
| `nodes/memory_consolidation_node` | Conflicting or outdated facts, inside a generative rewrite | Implicit conflicts need inference, a documented weakness | Only `claude-sonnet-5` caught the implicit diet conflict ([EV-2026-09-19](../../evidence/EV-2026-09-19-consolidator-model-comparison/README.md)) **[R]** | **Not now.** Possibly a pre-screen for explicit duplicates, after a measurement | Parked |
| RAG rewrite, generate, and web answer; skill designer; three code-review chains | Generation | Writes text | n/a | **Not candidates** | n/a |
| Five DeepAgents agents | Model-directed control: which tool, when to stop | Replacing an agent's choice with a router changes the control model | n/a | **Compare, don't replace:** the question P6-C1 asks | P6-C1 |
| Approvals: every search (P1), `execute` (P4), the coordinator's unapproved shell | Whether a call needs a person | Tightening versus loosening decides (principle 4) | OpenRouter's gate and auto-approve recipes **[S]** | Gates with a review band where approval is the lesson; P6-B3 closes the shell with static rules plus approval | P8-B3/C1, P11-B1 |
| `LLMRegistry` tier choice | A static tier per call site | Per-request difficulty is a decision | Jev Router exists **[S]**; LiteLLM's routing study **[T]** | A routing contender when tiers are compared by measurement | P9-B2, E2 |

**What grading looks like today:** one sequential LLM call per retrieved document. At our
tiers' 1.3-2.2 s per call, a four-document question spends several seconds on grading alone.
A batched decision request measured about 0.45 s for six documents **[V]**. That contrast is
R2's natural opening demo.

## Roadmap consumers

| Stage | Decision | Pattern | Note |
| :--- | :--- | :--- | :--- |
| R1 | Citation support, one decision per claim and source | A batched `noul` per pair | The LLM does it in R1, and every decision is logged as future labels |
| R2 | Relevance grading; groundedness driving the reroute | Batch fan-out; draft, verify, escalate | **The first code consumer** |
| P5 teaching pass, C2 | Guard agreement | A tightening ensemble | Measurement only |
| P6-C1 | A deterministic workflow against a supervisor | Typed decisions as the workflow's branch conditions | Shows "code owns the control flow" against an agent loop |
| P7-A1, B2 | Per-field extraction with confidence; people review only ambiguous fields | Candidates, a `choice`, and "none"; a review band | Jev Lab's *Extract* recipe is this stage in miniature |
| P7-C3 | Prompt injection carried in documents | One signal among several | The red-team set doubles as the evidence gates need later |
| P8-A1, B1 | Ticket category, intents, urgency | `choice`, `noul`s, and a `score` in one request | The class's home ground |
| P8-B2 | Router against handoffs | A decider as a third router arm | Optional |
| P8-B3, C1 | Approval for sensitive actions; action permissions | A three-way gate with a review band | Loosening needs the red-team set |
| P8-C2, C3 | Labels; the calibrated cascade | As planned | DEC-004 |
| P9-B2 | Measured tier and cost choices | Difficulty routing as a contender | Optional |
| P11-B1 | Action proposals behind approval gates | A three-way gate | Needs the P8 evidence |
| P12-A1, C1 | Routing over typed contracts; the capability catalog | A `choice` with confidence and escalation | Compared against code routing |
| E1 | Eval datasets, the red-team suite | One labeled set per decision point | |
| E2 | Routing and policy services | Model routing; one telemetry stream for the control plane | |

## Where it doesn't belong

Teaching these is as important as teaching the fits:

- **The Finglish repair:** code detects the problem, and generation repairs it.
- **Consolidation, rewriting, answers, reports, review text, skill drafts:** all generation.
- **Counting, dates, and arithmetic:** code, always.
- **A security verdict as the only gate:** never.
- **Any decision without a labeled set:** not in production code.
