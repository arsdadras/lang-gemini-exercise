# Teach-back

The project-close defense ([SKILL.md](SKILL.md), *Teach-back*): the learner teaches the design
card's key decisions, and I play a tutee who probes. It produces review items and nothing else:
it never gates closing the project, which is the user's call
([Definition of Done](../../../library/teaching/pedagogy.md#definition-of-done);
[Principle 10](../../../library/governance/principles.md#10-decide-dont-ask)).

## Procedure

1. **Announce it at Session 0:** "At the close you'll teach this project's key decisions to a
   new engineer, with nothing open." Expecting to teach directly is part of the effect.
2. **Set up:** one design-card decision at a time, explained in 8 to 12 lines, with no ADR or
   code open, to a tutee I name: a competent engineer new to LangGraph, or a skeptical reviewer.
3. **Probe:** three to five ladder questions per decision ([questions.md](questions.md#why)): why
   not the alternative, what if a force changed, which line enforces it (named from memory; the
   code opens only to check). A stall gets a smaller question, never the answer. A tutee who
   nods lets the learner recite.
4. **Score** each decision on the six elements below, 0 or 1 each, against the design card and
   its ADR, never against the learner's phrasing.
5. **Transfer:** one project-level question with a changed force ("the search API now bills per
   call", "two users share one thread"): what is the smallest design change?
6. **Route** every missing element and a missed transfer question as below, and tell the
   learner each gap by concept. No totals.

## Six elements per decision

| Element | Scores 1 when the learner states |
| :--- | :--- |
| Claim | what was decided |
| Force | the production force that made it necessary |
| Mechanism | how the code enforces it, down to the function or line |
| Alternative | the strongest rejected option, and when it would win |
| Failure | what concretely breaks if the decision is violated |
| Boundary | where the rule stops applying |

## Gap routing

| Missing | Gap type | Next move |
| :--- | :--- | :--- |
| Force or mechanism | Knowledge | Re-teach with a [design contrast](techniques.md#design-contrast); re-probe next session |
| Alternative, boundary, or the transfer | Judgment | A [rank-and-reveal](techniques.md#rank-and-reveal) item on that decision type |
| A wrong claim | Misconception | The [refutation move](techniques.md#refutation-and-feedback), then a re-predict |

Each gap becomes a concept-level row in the [review items](materials.md#review-items-table).
Scores, quotes, and verdicts on the person stay out of every repo file.

## Repo example

The learner teaches: "Specialists return a `failed` envelope so the coordinator doesn't crash."
The tutee probes:
- "So every exception becomes `failed`?" (boundary) No: `run_rag` re-raises anything
  `failure_kind` can't classify, because that is a bug.
- "Why not let the coordinator catch?" (alternative) It couples every caller to every
  specialist's failure types, and the typed contract is lost.
- "Then where is the retry?" (mechanism) Inside the specialist, one layer: `TRANSIENT_RETRY`
  on the node that makes the external call, before the envelope is built.

## Design-defense prompts

Pick four or five per project, the same shape every time; the three in
[questions.md](questions.md#teach-back) also apply.

1. "Why is this a graph (or an agent, or a node) and not the other?"
2. "What happens when a dependency is down for five minutes? Walk the retry, the fallback,
   and the envelope."
3. "Where does per-user identity enter, and what leaks if it's read from the wrong place?"
4. "What would you remove to cut 30% of the code, and what would you lose?"
5. "Show me the test that proves this property. What doesn't it prove?"
6. "At production load, what changes first?"

**Evidence:** learning by teaching (MA) and tutee questions pushing tutors to build knowledge
(Review), both from students; untested in written chat, so its value rests on the probing
([evidence](evidence.md#learning)).
