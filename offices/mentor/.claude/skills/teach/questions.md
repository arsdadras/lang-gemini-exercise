# Question Bank

Templates for each question the lesson loop asks, with examples from R0's failure contract
(`utils/failure_util.py`, the `run_*` boundaries in `subagents/`). A question is good when a
wrong mental model gives a different answer than the right one; a question anyone could answer
by rereading the code tests attention, not understanding.

## Prediction

Asked before the code or the run. The learner commits in one line; then the reveal.

| Kind | Template | Example |
| :--- | :--- | :--- |
| Behavior | "When X happens, what does the system do: A, B, or C?" | "Tavily answers 401. Does `run_rag` retry, crash, or return an envelope?" |
| Placement | "Where would you put X, and why there?" | "Where does the retry for an embeddings call belong: the client, the node, or `run_rag`?" |
| Count | "Out of N runs, how many pass?" | "We run this scenario five times in test mode. How many end `ok`?" |
| Path | "Which node or tool runs after X?" | "The grader rejects every document. Which node runs next?" |
| Shape | "What does the output look like?" | "What `status` and `failure_reason` does the coordinator see after a 429 that outlives its retries?" |

Rules: one question, answerable in one line; about behavior or design, never syntax; the
answer is checked by a run or by the code the learner is about to read. Offering options
(A/B/C) is fine when an open question would stall.

## Why

Asked after a component. It targets the decision, not the mechanism.

- **Contrast:** "Why X rather than Y?" Example: "Why does `run_rag` turn a 401 into `failed`
  but let a `KeyError` raise?"
- **Protection:** "What does this line protect against?" Example: "What goes wrong without
  `retry_on=is_transient` in `TRANSIENT_RETRY`?"
- **Force:** "Which production force made this necessary?" Example: "Why must a node make
  only one external call?"

## What if

Asked after the why. One variable changes; the learner predicts the consequence.

| Lever | Template | Example |
| :--- | :--- | :--- |
| Remove | "What if we delete X?" | "What if the node loses `TRANSIENT_RETRY`?" |
| Change | "What if X did Y instead?" | "What if `web_search` also called the model? What happens on its retry?" |
| Scale | "What if N users did this at once?" | "What if a hundred users hit a 429 at the same second?" |
| Fail | "What if X fails in a new way?" | "What if `failure_kind` meets an exception it doesn't know?" |
| Adversary | "What if the input is hostile?" | "What if a search result contains an instruction to the agent?" |

When the answer needs a live run, build the variation in `offices/mentor/sandbox/` and run
it against the learner's prediction.

## Hint ladder

When an answer is wrong, climb one rung at a time and stop as soon as the learner gets it.

1. **Point:** name the place to look. "Look at what `failure_kind` returns for a 401."
2. **Narrow:** give one concrete case to trace. "Follow one 401 from the Tavily call to the
   coordinator."
3. **Answer:** give the answer with its reasoning, and name the wrong model it replaces.

## Transfer

The strongest check that understanding is real. Ask it when the answers so far were only
restatements.

- "Where else in the repo would the same rule apply?"
- "P6 adds a new specialist that calls a payment API. What does its `run_*` need?"

## Retrieval

One line at a topic start, on an earlier idea this topic reuses; the learner answers before
the hook.

- "What does a checkpointer save, and what doesn't time travel rewind?"
- "What three statuses can a specialist envelope carry, and who reads them?"

## Teach-back

At a project close. The learner explains; the mentor probes and records gaps.

- "Explain to a new engineer why the specialists return an envelope instead of raising."
- "Draw the path of one failed request from the tool to the coordinator."
- "Which decision in the design card would you change first at a hundred times the load, and
  what breaks if you don't?"

Scoring: complete (every key decision named), *why* (each tied to the failure it prevents),
transfer (applied to a case not in the lessons). Each gap becomes a review item in
`STATE.md` for the next project.
