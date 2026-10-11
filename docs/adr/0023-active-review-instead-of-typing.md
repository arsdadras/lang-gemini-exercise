# ADR-0023: The learner reviews verified code instead of typing it

- Status: Accepted
- Date: 2026-09-28
- Origin: user direction (2026-09-28): "code haro ham dige nmikhad pak konan ke man type konam,
  aksaran review cheshmi baram oke". Amends [ADR-0022](0022-engineer-role-and-division-of-labor.md)
  (step 4 of its flow) and the pedagogy's deliberate-practice rule.
- Revisit when: a teach-back or a "why" question shows a gap that reviewing didn't close, twice in
  one project.

## Context

- **Typing was the deliberate practice.** The pedagogy had the learner type the core
  architecture code, and the mentor reset lesson files so they could; ADR-0022 kept that step,
  with the engineer's verified version restored afterwards.
- **The learner prefers to review.** Reading and reviewing the verified code is enough for them
  most of the time; when they want to write, they write in their own private area and notebooks.
- **The risk is fluency:** reading code feels like understanding it. Typing hid that risk behind
  effort; reviewing needs checks of its own.

## Decision

- **Nothing is reset for typing.** The engineer's verified code stays in the repo, and the
  learner reviews it. There is no exercise state any more.
- **Active review is the practice:**
  - a prediction question before the code;
  - the mentor walks through the core architecture code one component at a time (diff-only),
    while plumbing is shown with links;
  - "why this design?" and "what if X changed?" questions after each component;
  - a hands-on scenario after the demo (the learner runs and probes the system);
  - a teach-back at each project close.
- **Variations are shown, not typed:** when a "what if" needs a live change, the mentor builds
  the demo in its own sandbox and leaves `src/` to the engineer.
- **The learner writes code only when they choose,** in `alireza/`, which stays private: no role
  reads it, and whatever they want reviewed they send.

## Consequences

- The pedagogy's learning-science basis, delivery invariants, and topic assessment change; so
  do the mentor's delivery loop and working agreements, and the git policy's exercise-state rule.
- The engineer shapes code for reading: lesson-sized commits and a named core for each
  component.
- Understanding is measured by the answers to the review questions and the teach-back, not by
  code the learner produced.

## Alternatives considered

- **Keep typing:** rejected. It was the learner's own choice to stop.
- **Review with no checks:** rejected. The fluency risk is real; prediction, "why", and
  teach-back questions already sat in the pedagogy and now carry the practice.
