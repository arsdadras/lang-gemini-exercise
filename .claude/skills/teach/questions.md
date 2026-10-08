# Question Bank

Templates for each question the lesson loop asks, with examples from R0's failure contract
(`utils/failure_util.py`, the `run_*` boundaries in `subagents/`) and P2's RAG graph
(`graphs/rag_graph.py`, `nodes/rag_node.py`). A question is good when a wrong mental model gives
a different answer than the right one; a question anyone could answer by rereading the code
tests attention, not understanding. Every question's expected answer and likely misconceptions
are written down before it is asked (SKILL.md, *Prepare a topic*). One question per message.

## Prediction

Asked before the code or the run. The learner commits, with a one-line reason; then the reveal.

| Kind | Template | Example |
| :--- | :--- | :--- |
| Behavior | "When X happens, what does the system do: A, B, or C?" | "Tavily answers 401. Does `run_rag` retry, crash, or return an envelope?" |
| Placement | "Where would you put X, and why there?" | "Where does the retry for an embeddings call belong: the client, the node, or `run_rag`?" |
| Count | "Out of N runs, how many pass?" | "We run this scenario five times in test mode. How many end `ok`?" |
| Path | "Which node or tool runs after X?" | "The grader rejects every document. Which node runs next?" |
| State | "After X, what does Y hold?" | "`grade_chunks_node` returns `{"chunks": relevant}`. After two rounds, what does `generate` see?" |
| Shape | "What does the output look like?" | "What `status` and `reason` does the coordinator see in the envelope after a 429 that outlives its retries?" |

Rules:
- Ask only where a wrong mental model answers differently; plain wiring gets none.
- Prefer a checkable answer: a path, a count, a final value. The run or the code the learner is
  about to read settles it.
- About behavior or design, never syntax.
- Options (A/B/C) are fine when an open question would stall; then each wrong option encodes one
  named misconception ([map](ai-engineering.md#misconception-map)).
- After a miss, one follow-up on the same idea with a new surface.

## Purpose

"In one sentence, at most 15 words: what is this for?" Hide the docstring. The first time, show
a line-by-line answer and a purpose-level answer on a different fragment, so the target is
clear. Judge: correct, purpose-level, unambiguous; give feedback on the weakest; follow with
"for every input?".

Example, `route_after_grading`:
- Line-by-line: "if chunks, generate; else if retries < MAX_RETRIES, rewrite; else web."
- Purpose-level: "Answer from the corpus if grading kept anything; otherwise rewrite and retry,
  then fall back to the web."

## Why

Asked after a component: the trade-off ladder. Two or three rungs per component, in order; rung
2 always makes the learner point at the line.

1. **Force:** what made this necessary? "Why must a node make only one external call?"
2. **Mechanism:** which line stops it? "Point at the line that keeps a retry from calling the
   model again."
3. **Breakage:** what breaks if we remove it, or do it the obvious way? "What goes wrong without
   `retry_on=is_transient` in `TRANSIENT_RETRY`?"
4. **Scale:** a hundred users, concurrent threads, an hour-long outage?
5. **Cost:** what does it cost (latency, calls, complexity)?
6. **Alternative:** the strongest rejected option, and when would it win? "Why does `run_rag`
   turn a 401 into `failed` but let a `KeyError` raise?"
7. **Reversal:** what would make us undo it?

Aim at how parts relate and what the whole is for. Atom-level questions only for framework atoms
(`retry_policy`, `NotRequired`, `END`).

## What if

Asked after the why, building on its answer. One variable changes; the learner predicts the
consequence.

| Lever | Template | Example |
| :--- | :--- | :--- |
| Remove | "What if we delete X? Walk the first production incident." | "What if the `retrieve` node loses `TRANSIENT_RETRY`?" |
| Change | "What if X did Y instead?" | "What if `web_search` also called the model? What happens on its retry?" |
| Scale | "What if N users did this at once?" | "What if a hundred users hit a 429 at the same second?" |
| Fail | "What if X fails in a new way?" | "What if `failure_kind` meets an exception it doesn't know?" |
| Force | "The world changed: what is the smallest design change?" | "The search API now bills per call. What changes?" |
| Adversary | "What if the input is hostile?" | "What if a search result contains an instruction to the agent?" |

When the answer needs a live run, build a labeled variant in `mentor/sandbox/` and run
it against the learner's prediction.

## Decision

For architecture steps and design contrasts ([cards](techniques.md)).

- **Rank and reveal:** a scenario in five to ten lines of production terms; "Rank options A-D and
  give two to four sentences of reasons." The options include the design's choice, a competent
  novice's, and one that breaks only at load. After the reveal: "What did the design weigh that
  you didn't?"
- **Reconstruct:** "Here are ADR-NNNN's context and forces. What would you decide, which two
  alternatives would you reject, and what consequence would hurt?" Then the full record, and the
  learner diffs it against their answer.

## Review

When the learner reviews a component as a PR before my walkthrough.

- Before the diff: "What must a correct change do? Two or three criteria."
- With the tests: "Which behavior does this test pin, and what stays untested?"
- After: "Two to four comments in a reviewer's voice: a question, a suggestion, or an approval
  with its reason." A real finding is fixed before the next step.

## Hint ladder

Only for the topic's target idea. Plumbing, API names, and flags are told outright, and "just
tell me" gets the answer at once plus one check. Otherwise climb one rung at a time and stop as
soon as the learner gets it.

1. **Point:** name the place to look. "Look at what `failure_kind` returns for a 401."
2. **Narrow:** give one concrete case to trace. "Follow one 401 from the Tavily call to the
   coordinator."
3. **Answer:** give the answer with its reasoning, name the wrong model it replaces, and end
   with a question that uses the correction.

## Transfer

The strongest check that understanding is real. Ask it when the answers so far were only
restatements.

- "Where else in the repo would the same rule apply?"
- "P12 adds a new specialist that calls a payment API. What does its `run_*` need?"
- At a topic close: "In three to five sentences: the force, the decision, the mechanism, the
  rejected alternative, and what breaks if it's violated." A paraphrase of the ADR doesn't count;
  ask for one element the record lacks.

## Retrieval

One line at a topic start, and one older review item after a recap. Ask for explanation, not
recognition.

- "Why does the model fallback re-raise the primary's error, and what does that break?" (not
  "which error is re-raised?")
- "What does a checkpointer save, and what doesn't time travel rewind?"

## Teach-back

At a project close; the procedure, scoring, and gap routing are in
[teach-back.md](teach-back.md).

- "Explain to a new engineer why the specialists return an envelope instead of raising."
- "Draw the path of one failed request from the tool to the coordinator."
- "Which decision in the design card would you change first at a hundred times the load, and
  what breaks if you don't?"
