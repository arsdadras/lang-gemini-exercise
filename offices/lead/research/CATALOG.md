# Catalog

Back to the [lead office](../README.md). This record was the research office's until 2026-10-03, when the role was folded into the lead ([ADR-0025](../../../docs/adr/0025-two-roles-lead-and-mentor.md); the old charter is [archived](../../../archive/offices/research/README.md)). **The one index of everything here.** Every record
appears once, with a stable ID or path. Updated whenever a record is added or its status
changes. As of 2026-09-27.

## Landscape

Living pages, edited in place. Each carries its "as of" date.

| Domain | Page | Covers | As of |
| :--- | :--- | :--- | :--- |
| decision-models | [README.md](landscape/decision-models/README.md) | What decision models are; the comparison with LLM judges; calibration; the cascade pattern; weaknesses the class shares; members side by side | 2026-09-27 |
| decision-models | [capabilities.md](landscape/decision-models/capabilities.md) | Judgment unbundled; the product, development, and learning loops; where decisions sit in a harness; capabilities with evidence; patterns; Jev engineering; limits; hype check | 2026-09-27 |
| decision-models | [ecosystem.md](landscape/decision-models/ecosystem.md) | What people build with Jev: the 551-build catalog mapped, harness and coding-agent builds, framework integrations, evaluation uses, eleven independent studies | 2026-09-27 |
| decision-models | [design-guide.md](landscape/decision-models/design-guide.md) | Guidance for any role designing an AI step: finding decision points in three loops, the backend rubric, Jev engineering, recurring policies, calling Jev here. Proposed as a library entry (the lead's call) | 2026-09-27 |
| decision-models | [jev.md](landscape/decision-models/jev.md) | TypeSafe's Jev: access through OpenRouter, API, limits, pricing, data policy, failure modes, measurements (ours included), reception | 2026-09-27 |
| decision-models | [laya.md](landscape/decision-models/laya.md) | Laya 0.3.20: checkpoints, the maintainers' benchmarks, known bugs, operating facts | 2026-09-26 |
| decision-models | [open-jev.md](landscape/decision-models/open-jev.md) | Open-Jev: models, serving, audited results | 2026-09-26 |
| decision-models | [langchain-integrations.md](landscape/decision-models/langchain-integrations.md) | `langchain-typesafe` and Laya's integration, read from source; the OpenRouter path; the dependency check; the shared protocol | 2026-09-27 |
| decision-models | [sources.md](landscape/decision-models/sources.md) | Every source used for the domain, with its type; background papers | 2026-09-27 |

## Evidence

Immutable records. **[V]** verified here with artifacts; **[R]** reconstructed from earlier
prose.

| ID | Label | Status | Question, and the answer in one line |
| :--- | :-: | :--- | :--- |
| [EV-2026-08-26-gapgpt-model-ids](evidence/EV-2026-08-26-gapgpt-model-ids/README.md) | R | partial | Were the catalog's IDs checked against the gateway? Six carried from this check; the others never were |
| [EV-2026-09-17-finglish-line-repair](evidence/EV-2026-09-17-finglish-line-repair/README.md) | R | current, model since changed | How much does line-level repair cut Perso-Arabic leakage? 215 → 55 lines; a whole-answer rewrite was worse |
| [EV-2026-09-17-memory-gate-spikes](evidence/EV-2026-09-17-memory-gate-spikes/README.md) | R | current | Where can a memory write be both approved and refused? In the storage backend, via `interrupt()`; a resume re-runs the tool |
| [EV-2026-09-19-hot-path-memory-writes](evidence/EV-2026-09-19-hot-path-memory-writes/README.md) | R | current | Does in-conversation memory writing keep the profile accurate? No: conflicts, duplicates, stale and missing facts after 6 conversations |
| [EV-2026-09-19-consolidator-model-comparison](evidence/EV-2026-09-19-consolidator-model-comparison/README.md) | R | current, **inconsistent** | Which model catches conflicting facts? `claude-sonnet-5`; its two records don't agree on the numbers |
| [EV-2026-09-22-interrupt-resume-order](evidence/EV-2026-09-22-interrupt-resume-order/README.md) | R | current | How are resume values matched to `interrupt()` calls? By order within a node, so skipping one misroutes answers |
| [EV-2026-09-23-p5-eval-lite](evidence/EV-2026-09-23-p5-eval-lite/README.md) | R | current, catalog since changed | Do real models meet P5's assumptions? 13/13 scenarios, one run |
| [EV-2026-09-23-local-ollama-qwen](evidence/EV-2026-09-23-local-ollama-qwen/README.md) | V | current | Is local Qwen via Ollama usable here? It works end to end, the 4B is more reliable, and it's far too slow for interactive use |
| [EV-2026-09-25-laya-zero-shot](evidence/EV-2026-09-25-laya-zero-shot/README.md) | V | current | Laya zero-shot vs our LLM tiers on 23 cases: 18/23 vs 23/23; the guard never answered "ask" |
| [EV-2026-09-26-jev-wire-compat](evidence/EV-2026-09-26-jev-wire-compat/README.md) | V | current | Does the official Jev LangChain client work against another backend? Yes, 8/8 checks |
| [EV-2026-09-26-laya-all-checkpoints](evidence/EV-2026-09-26-laya-all-checkpoints/README.md) | V | current | All 3 Laya checkpoints on our 23 cases: fine-tuned `typed-decisions` 20/23 (guard 7/8), english 18, multilingual 17; LLM 23/23 |
| [EV-2026-09-27-jev-openrouter](evidence/EV-2026-09-27-jev-openrouter/README.md) | V | current | Jev through OpenRouter on our 23 cases, and the LangChain path: 22/23 in both question variants, no unsafe guard error, no label change over 3 runs, ~0.5 s and ~$0.00002 per decision; the client passed 11/11 checks |
| [EV-2026-09-27-jev-harness-decisions](evidence/EV-2026-09-27-jev-harness-decisions/README.md) | V | current | Jev on this repo's harness decisions against two LLM tiers: specialist routing 32/32 × 3 (LLMs 30/32), memory staleness 59/60 (LLMs 20/20, Jev unsure on implied changes), semantic lint of our conventions AUROC 1.0 on synthetic snippets (weak on syntax-level rules) |
| [EV-2026-10-05-claim-check-jev](evidence/EV-2026-10-05-claim-check-jev/README.md) | V | current | Jev on R1's claim-check seed set (34 cases): 91.2% accurate, 2 unsafe errors, both below the 0.8 threshold, which covers 85% of cases at 100% accuracy; p50 443 ms, $0.0006; the LLM half is pending (GapGPT unreachable) | 2026-10-05 | `evidence/EV-2026-10-05-claim-check-jev/` |
| [EV-2026-10-05-claim-check-flash-lite](evidence/EV-2026-10-05-claim-check-flash-lite/README.md) | V | current | Gemini 3.5 Flash-Lite (Google direct) on R1's claim-check seed set: 100% on 34 cases, 0 unsafe errors, p50 937 ms but p95 20 s (free-quota throttling); the LLM half of the Jev record | 2026-10-05 | `evidence/EV-2026-10-05-claim-check-flash-lite/` |
| [EV-2026-09-27-jev-ecosystem-map](evidence/EV-2026-09-27-jev-ecosystem-map/README.md) | V | current | What 551 cataloged Jev builds do: 53.9% of builds that use Jev work in agents' harnesses; 23.6% serve coding agents; 24.5% pair Jev with an LLM; 6.7% measure quality. Classified by Jev for $0.03, 80% agreement with a blind hand sample (19/19 at confidence ≥ 0.9) |
| [EV-undated-flash-lite-false-memory-claims](evidence/EV-undated-flash-lite-false-memory-claims/README.md) | R | current, possibly stale | Which low-tier model calls the memory tool reliably? `gpt-5.6-luna`; Gemini claimed writes it never made |

## Briefs

| ID | Status | Question, and the short answer |
| :--- | :--- | :--- |
| [BR-001-decision-model-adoption](briefs/BR-001-decision-model-adoption/README.md) | superseded by BR-003 | Should we adopt AI decision models? (2026-09-26: the pattern yes, at P8-C3; no member in today's call sites) |
| [BR-002-model-catalog-evidence-map](briefs/BR-002-model-catalog-evidence-map/README.md) | current | Which model choices in code rest on evidence? 3 on direct measurement, 5 partial, 3 on none, including the tier-ranking scores themselves |
| [BR-003-decision-points](briefs/BR-003-decision-points/README.md) | current, version 3 | What should decision models change in this repo, its development, and its teaching? Decision models as a second model family beside the LLM tiers, deciding a measured System-1 layer across the product, development, and learning loops; a Phase 1 retrofit of P1 to P5's decision points from R1; field-level structured output; tier selection at R2; utilities and compositional builds; one standard for every decision point; gates escalate, never approve. Version 3's verdicts on the user's second review: [second-review.md](briefs/BR-003-decision-points/second-review.md) |

## Outbox

Messages to other roles, in the protocol's format: [OUTBOX.md](../../../archive/offices/research/OUTBOX.md) (RS-001 to RS-020).
