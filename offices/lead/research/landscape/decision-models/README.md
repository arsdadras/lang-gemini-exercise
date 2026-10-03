# Decision Models: Domain Overview

Part of the research office's [landscape](../../../../../archive/offices/research/README.md#how-its-organized). As of **2026-09-27**.
Labels: [V] verified here, [R] reconstructed, [S] primary source, [T] third-party, [C] vendor
claim.

What the class changes (the product, development, and learning loops), with the patterns:
[capabilities.md](capabilities.md). What people build, and eleven independent studies:
[ecosystem.md](ecosystem.md). How to design with it: [design-guide.md](design-guide.md). Our
position: [BR-003](../../briefs/BR-003-decision-points/README.md).

## What they are

A decision model reads a **state** (text, JSON, or a conversation) and answers **typed
questions** you define, returning each answer with probabilities from one forward pass. An LLM
writes its answer; a decision model picks one from a set you gave it. The industry label is
"System One model", after Kahneman's fast, intuitive System 1.

All current members share three question types **[S]**:

| Type | You define | You get back | Typical agent-system use |
| :--- | :--- | :--- | :--- |
| `choice` | labeled options | the chosen label, a probability per option, a confidence | routing, triage, intent, a policy verdict |
| `score` | ordered levels | an expected level (can be fractional), a probability per level, a confidence | urgency, severity, rubric grading |
| `noul` | a yes/no statement | P(true), and no confidence | relevance, groundedness, "is this a refund request?" |

Many questions travel in one request and are answered in parallel over the same state, so
adding a question adds little latency **[S]**.

## Against an LLM judge

| | LLM judge (this repo today) | Decision model |
| :--- | :--- | :--- |
| Output | Text parsed into a schema | Typed values by construction |
| How it fails | Malformed output, refusals, schema errors | Always well-formed; fails by being confidently wrong |
| Probabilities | Not native | Native, per option |
| Explanations | Can write a reason | Cannot; any user-facing reason comes from code or an LLM |
| Scope | Open-ended: drafting, rewriting, extraction | Closed-set questions only |
| Accuracy, like for like | Best measured | Mid-pack on hard many-class tasks; no study found a decision model more accurate than a good open LLM **[T]**. On our 23 narrow cases, Jev 22 against 23 **[V]** |
| Latency | 0.3-5.6 s across providers **[T]**; 1.3-2.2 s on our tiers **[V]** | 0.13-0.28 s hosted (Jev) **[T]**; 0.48 s end to end from here through OpenRouter (Jev) **[V]**; 0.2-0.4 s on our CPU (Laya) **[V]** |
| Cost per 1k decisions | $0.19-$2.48 **[T]** | $0.02-$0.07 hosted (Jev) **[T][V]**; self-hosted infrastructure only (Laya, Open-Jev) |
| Option limit | Hundreds **[T]** | Jev 255 (hard cap) **[T]**; Laya degrades beyond ~20 **[S]** |

Vendors advertise "40-200x faster". Like for like, the independent figures are about 25x
against default LLM settings and 1.2x against the fastest hosted LLM **[T]**.

"Cannot hallucinate" means the model cannot invent a *label*. It can still pick the wrong one
with high confidence, and our spike recorded one at 0.93
([EV-2026-09-25-laya-zero-shot](../../evidence/EV-2026-09-25-laya-zero-shot/README.md)).

## Calibration: the central claim, unproven

The class's value rests on **calibration**: a stated 0.8 should be right 80% of the time, so
code can act on the number.

