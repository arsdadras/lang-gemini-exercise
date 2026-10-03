# EV-2026-09-26-laya-all-checkpoints: All three Laya checkpoints on our 23 decision cases

| | |
| :--- | :--- |
| Status | current |
| Label | **[V]**: script, cases, and raw output in [`artifacts/`](artifacts) |
| Ran | 2026-09-26, research office |
| Question | Does the fine-tuned third checkpoint (`laya-typed-decisions`), which the first spike never loaded, make Laya meaningfully better on our cases? |
| Extends | [EV-2026-09-25-laya-zero-shot](../EV-2026-09-25-laya-zero-shot/README.md), which used only the router's automatic choice between the English and multilingual checkpoints |

## Setup

The earlier spike, rerun with **one checkpoint forced per run** (`model=` on every call):

- `typed-decisions` (ModernBERT-large, fine-tuned);
- `english`;
- `multilingual`.

The cases are the same 23, labeled before any run. Laya 0.3.20, CPU only, zero-shot, warm.

A correction to an earlier claim of mine: Laya does **not** have 9 GB of checkpoints. The
9.3 GiB figure is the maintainers' *peak RAM* with every checkpoint loaded. The three
checkpoints together take **2.3 GB** on disk.

## Results

The plain-`noul` variant, which is the setup that counted in the first spike:

| Group | typed-decisions | english | multilingual | glm-5.3 (LLM, earlier) |
| :--- | :---: | :---: | :---: | :---: |
| Relevance (6) | 5 | 5 | **6** | 6 |
| Groundedness (6) | **6** | **6** | 5 | 6 |
| Intent (3) | 2 | 2 | 1 | 3 |
| Guard (8) | **7** | 5 | 5 | 8 |
| **Total (23)** | **20** | 18 | 17 | 23 |
| Group p50 latency | 178-331 ms | 214-317 ms | **76-137 ms** | 1.5-2.2 s |

- **The A/B-label variant** was unstable. With it, `typed-decisions` scored 6/6 on relevance but
  3/6 on groundedness, answering "yes" to all six.
- **Intent and Finglish:** no checkpoint was reliable. `typed-decisions` and `english` answered
  "no" to everything; `multilingual` answered "yes" to everything, one at 1.00 confidence.
- **Guard:**
  - `typed-decisions` returned "ask" for the first time (2 of 3). It still turned the
    third-party fact into "allow", at 0.59.
  - `multilingual` guessed near 0.44-0.50 confidence, including a "block" on a harmless goal
    entry.

## Reading

- **Better, but not enough.** The fine-tuned checkpoint went from 18 to 20 out of 23, and the
  guard from 5 to 7 out of 8. It still fails open on one sensitive case. It never read intent,
  and Finglish in particular, correctly.
- **The routed setup is no better** than the best single checkpoint for a known task type.
- **Multilingual is two to three times faster** than the other two, but the least accurate.
- **No checkpoint reaches the LLM** (23/23). The gap is small on relevance and groundedness,
  and wide on the guard and on intent.

## Limits

- n = 23, one author: this shows direction, not rates.
- Zero-shot on our domain; no temperatures fitted.
- `typed-decisions` was fine-tuned on the maintainers' workflows (invoices, security, support,
  agent traces), not on ours.
