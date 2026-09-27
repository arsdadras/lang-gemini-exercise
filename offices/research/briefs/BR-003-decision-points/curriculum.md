# BR-003 › Curriculum: teaching decision points

Supports [BR-003](README.md). A proposal against the lead's
[PEDAGOGY](../../../../offices/lead/PEDAGOGY.md): backward design, one hard concept per stage,
the problem before the theory. The lead decides; the mentor teaches.

## What the learner should be able to do

| Outcome | Competencies |
| :--- | :--- |
| Tell a decision point from a generation point, and choose per step between code, a decision model, an LLM, or a cascade, with reasons | C9, C10 |
| Break a broad judgment into atomic typed questions, and measure wordings against each other | C8 |
| Set thresholds from the cost of each mistake, asymmetric on security | C6, C9 |
| Build a labeled set, then measure a decision: accuracy per class, unsafe errors, coverage at an error budget, latency, cost | C8 |
| Build a cascade, and a gate with a review band that fails closed on errors | C5, C6 |
| Keep backends swappable behind a protocol | C10 |
| Explain why a decider may tighten a security verdict, and what evidence would allow it to loosen one | C6 |

## The thread

The thread is one hard concept at a time. Only P8-C3, already planned, makes decision models the
stage's hard concept. Everywhere else, the decision-point lesson is a supporting lesson built on
things the learner already knows: typed output and eval sets.

| Stage | Hard concept (unchanged) | Supporting decision-point lesson | Evidence of learning |
| :--- | :--- | :--- | :--- |
| R2 | Retrieval evaluation | The grader measured on the same labeled set, LLM against a decision model, one call per document against one batched request | Before and after: grading time and accuracy on the same questions |
| P5 teaching pass, C2 | As planned | Guard agreement, counting unsafe errors apart from accuracy | The guard set |
| P6-C1 | Deterministic against model-directed control | Typed decisions as the workflow's branch conditions | The control comparison |
| P7-A1, B2 | Typed extraction; review of ambiguous fields | Candidates, a `choice`, and "none"; the review band | Per-field accuracy |
| P8-B3, C1 | Approval for sensitive actions | Gates with a review band, and the evidence a loosening needs | The red-team set and labels |
| P8-C3 | The calibrated cascade (DEC-004) | n/a | Coverage at an error budget; cost and latency against the LLM alone |
| P12, E2 | Routing; platform services | Confidence-gated routing; a routing service | Per stage |

**R2's opening demo, the problem before the theory:** today's grader makes one LLM call per
document, one after another. The learner times a question with four documents, sees several
seconds go to grading, and predicts what one batched decision request would take (about 0.45 s
for six documents, measured).

## Teaching practices that decision models make cheap

Each check costs about $0.00002 and returns in under a second, so these can run live in any
lesson:

1. **Prediction questions with live probabilities.** "What will the model say to this negated
   Finglish sentence, and how sure will it be?" Then run it. Each one builds intuition for the
   documented failure modes.
2. **A question-design lab.** Two wordings, one labeled set, and a comparison. Our own evidence is
   the first case: the same cases moved in both directions with wording alone
   ([EV-2026-09-27 §3](../../evidence/EV-2026-09-27-jev-openrouter/README.md#3-wording-moves-answers-in-both-directions)).
3. **Decision-point hunts.** At each design card review, the learner lists the AI steps and
   marks, for each one:
   - decision or generation;
   - its error direction;
   - whether plain code could decide it.
4. **Error-direction drills.** The recorded case: two guards that both scored 7/8 on our set,
   one with no unsafe error (Jev) and one that let a fact about a third person through (Laya).
   The learner explains why the first is better.
5. **Case studies from our own records.** Laya failing open, the simulated cascade, and the
   wording flip. Real data from this repo beats textbook examples.
6. **Cost and latency literacy:**
   - input-only pricing;
   - batching;
   - end-to-end latency against the model's own (475 ms here against about 260 ms reported).
7. **Evidence before loosening a control.** At P8-B3, the learner must produce the red-team
   numbers before an auto-approve path ships: production change control in miniature.
8. **Compile, then run.** The learner has an LLM turn `MEMORY_WRITE_POLICY` into typed questions,
   then measures the result: policy treated as tested code.

## Assessment

- **Teach-back questions** (DEC-008) wherever a project has a decision point:
  - Why does this gate fail closed?
  - How did you choose the threshold?
  - What would make you loosen it?
- **Stage evidence:** every decision-point lesson ends with a before-and-after table of accuracy,
  unsafe errors, latency, and cost.

## Keeping it honest

- **Show the non-uses as deliberately as the uses.** The Finglish repair is code plus
  generation, consolidation needs inference, and the guard's user-facing sentence is generation.
- **Keep every exercise's backend swappable,** so the lesson is the pattern, not a vendor.
- **No deep-dive session is needed.** The concept has natural stages, and PEDAGOGY reserves
  deep-dives for techniques that have none. The library entry doubles as a 20-minute reading
  before R2.
