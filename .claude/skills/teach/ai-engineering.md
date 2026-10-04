# Teaching LLM Systems

What makes agent and LLM engineering different to teach from classic programming, and the
lesson patterns that follow. Sources: [evidence.md](evidence.md#llm-systems).

## What is different

1. **One input, many outputs.** Outputs vary even at temperature 0, so "it worked when I ran
   it" is a sample of one.
2. **Correctness is a rate.** Graders (code, model, human) judge transcripts and outcomes;
   tests grow into evals with thresholds. One success is not reliability: pass^k (every one of
   k runs succeeds) falls as k grows while pass@k rises.
3. **Part of the program is prose.** Prompts and tool descriptions steer behavior with no
   compiler or type checker, and even experienced developers predict their effect poorly.
4. **The trace documents the run.** The model picks the path at runtime, so the trace, not the
   source, shows what happened.
5. **The judge is a model too.** An LLM grader must itself be checked against human labels,
   and people can't fix grading criteria before they have read outputs (criteria drift).

## Lesson patterns

Each pattern is a demo or hands-on shape; pick the one that makes the topic's idea visible.

| Pattern | How it runs | Fits |
| :--- | :--- | :--- |
| **Failure first** | The failing run and its trace come first; the learner diagnoses; then the lead's fix, compared with the diagnosis | Every hook |
| **Predict, run, investigate** | The learner writes a prediction (output, path, pass count), we run, then explain the gap | Every demo |
| **Variance run** | The same scenario 3 to 5 times in test mode; the learner predicts the pass count first; we name pass@k and pass^k; after a change, ask whether the spread moved, not only the mean | Any model-driven demo |
| **Trace walk** | Open one trace; at each decision point the learner says why the model chose it before I comment | Routing, agents, tool choice |
| **Show me the prompt** | From the trace, rebuild the real system prompt and tool schemas the framework sent, and name what the framework added | Any framework abstraction |
| **Ablation** | Remove one part (a guard, a tool sentence, a retry, a grader); the learner predicts; run a small fixed set; compare | Design "why" questions |
| **Tier comparison** | One small eval set across two tiers or providers: quality, latency, cost per decision point | Model strategy, decision points |
| **Mini error analysis** | Read 20 to 30 outputs; one free-text note per failure; group into categories; count; one binary check for the top category | Eval topics |
| **Judge alignment** | The learner labels about 20 outputs; compare with the LLM judge; discuss each disagreement | Graders, eval-lite |
| **Grader or agent?** | A failing transcript; the learner says whether the agent or the grader failed and names the evidence; the outcome state settles it | Graders, eval-lite |
| **Capability to regression** | After a fix, decide which eval cases join the regression set and why | Closing an eval topic |
| **Design kata** | Given a job: workflow or agent, code or model at each decision point, where the gate goes, what the failure contract is; then compare with the verified design | Architecture steps |

Keep the sets small (k of 3 to 5, 10 to 30 cases) so a pattern fits one sitting, and record
the learner's prediction before every run.

## Sequencing rules

- Look before judging: read outputs before writing criteria or eval cases.
- Measure before tweaking: a prompt change is judged on a fixed set against a baseline.
- Least autonomy that works: workflow before agent, one agent before several, code before a
  model where a rule decides ([decision models](../../../library/architecture/decision-models.md)).
- Concept before framework: the idea in plain terms first, then the LangChain, LangGraph, or
  DeepAgents feature that implements it.
- Own taxonomy first: compare the learner's failure categories with a published taxonomy (such
  as MAST) only after they have built their own.
- One failure per demo, one measured claim per project: every demo shows a failure and its
  trace; every project close carries a pass count before and after, over k runs.
- Failure contracts, retry layering, and timeouts are taught from the repo's own conventions
  (`AGENTS.md`, convention 11); outside courses barely cover them.

## Misconception map

Seeded from practitioner sources and `AGENTS.md`'s gotchas; grown from the learner's observed
misses (a new row whenever a prediction misses for a reason not listed).

| Misconception | Question that exposes it | Pattern that corrects it |
| :--- | :--- | :--- |
| "It worked once, so it works" | "How many of five runs pass?" | Variance run |
| "Temperature 0 is deterministic" | "Why might two identical calls differ?" | Two diverging traces |
| "The agent did X because it said so" | "What is the outcome state, not the claim?" | Check the outcome against the transcript |
| "A better prompt will fix it" | "What is the baseline pass rate, on which cases?" | Before and after on a fixed set |
| "Use a standard metric" | "Which failure in our outputs does it catch?" | Mini error analysis |
| "The LLM judge is ground truth" | "How often does it agree with you on 20 labels?" | Judge alignment |
| "The framework feature is the concept" | "What prompt and state update did this call produce?" | Show me the prompt |
| "More agents or tools means more capable" | "Which failure does the extra agent add?" | Design kata, ablation |
| "A node retry is harmless" | "When this node retries, what runs again?" | Failure overlay on a trace; fault lab |
| "Returned updates accumulate" | "After two rounds, what does the next node see?" | Per-step state diff |
| "Scratch state resets itself" | "Same thread, second question, no reset: which path runs?" | Follow-up run on the same thread |
| "Replay rewinds side effects" | "After replaying to step 3, does the file exist?" | Time-travel demo (P4) |
| "`virtual_mode` sandboxes the shell" | "Which control stops `cat ../../.env`?" | Rank and reveal on safeguards |
| "The surfaced error is the last provider's" | "The primary timed out and the fallback hit a 429: which error surfaces?" | Fallback lab |
