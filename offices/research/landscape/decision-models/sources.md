# Sources: Decision Models

[Decision models](README.md) › sources. Accessed 2026-09-23 to 27. **[S]** means a primary
source (official docs or the package's own source), **[T]** a third-party measurement or
report, and **[C]** vendor or partner marketing. *Summary* marks pages read through a
summarizing fetch rather than line by line.

## Jev through OpenRouter (2026-09-27)

Read as raw markdown via OpenRouter's [docs index](https://openrouter.ai/docs/llms.txt), unless
marked.

| Source | Type | Used for |
| :--- | :--- | :--- |
| [Jev documentation hub](https://openrouter.ai/docs/guides/community/jev.md) | [S] | The two API surfaces, context length, billing, FAQ |
| [Jev tutorial](https://openrouter.ai/docs/guides/community/jev-tutorial.md) | [S] | Request and response shapes, run-to-run variation, threshold advice |
| [TypeSafe SDK on OpenRouter](https://openrouter.ai/docs/guides/community/typesafe-sdk.md) | [S] | Base URL, model-ID mapping, the `models.list()` incompatibility |
| API reference: [System One](https://openrouter.ai/docs/api/api-reference/systemone/submit-a-system-one-request.md), [Decisions](https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-request.md) | [S] | Endpoints and error statuses |
| Cookbooks: [gate tool calls](https://openrouter.ai/docs/cookbook/building-agents/gate-tool-calls-with-jev.md), [verified cascade](https://openrouter.ai/docs/cookbook/evaluate-and-optimize/jev-verified-cascade.md), [classify at scale](https://openrouter.ai/docs/cookbook/evaluate-and-optimize/jev-classification.md), [auto-approve permission prompts](https://openrouter.ai/docs/cookbook/coding-agents/auto-approve-permission-prompts-with-jev.md) | [S] for the patterns, [C] for the results | The published patterns and their captured results |
| [Jev Lab](https://openrouter.ai/labs/jev), with the triage, overseer, extract, and compile recipes' code, read in a browser | [S] | Batch fan-out, oversight checks, extraction without guessing, compile-then-run |
| [OpenRouter models API](https://openrouter.ai/api/v1/models) | [S] | `typesafe/jev-router` and its description |
| [shipwithjev.com](https://www.shipwithjev.com/) | [T] *summary* | The community catalog: 551 builds, categories, "not affiliated" |
| [OpenRouter LangChain guide](https://openrouter.ai/docs/guides/community/langchain) | [S] *summary* | `langchain-openrouter`'s `ChatOpenRouter`; no Jev content |
| [`langchain-typesafe` on PyPI](https://pypi.org/pypi/langchain-typesafe/json) | [S] | Latest release and requirements, on 2026-09-27 |

## The wider sweep (2026-09-27)

Added when the dossier was redone. The LangChain posts, the TypeSafe pages, and the catalog were
read in full or in a browser; the rest were read through a summarizing fetch.

| Source | Type | Used for |
| :--- | :--- | :--- |
| LangChain, [*Building a harness with Jev*](https://www.langchain.com/blog/building-a-harness-with-jev) (2026-09-17) | [S] for the API, [C] for claims | The agent-loop framing; model routing and auto-mode middlewares; early builds |
| LangChain, [*Building prod with Jev and LangGraph*](https://www.langchain.com/blog/building-prod-with-jev-and-langgraph) (2026-09-25) | [S]/[C] | "Prod, not god"; the three architectures; the litigation graph; the unbundling of judgment; Stagehand |
| LangChain, [*Jev as an agent evaluator in LangSmith*](https://www.langchain.com/blog/jev-agent-evals-langsmith) (2026-09-20) | [C] *summary* | Agreement, variance, and cost against three LLM judges on five traces |
| [TypeSafe manifesto](https://typesafe.ai/manifesto); [*Introducing System One models and Jev*](https://typesafe.ai/blog/introducing-system-one-models-and-jev) | [C] *summary* | Positioning, RLCD, vendor benchmarks |
| TypeSafe docs, every page in the [index](https://docs.typesafe.ai/llms.txt) on 2026-09-27: patterns, 20 cookbooks, the use-case map, *Jev with coding agents*, the agent skill | [S] for the method, [C] for the results | Decision shapes, patterns, cookbook results, the official skill |
| [Browserbase, *What is Jev*](https://www.browserbase.com/blog/what-is-jev) | [T] *summary* | Stagehand's candidate-menu design and latency |
| [shipwithjev.com](https://www.shipwithjev.com/): all 551 build pages (sitemap), the guides, the blog index, and the *Jev use cases*, *review*, *limitations*, *AI grading*, and *Jev for developers* posts | [T] | The ecosystem map; Jev engineering; education and developer uses |
| Langfuse, [*Using TypeSafe's Jev for evals*](https://langfuse.com/blog/2026-09-18-using-typesafes-jev-for-evals) | [T] *summary* | The native evaluator; 91.5% agreement; cost per million verdicts |
| [beri.net on decomposition and shadow evals](https://www.beri.net/article/typesafe-jev-typed-decision-model-calibration-decomposition-shadow-eval) | [T] *summary* | 62.6% → 95.0%; out-of-distribution calibration |
| Independent repositories: [jev-decision-benchmarks](https://github.com/baibizhe/jev-decision-benchmarks), [jev-eval](https://github.com/4esv/jev-eval), [jev-evaluation](https://github.com/willkelly/jev-evaluation), [jev-acento](https://github.com/marcosmartinez/jev-acento); plus jev-rerank-bench, jev-orderby-bench, Jev-vs-ML, and jev-behavior-study, via their catalog pages | [T] | [ecosystem.md](ecosystem.md#independent-studies) |
| YouTube: *7 Jev Repos That 10x Claude Code* (AI Edge, 15 min); *Master ALL Jev Design Patterns* (The AI Automators, 2026-09-25, 14 min) | [T], title, description, and chapters only | Where attention is (coding-agent add-ons; decision types, shapes, and patterns). The transcripts couldn't be loaded without signing in, so nothing specific is cited from them |

## Background: the ideas' precursors

Cited in [capabilities.md](capabilities.md#what-is-new-and-what-isnt). The two linked papers
were confirmed by search on 2026-09-27; the others are standard references, cited without
re-reading.

| Work | Used for |
| :--- | :--- |
| Chen, Zaharia, and Zou, [FrugalGPT](https://arxiv.org/abs/2305.05176) (2023) | LLM cascades |
| Ong et al., [RouteLLM](https://arxiv.org/abs/2406.18665) (ICLR 2025) | Learned routing between a strong and a weak model |
| Yin, Hay, and Roth, "Benchmarking Zero-shot Text Classification" (EMNLP 2019) | NLI-based zero-shot classification |
| Inan et al., "Llama Guard" (2023) | Guard models with a fixed taxonomy |
| Viola and Jones, "Rapid Object Detection using a Boosted Cascade of Simple Features" (CVPR 2001) | The cascade idea |
| Geifman and El-Yaniv, "Selective Classification for Deep Neural Networks" (NeurIPS 2017) | Abstention and coverage |
| Guo et al., "On Calibration of Modern Neural Networks" (ICML 2017) | ECE and temperature scaling |
| Kahneman, *Thinking, Fast and Slow* (2011) | The System 1 and System 2 names |

## Jev

| Source | Type | Used for |
| :--- | :--- | :--- |
| [docs.typesafe.ai](https://docs.typesafe.ai/): Models, API, *Jev 1.13 jaggedness*, Confidence, Legal, *Jev with coding agents*, *How to build with System One*, *Confidence-gated routing*, cookbooks, read as raw markdown via its [index](https://docs.typesafe.ai/llms.txt) | [S] | Limits, pricing, rate limits, languages, data policy, failure modes, confidence semantics, the three architectures, decomposition, patterns |
| [`langchain-typesafe` 0.0.1a3](https://pypi.org/project/langchain-typesafe/), wheel source | [S] | Everything source-level in [langchain-integrations.md](langchain-integrations.md) |
| [LangChain's TypeSafe integration page](https://docs.langchain.com/oss/python/integrations/providers/typesafe) | [S] *summary* | Package, classes, environment variables |
| [LangChain blog: *Building a harness with Jev*](https://www.langchain.com/blog/building-a-harness-with-jev) (2026-09-17) | [C] *summary* | Positioning and use cases |
| [Wikipedia: *Jev (AI model)*](https://en.wikipedia.org/wiki/Jev_(AI_model)) | [T] *summary* | Company, founders, funding, the vendor's claims |
| [nibzard/decision-model-benchmark](https://github.com/nibzard/decision-model-benchmark), v2 | [T] | Accuracy against 8 LLMs, calibration, bluffing, position bias, the 255-option cap, latency, cost |
| [AbdelStark/jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks), BTZSC pilot | [T] | Accuracy against GLiNER2.5, zero-probability failures, coverage at an error budget |
| [LiteLLM: Jev auto-router benchmark](https://docs.litellm.ai/blog/jev-auto-router-benchmark) | [T] *summary* | Routing agreement, latency and cost against Haiku |
| [Context Studios: Jev measured independently](https://www.contextstudios.ai/blog/jev-measured-92-214-ms-per-decision-under-1-cent-per-8-requests) | [T] *summary* | Latency waves; why 200x becomes about 25x |
| [Benchmark Heaven: JevBench](https://benchmarkheaven.com/jev-models) | [T] *summary* | Jev-class ranking; the sealed-tier gap |
| Web-search summaries of the Hacker News launch thread, [KDnuggets](https://www.kdnuggets.com/what-everyone-is-getting-wrong-about-typesafe-ais-jev), [agentpedia](https://agentpedia.codes/blog/jev-system-one-models), [AgentConn](https://agentconn.com/blog/jev-typesafe-new-agent-layer-if-calibration-holds/), [Tom's Hardware](https://www.tomshardware.com/tech-industry/artificial-intelligence/typesafe-ais-jev-offers-an-alternative-to-llms-that-claims-to-be-193x-faster-and-445x-cheaper-system-one-type-model-is-bespoke-for-probabilistic-decision-making), [MarkTechPost](https://www.marktechpost.com/2026/09/19/typesafe-ai-releases-jev/) | [T] *summary* | Reception and criticism |
| [Forbes: Vercel and Cloudflare add Jev](https://www.forbes.com/sites/josipamajic/2026/09/19/jev-cuts-ai-decision-costs-100x-and-vercel-cloudflare-rushed-to-add-it/) | [T] headline only (HTTP 403) | Ecosystem adoption |
| [PromptEngineer48/langchain-jev-tutorial](https://github.com/PromptEngineer48/langchain-jev-tutorial) | [T] | A community example; not read in depth |

## Laya

| Source | Type | Used for |
| :--- | :--- | :--- |
| [NandhaKishorM/laya](https://github.com/NandhaKishorM/laya): README, `BENCHMARKS.md`, `laya/integrations/langchain.py`, `laya/serve.py`, read directly | [S] | Checkpoints, benchmarks, known bugs, integration classes, server settings |
| [`laya` on PyPI](https://pypi.org/project/laya/) | [S] | Authorship check, release history |
| [Laya docs site](https://nandhakishorm.github.io/laya/): overview, LangChain, reference | [S] *summary* | First orientation; superseded by the repository reads |

## Open-Jev

| Source | Type | Used for |
| :--- | :--- | :--- |
| [Zefan-Cai/Open-Jev](https://github.com/Zefan-Cai/Open-Jev): README and `docs/provider-comparison.md`, read directly | [S] | Models, serving, audited results, latency |
| [openjev.com](https://openjev.com/), read in a browser | [S] | Confirmed to be the unrelated "SemIf" demo |
