# Open-Jev (Zefan Cai)

[Decision models](README.md) › Open-Jev. README read 2026-09-23; status checked 2026-09-26.
Labels: [V] verified here, [S] primary source, [T] third-party.

## At a glance

| | |
| :--- | :--- |
| What | An independent open-weight implementation inspired by Jev. A Qwen base model plus a trained decision head returns typed probabilities **[S]** |
| Where | `github.com/Zefan-Cai/Open-Jev`; models under `ZefanCai/` on Hugging Face **[S]** |
| Models | Open-Jev-2B and 9B (LoRA adapters on Qwen3.5-2B/9B) and Open-Jev-27B-v1.1. Each package holds an adapter, a scalar decision head, and a calibration temperature. The base Qwen weights aren't included; they are pinned by revision **[S]** |
| Serving | `python -m jev.server --model Qwen/Qwen3.5-2B --revision <sha>` listens on `127.0.0.1:8791` and serves `POST /v1/systemone`, which it calls partially compatible with Jev. Docker images exist for the 2B, on GPU or CPU **[S]** |
| Needs | Python 3.10+ and a Linux-first GPU workflow. The 9B fits one 16 GB card in bf16 **[S]** |
| Not to confuse with | `openjev.com`, now "SemIf (formerly OpenJev)", an unrelated browser-only demo with no backend **[V]** (checked 2026-09-23) |

## What its authors measured

From the project's own audited reports **[S]**:

| Model | JevBench public (231) | Hard tier (111) |
| :--- | ---: | ---: |
| Open-Jev-2B | 150 (64.9%) | 46 (41.4%) |
| Open-Jev-9B | 179 (77.5%) | 66 (59.5%) |
| Open-Jev-27B-v1.1 | 197 (85.3%) | 80 (72.1%) |
| Jev 1.13, their run | 200 (86.6%) | 81 (73.0%) |

- **Latency.** On a short request, the 2B answers locally at a median of 85 ms, against 295 ms
  for Jev over HTTPS. At 1,024 state tokens and 32 options it takes 1,016 ms, against Jev's
  301 ms. The two ran on different hardware.
- **Reported weak spots.**
  - Browser-snapshot actions: the 2B scores below an "always BLOCKED" baseline.
  - Drone control, Wiki navigation, and some customer-workflow judgments.
  - Several evaluations are still pending.
- **Benchmark Heaven [T]** gives the 2B and 9B low composite scores (10.0 and 11.2), mostly on
  the speed and cost axes as served there.

## For this repo

- It is a **decoder** (Qwen) with a decision head, heavier than Laya's encoders and GPU-bound in
  practice.
- **Hardware:** we have no confirmed GPU. Qwen3.5 on our CPU took 90-360 s per structured call
  on a different serving path
  ([EV-2026-09-23-local-ollama-qwen](../../evidence/EV-2026-09-23-local-ollama-qwen/README.md)).
- **Scope:** its checkpoints are fine-tuned research artifacts, and training neural models is
  outside the curriculum (DEC-004).
- **Why it matters anyway:** it speaks the same protocol, so it could become a third backend
  behind one client if a GPU appears
  ([BR-001](../../briefs/BR-001-decision-model-adoption/README.md)).
