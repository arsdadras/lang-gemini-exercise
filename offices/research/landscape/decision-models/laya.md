# Laya (Convai Innovations)

[Decision models](README.md) › Laya. As of **2026-09-26**, version **0.3.20**. Our own runs are
evidence records, linked below. Labels: [V] verified here, [S] primary source, [T] third-party.

## At a glance

| | |
| :--- | :--- |
| What | An open, non-autoregressive decision engine. It answers `choice`, `score`, and `noul` in one forward pass, as an open take on Jev's idea **[S]** |
| Maker | Convai Innovations; the maintainer is NandhaKishorM. Apache 2.0 **[S]** |
| Where | `github.com/NandhaKishorM/laya`, PyPI `laya`, Hugging Face `convaiinnovations/*`. The PyPI metadata matches the repo and the Hub organization (checked 2026-09-25) **[S]** |
| Maturity | Repository created **2026-09-18**; 28 PyPI releases in its first week; about 23.9k stars, 2k forks, and 121 open issues on 2026-09-25 **[S]** |
| Ways to run | Python SDK, CLI, HTTP server (`laya-serve`, on Jev's wire protocol), MCP server, Docker, ONNX. Runs on CPU, CUDA, Apple, and Intel XPU **[S]** |

## Checkpoints

A pure-Python `Router` detects the script and language in under 0.5 ms and picks a checkpoint.
Latin-script text in a language it can't identify goes to the English checkpoint, Finglish
included **[S][V]**.

| Checkpoint | Encoder | Params | Default context | For |
| :--- | :--- | ---: | :--- | :--- |
| `laya` | ModernBERT-large | 421M | 512 tokens (~320 left for the state) | English |
| `laya-multilingual` | mmBERT-base | 322M | 1,024 (up to 8,192; accuracy varies past ~4,000) | 100+ languages |
| `laya-typed-decisions` | ModernBERT-large | 421M | 1,024 | Fine-tuned on the maintainers' typed-decisions benchmark |

## What the maintainers measured

Source: README and `BENCHMARKS.md` **[S]**. Their Jev figures are third-party published, not
their own runs.

- **Latency.** On a T4 GPU, one question takes 32.8 ms (multilingual) or 39.5 ms (English). On
  CPU, 193-464 ms per request; per question, about 600 ms on the English checkpoint and 185 ms
  on multilingual.
- **Zero-shot is weak.** On typed decisions, the base checkpoints score 0.362 (English) and 0.352
  (multilingual), below the 0.461 majority-class baseline. The fine-tuned checkpoint reaches
  0.766 (Jev's published score: 0.727). Their own summary: *"a fast base to specialise, not a
  zero-shot decision engine."*
- **Standard tasks.** AG News 0.947, BoolQ 0.830, DAIR Emotion 0.573 (English checkpoint).
- **Safety tasks.**
  - Held-out prompt injections: 0.698 English, 0.578 multilingual.
  - Jailbreaks: 0.708-0.762.
  - Toxic-chat moderation: 0.530, "barely above chance".
- **Ordinal questions** (`score`) are the weakest type: SST-5 0.372.
- **Persian.** On 20-way MASSIVE intent (random 0.05): 0.140 English, 0.390 multilingual.
- **Calibration.** Over-confident as shipped. Fitting temperatures on held-out data lowers ECE
  from 0.466 to 0.081. `laya-multilingual` ships with no fitted temperatures at all.
- **Many options.** On Banking77 (77 labels) it scores 0.425 against Jev's 0.870. The option
  labels share a 192-256-token budget and get truncated beyond about 20 options.

## Known bugs

From the maintainers' "honest limits" section and issue tracker **[S]**:

| Issue | Behavior |
| :--- | :--- |
| #156 | `noul` follows its `true`/`false` labels instead of the state, worst on English. The workaround overrides `labels` |
| #377 | Negated requests trigger the action: "don't cancel" chose `cancel_account`, once at 0.9998 |
| #131 | `laya-multilingual` rarely picks the first-listed `score` level |
| #185 | `act_probability` carries no usable signal (AUROC 0.30) |
| (limits) | Boolean words used as `choice` keys are followed instead of the option descriptions |

## Operating facts

What we observed while running it **[V]**:

- **Network exposure.** `laya-serve` binds `0.0.0.0` unless `LAYA_HOST` is set, and requires no
  authentication unless `LAYA_API_KEY` is set. It ignores `--help` and starts the server. A
  production deployment needs both variables plus a network policy.
- **Calibration warning.** The English checkpoint loads with a warning that some shipped
  temperatures are invalid and clamped to 0.5. By the tool's own admission, confidence on those
  buckets is uncalibrated.
- **Footprint.**
  - A 685 MB virtualenv (torch 2.14 CPU, transformers 5.17);
  - about 3 GB of checkpoints, which took about 17 minutes to download here the first time;
  - up to 9.3 GiB RSS with every checkpoint loaded **[S]**.

## Our runs

- [EV-2026-09-25-laya-zero-shot](../../evidence/EV-2026-09-25-laya-zero-shot/README.md):
  18/23 on our cases, and the memory guard never answered "ask".
- [EV-2026-09-26-jev-wire-compat](../../evidence/EV-2026-09-26-jev-wire-compat/README.md):
  `laya-serve` answered the official Jev LangChain client unchanged, 8 of 8 checks.

## For this repo

Our position is in [BR-001](../../briefs/BR-001-decision-model-adoption/README.md). In short:

- **Strengths:**
  - open weights, self-hosted, Apache 2.0 (the state never leaves our infrastructure);
  - speaks Jev's protocol;
  - can be fine-tuned and calibrated on our labels;
  - works on CPU;
  - unusually candid documentation.
- **Concerns:**
  - it measured worse on our cases, and in the dangerous direction for the guard;
  - Finglish reaches the wrong checkpoint;
  - zero-shot is weak by its own benchmark;
  - a week old, with a release roughly every six hours and open bugs in all three question
    types;
  - its value depends on labeled data that P8-C2 is planned to produce.
