# EV-2026-09-27-jev-harness-decisions: Jev on harness decisions this repo actually makes

| | |
| :--- | :--- |
| Status | current |
| Label | **[V]**: cases, scripts, raw results, and console output in [`artifacts/`](artifacts) |
| Ran | 2026-09-27, research office |
| Question | Beyond the RAG and guard checks measured in [EV-2026-09-27-jev-openrouter](../EV-2026-09-27-jev-openrouter/README.md), how does Jev do on the *harness* decisions an agent system makes around its model, compared with our own LLM tiers? |
| Cited by | [BR-003](../../briefs/BR-003-decision-points/README.md), [capabilities](../../landscape/decision-models/capabilities.md) |

## Setup

Three decision types, each mirroring a real decision point in this repo or in its development:

1. **Routing (32 requests)** to one of seven specialists: web research (P1), repo docs (P2),
   code review (P3), run code (P4), memory (P5), direct answer, clarify.
   - 20 in English, 12 in Finglish.
   - Three negation traps ("don't search the web, just tell me…").
   - Four vague requests that should get "clarify".
2. **Memory staleness (20 pairs):** does the user's newest message make a stored fact stale?
   This is the decision P5's consolidator makes implicitly.
   - Explicit changes, implicit ones ("had a steak dinner" against "is vegetarian"), and traps:
     a visit, a maybe, and another person.
   - 4 of the 20 in Finglish.
3. **Semantic lint (16 snippets × 8 rules)** of this repo's own `AGENTS.md` conventions:
   - the rules: import-time work, model IDs outside the config, paths from the working
     directory, raw `.content`, non-ASCII console output, a retry around a model call, secrets
     passed to a subprocess, and identity from `config`;
   - eight snippets each break one rule, and eight look alike but are clean;
   - one request per snippet asks all eight rules at once (speculative fan-out).

Labels were written before any run.

**Jev:**

- `typesafe/jev-1.13` through OpenRouter's System One API, with `langchain-typesafe` 0.0.1a3;
- one question per request (eight for lint);
- three repeats.

**LLMs:** the repo's own registry, `llm_model.chain(tier, structured=...)`, with Pydantic `Literal`
schemas and prompts carrying the same definitions. Test mode, one run each:

- `default` → `opensource` tier (`glm-5.3`);
- `reliable` → `low` tier (`gemini-3.5-flash-lite`).

## Results

| Task | Jev, 3 runs | `glm-5.3` | `gemini-3.5-flash-lite` |
| :--- | :---: | :---: | :---: |
| Routing (32) | **32, 32, 32** | 30 | 30 |
| Memory staleness (20) | 20, 19, 20 | **20** | **20** |
| p50 per decision, end to end from here | **439-444 ms** | 2.2-2.3 s | 1.4-1.6 s |

**Routing.**

- Jev routed all 32 in every run, the Finglish requests and the negation traps included.
- Both LLMs sent the same two vague requests ("Do the thing we discussed", "hamoon kar-e dirooz ro
  edame bede") to `memory` instead of `clarify`.
- An earlier run of the `reliable` profile, lost to a file-naming bug in the script and rerun,
  scored 31/32. The LLMs vary from run to run as well.

**Staleness.**

- The LLMs were perfect. Jev was right on 59 of 60 answers, but with thin margins on exactly the
  implicit cases:
  - "Had an amazing steak dinner" against "vegetarian": p(yes) 0.57-0.59;
  - the movers bringing furniture to a new flat: 0.72-0.77;
  - "hamsaram migoft…" against "is single": 0.59, **0.47**, 0.56. This one changed its label
    in one run.
- The traps (a visit, a brother's steak, a maybe) were all right.

**Semantic lint** ([`output_lint_jev.txt`](artifacts/output_lint_jev.txt)):

| Threshold | Violations caught (of 8) | False alarms (of 120 clean checks) |
| :---: | :---: | :---: |
| 0.5 | 8 | 0 |
| 0.7 | 7 | 0 |
| 0.9 | 6 | 0 |

- AUROC 1.000 in run 1. Across runs, three checks changed label and p moved by up to 0.14.
  The p50 was 479 ms for all eight rules in one request, and all three runs cost $0.0015.
- The weak spots were the two rules a parser could decide:
  - raw `.content`: the violation scored 0.52, then 0.43 and 0.42, so it was missed twice;
  - non-ASCII output: the clean snippet scored 0.36-0.50.
- The rules only meaning can decide were clear, at 0.94-0.97: a retry around a model call,
  secrets passed to a subprocess, identity from `config`, a model ID outside the config, and a
  path from the working directory.

**Cost:** all Jev runs in this record, 156 routing and staleness decisions and 384 lint checks,
cost under $0.005.

## Reading

- **Routing is Jev's strongest ground here.** It was perfect and stable, with better abstention
  on vague requests than two LLM tiers, in both languages, at about a fifth of the latency. This
  matches the independent tool-selection results: MetaTool 77.8% against ChatGPT's 69.1%, and
  abstention 87.0% against 50.4% ([ecosystem](../../landscape/decision-models/ecosystem.md#independent-studies)).
- **Implied change is its weak ground,** as its own jaggedness page says: it got the answers
  right, but without confidence. A cascade handles this. At a 0.8 margin, the three implicit
  staleness cases would go to the LLM, which got them right.
- **Semantic lint works for meaning, not syntax.** Rules only meaning can decide separate
  cleanly. Rules a parser can decide should stay deterministic (AST or regex), with the decider
  reserved for what code can't express.

## Limits

- **Small sets, one author.** The cases are ours; they show direction, not rates.
- **The routing definitions matched word for word** in the Jev criteria and the LLM prompt.
  Production routing sees messier requests.
- **The lint snippets are synthetic,** one violation each, written to be recognizable. Real
  diffs mix concerns, and the precision of repo-scale semantic lint is untested here. One
  replay of 93 real Claude Code sessions reported 10 of 39 flagged edits confirmed **[T]**
  ([ecosystem](../../landscape/decision-models/ecosystem.md)).
- **One LLM run each,** and the lost `reliable` run is known only from its console line.
- **Latency is end to end from this machine,** through each provider's gateway.

## Re-running

1. The Jev scripts run in a venv with `langchain-typesafe[experimental]==0.0.1a3` and
   `python-dotenv`: `python -u spike_jev.py`, then `python -u spike_lint.py`.
2. The LLM script runs from the repo root:
   `LLM_TEST_MODE=true [LLM_TEST_PROFILE=reliable] uv run python -u <artifacts>/spike_llm.py`.
3. All scripts read the repo's `.env` by absolute path; update `REPO` if the repo moves. A full
   re-run costs about $0.01 for Jev plus 104 test-mode LLM calls.
