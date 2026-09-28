---
title: Technology radar
maintainer: lead
status: current
updated: 2026-09-28
summary: Where each technology stands in this repo (adopt, trial, assess, hold), and the locked versions of the core stack.
related: [models.md, ../engineering/dependency-policy.md, ../architecture/decision-models.md]
---

# Technology Radar

Where each technology stands in this repo. How dependencies are added, pinned, and kept current:
the [dependency policy](../engineering/dependency-policy.md). Rings follow the usual radar meaning:

- **Adopt:** the default; use it for new work.
- **Trial:** in use where its risk is contained; widen only with evidence.
- **Assess:** worth learning about; a spike or a planned stage decides.
- **Hold:** don't start new uses.

Last reviewed: 2026-09-28.

## Frameworks and libraries

| Technology | Ring | Why | Record |
| :--- | :--- | :--- | :--- |
| LangChain 1.4, LangGraph 1.2, DeepAgents 0.7, LangSmith 0.14 | Adopt | The curriculum's subject | [ARCHITECTURE.md](../../offices/lead/ARCHITECTURE.md) |
| Pydantic 2 | Adopt | Typed contracts at every boundary | `AGENTS.md` convention 8 |
| `ModelFallbackMiddleware`, `HumanInTheLoopMiddleware`, `ToolRetryMiddleware` | Adopt | Built-ins before custom code | [ADR-0007](../../docs/adr/0007-built-in-model-fallback.md) |
| `langchain-typesafe` 0.0.1a3 (the Jev client) | Trial | Enters at R1 behind the `decision_model` seam as a recorded pre-release: the maintained LangChain client for the System One API; no call site imports it. Exit: its first non-alpha release, or an in-house client over `/v1/systemone` if it is still alpha at P8-C3 | [ADR-0021](../../docs/adr/0021-decision-models-as-a-second-model-family.md) |
| `PIIMiddleware` | Trial | Protects what a model sees; not persistence | [ADR-0010](../../docs/adr/0010-one-gate-in-memory-storage.md) |
| Custom retry middleware; agent registries without a consumer | Hold | Replaced by built-ins; speculative | [ADR-0007](../../docs/adr/0007-built-in-model-fallback.md), [ADR-0006](../../docs/adr/0006-remove-agent-registry.md) |

## Models and providers

| Technology | Ring | Why | Record |
| :--- | :--- | :--- | :--- |
| GapGPT gateway for `high`/`medium`/`low` (OpenAI, Anthropic, Gemini) | Adopt | One credential, three providers, fallback inside a tier | [ADR-0014](../../docs/adr/0014-weighted-model-tier-catalog.md) |
| `opensource` tier (GLM, Qwen, DeepSeek via GapGPT) | Trial | Low-stakes nodes only until structured output and tool calling are measured here | [ADR-0014](../../docs/adr/0014-weighted-model-tier-catalog.md) |
| `free` tier (Gemini Flash-Lite, Google direct) | Trial | Quota-limited; a fallback when the gateway is down | [ADR-0014](../../docs/adr/0014-weighted-model-tier-catalog.md) |
| `local` tier (Ollama, `qwen3.5:4b`) | Trial | Works, but 90-360 s per structured call on this machine; opt-in only | [ADR-0015](../../docs/adr/0015-local-tier-and-test-mode-profiles.md) |
| Encoder decision models (Laya) as a System-1 decider | Assess | A candidate local backend on the same protocol, for private state (the production path in ADR-0021). Zero-shot spike: 18/23, and all 3 security "ask" cases flipped to "allow"; the fine-tuned checkpoint scored 20/23 (guard 7/8); `laya-serve` binds all interfaces without authentication by default. Chosen by measurement when a local backend is needed | [DECISIONS.md](../../offices/lead/DECISIONS.md) DEC-004; `EV-2026-09-25-laya-zero-shot`, `EV-2026-09-26-laya-all-checkpoints`, `BR-001` |
| Hosted decision models over the shared protocol (Jev, `typesafe/jev-1.13`) | Trial | The first candidate at every decision point from R1, behind `decision_model`. Measured here through OpenRouter's System One API: 22/23 on our decision cases with no guard answer less strict than its label, routing 32/32 in three runs, about 0.45 s and $0.00002 per decision (`EV-2026-09-27-jev-openrouter`, `EV-2026-09-27-jev-harness-decisions`); the official client also works against other backends (`EV-2026-09-26-jev-wire-compat`). Independent results place Jev below `glm-5.3` on hard many-class accuracy and last on calibration, so thresholds are fitted per class on our labels | [ADR-0021](../../docs/adr/0021-decision-models-as-a-second-model-family.md), `BR-003` |
| OpenRouter's System One API (Jev's access path) | Trial | One key, billed per input token; the same protocol TypeSafe and local servers speak | [ADR-0021](../../docs/adr/0021-decision-models-as-a-second-model-family.md) |
| OpenRouter as an LLM gateway | Hold | One LLM gateway until a concrete need | [ADR-0014](../../docs/adr/0014-weighted-model-tier-catalog.md) |

