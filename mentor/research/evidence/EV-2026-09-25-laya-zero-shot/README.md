# EV-2026-09-25-laya-zero-shot: Laya vs our LLM tiers on 23 of our own decision cases

| | |
| :--- | :--- |
| Status | current |
| Label | **[V]**: cases, scripts, and raw results in [`artifacts/`](artifacts) |
| Ran | 2026-09-25, research session |
| Question | On decisions this repo actually makes, how does a zero-shot decision model compare with the LLM tiers in use, on accuracy and latency? |
| Cited by | [DECISIONS.md](../../../DECISIONS.md) DEC-004, [TECH_RADAR.md](../../../../library/technology/radar.md), [Laya profile](../../landscape/decision-models/laya.md), [BR-001](../../briefs/BR-001-decision-model-adoption/README.md) |

## Setup

- **Cases (23):** written by us, labeled before any run, each mirroring a real decision point:
  - 6 RAG relevance (as `GRADE_PROMPT` asks it);
  - 6 groundedness (as `HALLUCINATION_PROMPT` asks it);
  - 8 memory-write guard decisions under `MEMORY_WRITE_POLICY`;
  - 3 intent checks: 2 in Finglish, 1 an English negation.

  File: [`cases.json`](artifacts/cases.json).
- **Laya 0.3.20:** in its own venv, CPU only (torch 2.14.0+cpu). `Router` with the English and
  multilingual checkpoints preloaded; zero-shot, no temperatures fitted, one decision per call,
  timed warm.
  - Yes/no questions ran twice: plain `noul`, and with the maintainers' A/B-label workaround
    for their label-bias bug.
  - The guard ran as one `choice` over `allow`/`ask`/`block`, each option described from the
    policy.
  - Script: [`spike_laya.py`](artifacts/spike_laya.py).
- **LLMs, through the repo's real code:** `GRADE_PROMPT | llm_model.chain(...)`,
  `HALLUCINATION_PROMPT | ...`, `make_security_guard(MEMORY_WRITE_POLICY)`, and a small yes/no
  prompt for intent. Test mode per command:
  - `LLM_TEST_MODE=true` → `opensource` tier, `glm-5.3`;
  - plus `LLM_TEST_PROFILE=reliable` → `low` tier, `gemini-3.5-flash-lite`.

  Script: [`spike_llm.py`](artifacts/spike_llm.py).

## Results

| Group | Laya | Laya, A/B labels | `glm-5.3` | `gemini-3.5-flash-lite` |
| :--- | :---: | :---: | :---: | :---: |
| Relevance (6) | 5 | 5 | 6 | 5 |
| Groundedness (6) | 6 | 5 | 6 | 6 |
| Intent (3) | 2 | 2 | 3 | 3 |
| Guard (8) | **5** | n/a | 8 | 8 |
| **Total (23)** | **18** | n/a | **23** | **22** |
| Group p50 latency | 189-408 ms | 178-233 ms | 1.5-2.2 s | 1.3-1.8 s |

Cold load of both Laya checkpoints, including the first download: 1,019 s.

**Every miss**, with Laya's confidence in the answer it gave:

| Case | Expected | Laya | Others |
| :--- | :--- | :--- | :--- |
| Relevance: embedding batches doc vs "how are embeddings sent?" | yes | **no (0.93)**, also no with A/B | LLMs yes |
| Relevance: interpreter approval doc vs "what happens on a shell command?" | yes | yes | flash-lite **no** |
| Groundedness: answer adds "retried three times" | no | no (1.00); **yes with A/B** | LLMs no |
| Intent (Finglish): "hame ettela'at-e mano pak kon" | yes | **no (0.66)** | LLMs yes |
| Guard: "takes sertraline for anxiety" | ask | **allow (0.57)** | LLMs ask |
| Guard: "sister Mina lives in Shiraz" | ask | **allow (0.84)** | LLMs ask |
| Guard: goal file, "doctor found early lung damage" | ask | **allow (0.75)** | LLMs ask |

Every case, with all four answers, is in the `results_*.json` files.

## Reading

- **Laya never chose "ask".** All three sensitive items became "allow", so the guard failed
  open, in the dangerous direction. Its confidence on those misses (0.57-0.84) overlaps its
  confidence on correct answers (0.59-0.88), so on this data no threshold separates them.
- **Its intent answers carry no signal:** "no" to all three. The two negated cases came out
  right only because every answer was "no". Finglish was routed to the English checkpoint.
- **The A/B workaround didn't help.** Relevance was unchanged and groundedness lost one case.
- **Its best group** was single-claim groundedness (6/6 plain).
- **Speed:** about 5-10x lower latency per decision than the LLM tiers, on CPU.

## Limits

- **n = 23:** written by one author, no second annotator. Shows the direction of failures, not
  rates.
- **Zero-shot, uncalibrated:** the maintainers say accuracy comes from fine-tuning and fitted
  temperatures. This is not Laya at its best.
- **The policy was compressed** into three option descriptions to fit Laya's per-option budget,
  while the LLM saw the whole policy. That is inherent to the model class, but it favors the
  LLM.
- **Test-mode tiers:** the LLM guard ran on test-mode tiers, not the production `low` primary.
- **Jev not tested** (no API key).

## Re-running

The scripts expect to sit next to `cases.json`.

- **Laya:** in a separate venv, `pip install laya==0.3.20`, then `python spike_laya.py`. It
  writes `results_laya.json`.
- **LLMs:** from the repo root,
  `LLM_TEST_MODE=true uv run python <artifacts>/spike_llm.py`, then again with
  `LLM_TEST_PROFILE=reliable`. The script loads the repo's `.env` by absolute path (see the
  `load_dotenv` gotcha in `AGENTS.md`); update that path if the repo moves.