- **Jev** trains for it (RLCD, reinforcement learning for calibrated decisions) but has
  published no reliability curve or ECE **[C]**.
  - The only independent check found it worst-calibrated of all contenders: ECE 0.246 against
    0.039-0.122 for LLMs **[T]**.
  - Yet its confidence can still *rank* errors below correct answers, which is what a threshold
    needs. OpenRouter's TweetTopic bands show it **[C]**, and so did one of our two question
    variants ([EV-2026-09-27](../../evidence/EV-2026-09-27-jev-openrouter/README.md#4-confidence-and-a-simulated-cascade))
    **[V]**.
- **Laya** ships over-confident and says so; fitting a temperature on held-out data from your
  own domain cut ECE from 0.466 to 0.081 in their tests **[S]**.
- **Confidence is not probability, and it isn't portable.**
  - Jev derives `confidence` from the distribution's shape **[S]**; Laya uses 1 − normalized
    entropy and warns that Jev thresholds don't transfer **[S]**.
  - In Jev's own docs, a `noul` and its negation summed to 1.19 **[S]**.

**Consequence:** every threshold is fitted per model version and question shape, on labeled
data from our own domain.

## The architecture it enables: the calibrated cascade

```
state ──► decision model ──► confidence ≥ threshold for this class? ──yes──► act
                                        │ no, or error
                                        ▼
                               LLM judge (or a human) ──► act
```

- **Per-class, asymmetric thresholds:** a wrong "allow" on a security decision costs far more
  than a wrong "ask", so the fast path may never grant it.
- **Fail-safe:** a decider error escalates; it never fails open.
- **Measured as a system:** combined accuracy, **coverage** at a fixed error budget (the share
  the fast path may decide alone), calibration, p50/p95 latency, and cost per 1k decisions.

Jev's docs call this "confidence-gated routing" **[S]**. The office plans it for P8-C3
(DEC-004).

## Weaknesses the whole class shares

1. **Literal reading and negation:** Jev's documented failure mode #1; Laya issue #377
   ("don't cancel" picked cancel at 0.9998) **[S]**.
2. **Adversarial content in the state** moves the answer, per both vendors; Laya scores 0.698
   on held-out prompt injections **[S]**. Never a security gate on its own.
3. **No arithmetic, counting, or date comparison:** keep those in code **[S]**.
4. **Context rot:** unrelated material in the state lowers accuracy; filter first **[S]**.
5. **Position and label bias:**
   - Jev changes 13% of answers when options are reordered (the worst LLM measured: 37%)
     **[T]**;
   - Laya's `noul` follows its `true`/`false` labels instead of the state (issue #156) **[S]**.
6. **English first.** No vendor tests Persian in Latin script (Finglish).
   - Laya routed it to its English checkpoint and got the one positive case wrong **[V]**.
   - Jev read all three Finglish and negation cases correctly, in both question variants
     **[V]**.

   Three cases prove little.
7. **Bluffing:** on unanswerable items, LLMs admitted uncertainty 97-100% of the time, Jev
   49.7% **[T]**.

## Members

| | [Jev](jev.md) | [Laya](laya.md) | [Open-Jev](open-jev.md) |
| :--- | :--- | :--- | :--- |
| Maker | TypeSafe AI | Convai Innovations | Zefan Cai, independent |
| Weights | Closed; hosted API only | Open, Apache 2.0 | Open adapters on pinned Qwen |
| Model | Undisclosed transformer | Encoder: ModernBERT-large 421M, mmBERT-base 322M | Qwen3.5 2B/9B, 27B v1.1, plus a decision head |
| Runs on | TypeSafe's servers | CPU or GPU, anywhere | Self-hosted; GPU in practice |
| First release | 2026-09-15 | 2026-09-18 | 2026-09 |
| Wire protocol | `/v1/systemone` (originated it) | `/v1/systemone` via `laya-serve` **[V]** | `/v1/systemone`, "partial" **[S]** |
| LangChain | Official `langchain-typesafe`, alpha; verified through OpenRouter **[V]** | Own wrapper; also works with `langchain-typesafe` **[V]** | Through the protocol |
| Access | TypeSafe key, or an OpenRouter key | Self-hosted | Self-hosted |
| Tested here | Yes, through OpenRouter | Yes | No (no GPU) |

Numbers compared on the same benchmark:

| Measure | Jev | Laya | Open-Jev | LLM |
| :--- | :--- | :--- | :--- | :--- |
| Banking77, 77-way (nibzard) **[T]** | 76.3% | n/a | n/a | glm-5.3 80.4%, gpt-oss-120b 81.3%, claude-haiku-4.5 75.7% |
| JevBench public 231 (Open-Jev's audit) **[S]** | 200 | n/a | 27B: 197, 9B: 179, 2B: 150 | n/a |
| ECE (nibzard) **[T]** | 0.246 | n/a | n/a | 0.039-0.122 |
| Our 23 decision cases **[V]** | 22/23, no unsafe guard error | 18/23 routed; 20/23 best checkpoint | untested | glm-5.3 23/23, flash-lite 22/23 |

Seen but not researched: "decider-4b v2" and "JevK5", which rank near Jev on JevBench **[T]**,
and GLiNER2.5, a local zero-shot encoder used as a baseline **[T]**.

## Also in this domain

- [capabilities.md](capabilities.md): what the class changes in software, its precursors, the
  published patterns, and its limits.
- [ecosystem.md](ecosystem.md): the 551-build catalog mapped, the harness and coding-agent
  builds, the framework integrations, and the independent studies.
- [langchain-integrations.md](langchain-integrations.md): how each member plugs into LangChain
  and LangGraph, read from source.
- [sources.md](sources.md): every source, with its type.
- Our position: [BR-003](../../briefs/BR-003-decision-points/README.md), which supersedes
  [BR-001](../../briefs/BR-001-decision-model-adoption/README.md).
- For agents designing an AI step:
  [design guide](design-guide.md).
