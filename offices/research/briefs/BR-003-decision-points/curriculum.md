# BR-003 › Curriculum: teach it, teach with it, teach by building it

Supports [BR-003](README.md) version 2. A proposal against the lead's
[PEDAGOGY](../../../lead/PEDAGOGY.md):

- backward design;
- one hard concept per stage;
- the problem before the theory;
- the learner types the core architecture code.

The lead decides; the mentor teaches.

## Why this belongs in this curriculum

The curriculum's product is an engineer who can design production-grade agent systems. In
September 2026 the production pattern for controlling agents became:

- typed, cheap judgments at every step;
- escalation to an LLM or a person;
- measurement against labeled data.

Decomposing judgment and measuring it, "decision engineering", is a skill of its own. It isn't
prompt engineering, and the evidence shows it matters: one task went from 62.6% to 95.0% by
decomposition alone. Learning it here, across the stages the learner builds anyway, is exactly
the "production-level skill" the mission names.

## Outcomes

| The learner can… | Competencies |
| :--- | :--- |
| Find the decision points in any agent or graph, and tell them from generation points | C10, C9 |
| Decompose a judgment into operational, atomic questions with an honest answer set, and measure wordings against each other | C8 |
| Choose per point between code, a decider, an LLM, or a cascade, with evidence | C9 |
| Set thresholds from the cost of each mistake, and design gates that escalate but never approve | C6, C9 |
| Build and run a labeled set: accuracy per class, unsafe errors, coverage at an error budget, cost, latency | C8 |
| Put a decider behind a seam, so the backend is swappable and testable with a fake | C10, C5 |
| Explain where deciders fail (injection, implied conditions, off-distribution, language) and design around it | C6 |

## Teach it: the thread

Only one stage carries decision engineering as its hard concept; everywhere else it is practice
or a supporting lesson.

| Stage | Hard concept (unchanged unless noted) | Decision-point lesson | Opening demo (problem first) |
| :--- | :--- | :--- | :--- |
| R2 | Retrieval evaluation | *Supporting:* the grader measured LLM against decider on the same labeled set; one call per document against one batched request | Time a four-document question: several seconds of sequential grading, against about 0.45 s batched |
| P5 teaching pass | As planned | *Supporting:* memory staleness as a decision, with the implied cases escalated; the guard as a tightening ensemble | A remembered "vegetarian" survives "had a steak dinner last night" |
| **D1** (new, proposed) | **Decision engineering:** decomposition, thresholds from error costs, the cascade and the gate, the seam | This stage *is* the lesson. Material: our routing, staleness, and grader sets | The same phishing-style task asked as one broad question, then as five atomic ones (the 62.6% → 95.0% story, rebuilt on our own data) |
| P6 | Deterministic workflows (A1); control styles compared (C1) | *Practice:* branches decided by typed decisions; three control styles on one eval set | A supervisor agent that takes a dozen LLM calls to route what three typed decisions settle |
| P7 | Typed extraction; human review of ambiguous fields | *Practice:* candidates plus a `choice` plus "none"; the review band | An LLM extractor inventing an invoice number that isn't in the document |
| P8 | Triage; approvals; the cascade at scale (C3) | C3 stays its hard concept, now at production scale on feedback data | As planned |
| P11, P12 | Actions; routing | *Practice:* gates that escalate; routing over typed contracts | As planned |

**Why a dedicated stage, D1, and why there:**

- The skill has many consumers, and teaching it piecemeal would add a second hard concept to
  several stages.
- After R2 and the P5 teaching pass, the learner has labeled sets and two concrete decision
  points in hand.
- Right before P6, the capstone that uses it most.

If the lead prefers no new stage, the fallback is to widen R2's scope, with evaluation of
retrieval *and* decisions as one concept. That makes R2 heavier.

## Teach with it: the learning loop

Uses of decision models inside the teaching itself. All are formative, the learner owns every
judgment about their own work, and there are no grades. The learner's private scratch area is
never read; only in-session messages and repo code are used.

1. **Misconception routing.** When the learner's typed component or answer is wrong, the decider
   picks which known misconception it matches from a list the mentor wrote for that topic. The
   mentor then words the hint. The catalog's grading essay describes the same "verdict battery"
   design, and cites fluency bias and gaming as the risks.
2. **Stuck and fatigue signals.** The charter already asks the mentor to offer a stop point when
   the learner signals fatigue. A consistent check on recent messages makes that reliable. The
   pattern is the Rubik's-cube coach: quiet during progress, and stepping in on mistakes.
3. **Calibration training.** The learner attaches a probability to each prediction question.
   The mentor tracks calibration over the curriculum, and the learner can compare with a
   decider's own probability on the same question, like the ecosystem's "confidence trivia"
   game. It trains the very judgment the curriculum asks of an engineer.
4. **Teach-back checklists** (DEC-008). The design card's key decisions become atomic questions
   ("did the learner explain why the gate fails closed?"). They give the mentor a consistent
   coverage checklist, and the mentor still judges.
5. **Item analysis.** Across stages, the recorded misconceptions show which concepts keep
   returning, and those become review items (PEDAGOGY's assessment rules).

**Safeguards:**

- versioned question sets;
- logged probabilities;
- anything uncertain goes to the mentor's own judgment;
- the learner sees what was judged and can dispute it;
- no use of the decider on anything that affects stage closure, which stays the learner's own
  gate.

## Teach by building it: labs

Short, hands-on exercises inside the stages above, each ending in a measured before and after:

- **A router lab** (D1): our 32 routing requests, a decider against the coordinator's LLM choice.
- **A gate lab** (P6-B3, P8-B3): escalate-only command gates, with a red-team set that includes
  authority-claiming injections. The learner watches the gate be fooled, and shows why static
  rules come first.
- **A done-gate lab** (D1 or R5): verify a specialist's `ok` against its evidence.
- **A question-design lab** (D1): two wordings on one labeled set. Our own record shows wording
  moving answers both ways.
- **A compile-then-run lab** (D1): an LLM turns `MEMORY_WRITE_POLICY` into typed questions, and
  the learner measures and fixes them.

## Keeping it honest

- **The non-uses are taught as deliberately as the uses:**
  - generation;
  - syntax-level checks;
  - sole security gates;
  - implied conditions without escalation.
- **Every exercise's backend stays swappable** (Jev, an LLM, Laya), so the lesson is the pattern,
  not a vendor.
- **The evidence is taught with its labels.** Most ecosystem numbers are builder-reported; the
  learner learns to ask for the labeled set.
