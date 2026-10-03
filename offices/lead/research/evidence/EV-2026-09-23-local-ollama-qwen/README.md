# EV-2026-09-23-local-ollama-qwen: Qwen3.5 2B and 4B on local Ollama, through our model registry

| | |
| :--- | :--- |
| Status | current |
| Label | **[V]**: script and raw output in [`artifacts/`](artifacts) |
| Ran | 2026-09-23, model-catalog session |
| Question | Is the `local` tier usable for this repo's structured-output and tool-calling calls, and which of the two pulled models should be its primary? |
| Cited by | [ADR-0015](../../../../../docs/adr/0015-local-tier-and-test-mode-profiles.md) (tier order and opt-in status), `src/agentlab/configs/models_config.py` (`local` tier comment), [BR-002](../../briefs/BR-002-model-catalog-evidence-map/README.md) |

## Setup

- **Server:** `ollama serve` on `127.0.0.1:11434`, this machine; no GPU offload confirmed.
- **Models** (as `ollama` reported them):

  | Model | Parameters | Quantization | Context |
  | :--- | :--- | :--- | :--- |
  | `qwen3.5:2b` | 2.3B | Q8_0 | 262k |
  | `qwen3.5:4b` | 4.7B | Q4_K_M | 262k |

  Both are listed with `tools` and `thinking` capabilities.
- **Path:** each model built through the repo's own `build_chat_model` from its
  `MODEL_TIERS["local"]` spec; no mocking.
- **Five checks per model, in order:**
  1. a one-word plain chat;
  2. `with_structured_output(GradeDocument)`, the RAG relevance schema;
  3. `with_structured_output(GuardVerdict)`, the security-guard schema, on a prompt-injection
     attempt;
  4. `with_structured_output(FinglishLines)`, a two-line Finglish repair;
  5. `bind_tools([add])` on "what is 17 plus 25?".

  Script: [`probe_local_ollama.py`](artifacts/probe_local_ollama.py). The content is exactly as
  run; only the file name changed, from `test_local_ollama.py`, so pytest can never collect it
  and fire live calls.

## Results

From [`artifacts/output.txt`](artifacts/output.txt):

| Check | `qwen3.5:2b` | `qwen3.5:4b` |
| :--- | :--- | :--- |
| Plain chat | OK, 139.2 s (first call: includes cold start) | OK, 23.4 s |
| `GradeDocument` | OK, 153.9 s, correct `yes` | OK, 91.8 s, correct `yes` |
| `GuardVerdict` | OK, 211.3 s, `block`, reasoned | OK, 109.6 s, `block`, better reasoned |
| `FinglishLines` | **FAIL** after 241.0 s: `OutputParserException: Invalid json output` | OK, 356.9 s, correct: `salam chetori?`, `khoobam merci` |
| `bind_tools` | OK, 7.9 s, `add(a=17, b=25)` | OK, 11.4 s, `add(a=17, b=25)` |

## Reading

- **Both models work end to end** through the registry: chat, structured output, and tool calls.
- **`qwen3.5:4b` is the more reliable one.** It was the only one to produce valid JSON for the
  multi-line schema; the 2B failed there but handled single-field schemas.
- **Structured output is the slow path:** 90-360 s per call, even warm, while a bare tool
  call returned in 8-11 s. The most likely cause is CPU-bound generation plus the models'
  reasoning ("thinking") tokens before the answer. It was not isolated.
- At this latency the tier is far too slow for any interactive call site. That's a technical
  property of this hardware and serving path, not a verdict on the models' quality.

## Limits

- One run per check, no repeats: this shows direction, not rates.
- The cause of the slowness is inferred: GPU use wasn't checked, and thinking mode wasn't
  disabled to compare.
- It says nothing about these models behind a GPU or through another server.

## Re-running

1. Start `ollama serve` with both models pulled.
2. From the repo root: `uv run python -u offices/lead/research/evidence/EV-2026-09-23-local-ollama-qwen/artifacts/probe_local_ollama.py`.
3. The script builds models from the repo's current `MODEL_TIERS["local"]`, so a changed
   catalog changes what it tests.
