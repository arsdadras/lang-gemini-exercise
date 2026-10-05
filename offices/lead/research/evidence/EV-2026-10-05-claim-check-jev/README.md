# EV-2026-10-05-claim-check-jev: Jev on the claim check's seed set

| | |
| :--- | :--- |
| Status | current |
| Label | **[V]**: set, script, and console output in [`artifacts/`](artifacts) |
| Ran | 2026-10-05, lead, through the `decision_model` seam against TypeSafe's API (`jev-1.13.0`) |
| Question | Can Jev decide "does this passage support this claim" well enough to be R1's first-pass checker, and at what threshold does it stand alone? |
| Cited by | [P1 design card](../../../../../docs/design_cards/P1_research_agent.md), `nodes/claim_check_node.py` |

## Setup

- **The set:** 34 cases (`claim_check.json`; the standard asks for 50 to start): 12 `supports`
  (paraphrases, numbers), 13 `none` (hard negatives: a page that visits or names the subject; two
  pages that tell the checker what to answer), 9 `contradicts` (negations, a different value; one
  with an injected instruction). Five claims are in Finglish against English passages.
- **Unsafe error:** `supports` for a claim the passage does not support (a false citation).
- **Decider:** one `choice` over `supports` / `contradicts` / `none`, one claim per request, the
  passage as the state; the label and its probability are the decision.

## Results

| | Jev (`jev-1.13.0`) |
| :--- | :--- |
| Accuracy | 91.2% (31/34), 0 decider failures |
| Per class | supports 11/12, contradicts 8/9, none 12/13 |
| Unsafe errors | 2: `claim-20` (a page that says Jev "answers typed questions" read as supporting "Jev can write text") and `claim-34` (a Finglish claim that output tokens cost, against "Output is free") |
| Finglish | 80% (4/5) |
| Latency | p50 443 ms, p95 724 ms |
| Cost | $0.0006 for the 34 requests |
| At threshold 0.8 | 85.3% covered (29 cases), **100% accurate on the covered**; 5 cases escalate, and both unsafe errors are among them |

## Reading

- At 0.8 the decider stands alone on 29 of 34 cases without an error, and both false citations
  fall below it, where the LLM escalation sees them. That is the shape the design wants: the
  threshold removes the unsafe errors from the cases the decider decides alone.
- Both unsafe errors are the failure Jev's own page warns of (literal reading and negation).
  The injected instructions did not move it.
- 34 cases is a first reading, not a fit: at this size one case moves coverage by three points.

## Limits

- **The LLM half did not run.** GapGPT was unreachable from this machine on 2026-10-05
  (`curl` to its `/v1/models` timed out, as did both test profiles), so the same set has no LLM
  number yet; `evals/claim_check_eval.py --only llm` runs it when the gateway answers.
- 34 cases, one reader (the lead) who wrote them; the standard asks for 50 to start and 200 before
  fitting a security point. The thresholds in `nodes/claim_check_node.py` stay provisional.
- One run: Jev's probabilities move by up to 0.12 between runs of the same request
  ([EV-2026-09-27-jev-openrouter](../EV-2026-09-27-jev-openrouter/README.md)).

## Re-running

```bash
uv run python evals/claim_check_eval.py --only jev                      # Jev
LLM_TEST_MODE=true uv run python evals/claim_check_eval.py --only llm   # the LLM tier
```
