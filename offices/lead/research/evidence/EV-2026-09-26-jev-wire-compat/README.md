# EV-2026-09-26-jev-wire-compat: The official Jev LangChain client against a local Jev-compatible server

| | |
| :--- | :--- |
| Status | current |
| Label | **[V]**: script and raw output in [`artifacts/`](artifacts) |
| Ran | 2026-09-26, research session |
| Question | Without a TypeSafe key, can the official Jev integration run unchanged against another server that speaks Jev's `/v1/systemone` protocol? If so, the backend is a configuration choice |
| Cited by | [LangChain integrations](../../landscape/decision-models/langchain-integrations.md), [BR-001](../../briefs/BR-001-decision-model-adoption/README.md) |

## Setup

- **Client:** `langchain-typesafe[experimental]==0.0.1a3`, the official package in LangChain's
  own repo, with `langchain` 1.4.2 and `langchain-core` 1.6.5, in a scratch venv separate from
  the repo's. Configured as `TypeSafeClassifier(base_url="http://127.0.0.1:8791", api_key=<test key>)`;
  everything else default, including `model="jev-latest"`.
- **Server:** `laya-serve` from `laya[serve]==0.3.20`, CPU, English and multilingual
  checkpoints. Environment: `LAYA_HOST=127.0.0.1`, `LAYA_PORT=8791`, `LAYA_API_KEY=<test key>`.
- **Script:** [`compat_typesafe_laya.py`](artifacts/compat_typesafe_laya.py). The middleware
  checks call `wrap_tool_call` directly with a constructed `ToolCallRequest`; there is no agent
  loop.

## Results

8 of 8 checks pass ([`results_compat.json`](artifacts/results_compat.json)):

| Check | Outcome | Time |
| :--- | :--- | ---: |
| `invoke`: string state, one `noul` + one `choice` + one `score` | refund P = 0.79; department `billing`, confidence 0.80; urgency 1.74. The response names `laya-rl-agent` as the model and counts 129 input tokens | 592 ms |
| `invoke`: a list of LangChain messages as the state | Same decisions; 252 input tokens | 535 ms |
| `ainvoke` | Identical to the sync call | 369 ms |
| `batch` of 2 | A billing ticket → `billing`; a crash report → `technical` (confidence 0.41, refund P = 0.12) | 671 ms |
| Wrong API key | `TypeSafeAuthenticationError`, 401 | 16 ms |
| A `choice` with 300 options | `TypeSafeUnprocessableEntityError`, 422 | 13 ms |
| `AutoModeMiddleware`: `delete_all_files("/")`, which the user never asked for | Blocked: error `ToolMessage`, tool not run | 424 ms |
| `AutoModeMiddleware`: `read_file("notes.txt")`, which the user asked for | Executed | 391 ms |

## Reading

- **The protocol is shared in practice:** the official client needs no change to talk to a
  non-TypeSafe backend, and `response.model` tells logs which backend decided.
- **Typed errors survive the swap:** the server's 401 and 422 arrive as the client's typed
  errors, which subclass LangChain's model errors.
- **The experimental tool-risk middleware** works end to end on a compatible backend. Its design
  limits (threshold fixed at 0.5, it blocks rather than asks a human) are the client's, not the
  backend's.
- **Seen along the way:**
  - the client prints a beta warning (`LangChainBetaWarning: ... API may change`);
  - `laya-serve` binds `0.0.0.0` unless `LAYA_HOST` is set (an earlier start hit a port
    conflict on that address), and requires no authentication unless `LAYA_API_KEY` is set.

## Limits

- This verifies **mechanics**, not decision quality: Laya's answers say nothing about Jev's.
- Hosted Jev (no key) and Open-Jev (no GPU; it calls its compatibility "partial") weren't
  tested, so wire-level differences could still show up there.
- The middleware was exercised directly, on two scenarios, with no agent loop.

## Re-running

In a venv with `laya[serve]==0.3.20` and `langchain-typesafe[experimental]==0.0.1a3`:

1. Start the server:
   `LAYA_HOST=127.0.0.1 LAYA_PORT=8791 LAYA_DEVICE=cpu LAYA_MODELS=english,multilingual LAYA_API_KEY=local-test-key laya-serve`.
2. Wait until `GET http://127.0.0.1:8791/health` lists both checkpoints.
3. Run `python compat_typesafe_laya.py`.
4. Stop the server.
