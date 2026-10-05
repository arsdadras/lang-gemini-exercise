# EV-2026-10-05-claim-check-flash-lite: Gemini 3.5 Flash-Lite on the claim check's seed set

| | |
| :--- | :--- |
| Status | current |
| Label | **[V]**: console output in [`artifacts/`](artifacts); the set and script are in [EV-2026-10-05-claim-check-jev](../EV-2026-10-05-claim-check-jev/artifacts) |
| Ran | 2026-10-05, lead, test mode (`LLM_TEST_MODE=true`, the `free` tier: `gemini-3.5-flash-lite` called directly on Google's API with `GOOGLE_API_KEY`) |
| Question | The LLM half of [EV-2026-10-05-claim-check-jev](../EV-2026-10-05-claim-check-jev/README.md): how does the escalation path do on the same 34 cases? |
| Cited by | [P1 design card](../../../../docs/design_cards/P1_research_agent.md), `nodes/claim_check_node.py` |

## Setup

The same 34 cases and the same unsafe-error definition as the Jev record. The LLM gets
`CLAIM_VERDICT_PROMPT` with structured output (`ClaimVerdict`), one claim and one passage per call.

## Results

| | Gemini 3.5 Flash-Lite | Jev (`jev-1.13.0`, from the Jev record) |
| :--- | :--- | :--- |
| Accuracy | 100% (34/34) | 91.2% (31/34) |
| Unsafe errors | 0 | 2 |
| Finglish | 100% (5/5) | 80% (4/5) |
| Latency | p50 937 ms, p95 20.4 s | p50 443 ms, p95 724 ms |
| Cost | $0 (Google's free quota) | $0.0006 |

## Reading

- On these 34 cases the LLM is more accurate than Jev and made no false citation, including on
  the injected instructions and the Finglish negations that moved Jev.
- Its tail is the cost: p95 20 s, from the free quota's rate limiting and retries, against Jev's
  sub-second tail. A 20 s call is acceptable for the unsure few and not for every pair.
- That supports the shape the card chose (the decider answers what it is sure of, the LLM sees
  the rest) but does not settle which should be primary: at 34 cases one miss is three points,
  and the LLM saw every case while Jev's 0.8 threshold sends it only 5.

## Limits

- 34 cases written by the lead; the free tier's throttling shapes the latency, not the model.
- One run; no repeat to see the LLM's variance. The standard asks for 50 cases to start and 200
  before fitting thresholds.
- The unsafe-error definition favors an LLM that is conservative about `supports`; the set has
  no passage that merely implies a claim, which would test that.

## Re-running

```bash
LLM_TEST_MODE=true uv run python evals/claim_check_eval.py --only llm
```