## Infrastructure and tools

| Technology | Ring | Why | Record |
| :--- | :--- | :--- | :--- |
| `uv`, `ruff`, `pytest` | Adopt | Toolchain | `AGENTS.md` |
| GitHub Actions CI (ruff check and format, pytest, docs lint on every push) | Adopt | Development standard; live | DEC-005, DEC-016 |
| Dependabot (`uv` daily, Actions weekly) | Adopt | Keeps the stack current; native `uv` support | DEC-016 |
| SQLite checkpointer and store | Adopt | Teaching harness behind swappable interfaces | [ARCHITECTURE.md](../../library/architecture/standards.md#scale-seams) |
| Chroma (local) | Adopt | Local vector index for P2 | [ARCHITECTURE.md](../../library/architecture/standards.md#scale-seams) |
| LangSmith tracing | Adopt | Observability thread | [ADR-0004](../../docs/adr/0004-testing-and-evaluation-policy.md) |
| `LocalShellBackend` with an allow-listed env | Adopt | Sandbox for Term P | [ADR-0005](../../docs/adr/0005-sandbox-secret-isolation.md) |
| Postgres checkpointer and store | Assess | The production swap; enters with concurrency (Term E) | [ARCHITECTURE.md](../../library/architecture/standards.md#scale-seams) |
| LangSmith Sandboxes (microVM; DeepAgents `LangSmithSandbox` backend) | Assess | Real isolation for P4's shell; research evaluates it for R4 and E1 (LD-005) | [ADR-0005](../../docs/adr/0005-sandbox-secret-isolation.md), DEC-012 |
| LangSmith Context Hub (versioned contexts; DeepAgents `ContextHubBackend`) | Assess | Production context registry: E2, and one line in the P5 teaching pass. Not for repo docs | DEC-011 |
| LangSmith Engine (trace failures clustered into issues, fixes proposed) | Assess | P8-C2's feedback loop | DEC-012 |
| Managed Deep Agents | Assess | Hosted runs, P12-B3 | DEC-012 |
| LangSmith LLM Gateway (spend limits, sensitive-data detection) | Assess | E2's routing and policy service | DEC-012 |
| Agent Server | Assess | Async runs, P12-B3 | [ROADMAP.md](../../offices/lead/ROADMAP.md) |

## Techniques

| Technique | Ring | Record |
| :--- | :--- | :--- |
| Typed specialist envelope; single enforcement point; single writer; eval-lite; real-framework tests with a scripted model | Adopt | [ARCHITECTURE.md](../../library/architecture/standards.md#architecture-principles) |
| Decider-first decision points with LLM escalation (calibrated cascades) | Trial | From R1; at production scale at P8-C3 ([ADR-0021](../../docs/adr/0021-decision-models-as-a-second-model-family.md)) |
| Decision engineering: question design, decomposition, thresholds from error costs, labeled sets per decision point | Trial | From R1; its own stage, D1 ([ADR-0021](../../docs/adr/0021-decision-models-as-a-second-model-family.md)) |
| Hybrid retrieval (BM25 + vector + reranker) | Assess | R2, judged by its metrics (DEC-013) |
| Compiled knowledge: entity-relation graphs with provenance, LLM-maintained wikis, graph plus vector retrieval | Assess | P7-C2 (DEC-013) |
| LLM-wiki maintenance for shared docs (index, append-only log, lint) | Adopt | [`library/`](../README.md) (DEC-013) |
| Whole-file rewrites by a model; prompt-only safety rules; mocking the framework in tests | Hold | [ADR-0012](../../docs/adr/0012-memory-consolidation-single-writer.md), [ADR-0008](../../docs/adr/0008-memory-write-governance.md), [ADR-0004](../../docs/adr/0004-testing-and-evaluation-policy.md) |

## Current versions

Checked 2026-09-26 with `uv lock --upgrade --dry-run`: no drift.

| Package | Locked |
| :--- | :--- |
| `langchain` | 1.4.2 |
| `langchain-core` | 1.6.5 |
| `langgraph` | 1.2.12 |
| `deepagents` | 0.7.19 |
| `langsmith` | 0.14.1 |
| `langchain-openai` | 1.6.6 |
| `langchain-google-genai` | 4.4.0 |
| `pydantic` | 2.13.5 |

Exact versions live in `uv.lock`; this table is refreshed at each lead session's drift check.
