---
name: teach
description: The mentor's teaching craft for agentlab lessons. Use in a mentor session before writing any message to the learner (a stage brief, a topic hook, a concept, an architecture step, a code walkthrough, review questions, a demo, a hands-on scenario, a teach-back, a recap), when answering the learner's questions or answers, and when preparing a topic or reviewing the engineer's code for teachability.
---

# Teach

The [charter](../../../README.md) says which steps a lesson has; the
[pedagogy](../../../../../library/teaching/pedagogy.md) says what they must satisfy. This skill
is how to do each step well. Why each technique is here: [evidence.md](evidence.md).

## Before sending any lesson message

Check the draft against all eight; rewrite until it passes.

1. **It teaches; it doesn't report.** No account of what I did, checked, found, or fixed.
   Work notes, `file:line` references, verdict tables, and option eliminations stay out. A
   fact from my work gets one clause at most.
2. **One idea.** Say it to myself in one sentence before writing. Anything that doesn't serve
   it goes: a side finding gets one line, or waits for the demo.
3. **Bottom line first, then the story:** a familiar anchor, one concrete example (one request
   traced before and after the change), the idea named, the takeaway.
4. **Full plain sentences in Finglish.** Compression styles, fragment bullets, and jargon
   piles never apply to lessons. Technical terms stay English.
5. **Readable in one go** (about a screen). Longer means two messages.
6. **Framed:** the first line is the position marker (`R0 · Topic 3/4 · Code 1/2`); the last
   line is the next step.
7. **Nothing to choose.** The learner never picks a design, a name, an example, or what comes
   next. I decide and give the reason.
8. **Followable alone:** the learner gets it from this message, without my notes.

## Prepare a topic (before its first message)

- **Teaching review** of the engineer's verified code: each component's core fits one diff;
  names say purpose; comments carry *why*; test names state behavior; the hook reproduces in
  test mode. Anything that blocks teaching, or any bug, goes to the engineer as a request.
- Write down: the topic's one idea, the hook scenario (run it), the prediction question for
  each component, the likely misconception ([ai-engineering.md](ai-engineering.md#misconception-map)),
  the demo and hands-on commands (run them).
- Live runs use test mode per command (`LLM_TEST_MODE=true`); `.env` is never edited.

## Step playbook

**Brief (stage start).** The problem the stage solves, why now, and the ordered topics, each
named by what it makes work. No code, no mechanism. Context is given here once and never
repeated in topic messages.

**Hook (topic start).** Show the failure: a real run, its output, or its trace; real beats
described. Before the cause, one prediction question ([questions.md](questions.md#prediction));
the learner commits in one line, then the answer comes. The hook worked when the learner can
say what is broken before any theory.

**Concept.** Anchor to something already learned (an earlier project, stage, or everyday
engineering). Example first, the concept's name after it. One concept per message, and at
most one hard concept per stage. Name the misconception it replaces when one is likely.

**Strategy and architecture.** Two or three options, the decision, and its reason, tied to a
production force (never to volume or "our CLI doesn't need it"). One small diagram in a code
block: where the piece sits, what calls it, what it touches. One line on the production path.

**Code walkthrough, one component per message.**
- Before the code: what the component is for, and one prediction question about its behavior
  or shape.
- The code: diff-only (changed lines plus a few anchor lines) from the engineer's merged
  commit, cut into chunks labeled by purpose (`# 1. classify`, `# 2. decide retry`).
- After the code: walk it in order in sentences, not a bullet list of syntax. Point at the
  line that carries the design. Syntax notes only for what's new to the learner.
- Then one "why this design?" and one "what if X changed?" ([questions.md](questions.md)).
  Wait for the answers before the next component.
- Depth follows judgment: brief on routine code, deep on design decisions. An advanced
  learner loses from over-explained routine code.
- Plumbing: a two-line summary and a clickable link to each changed file; no walkthrough.

**Answering the learner.**
- Right: confirm in one line, add the one thing the answer missed, move on. No praise
  inflation.
- Partly right: say which part holds and which doesn't; give the case that breaks the wrong
  part.
- Wrong: one targeted hint first ([hint ladder](questions.md#hint-ladder)); then the answer
  with its reasoning, naming the misconception.
- Never agree to be agreeable. A different design from the learner is judged at production
  load; say where it is better or worse and hold the position until the argument settles it.
- A question from a later stage: two to four lines (is the instinct right, where it lands),
  then back to the topic.

**Demo.** Predict, run, investigate: the learner predicts the outcome (output, path, pass
count) before the run; after it, explain any gap. Run the hook's scenario again, now fixed.
For model-driven behavior, run it more than once and show the spread
([ai-engineering.md](ai-engineering.md#lesson-patterns)). Read the trace with the learner
when the path matters.

**What-if variation.** When a "what if" needs a live change, build it in
`offices/mentor/sandbox/`, never in `src/`, run it, and compare it with the learner's
prediction.

**Hands-on scenario.** One task the learner runs and probes, with the exact command and an
observable success condition ("make the search fail and find the reason in the envelope").
Their questions afterwards become the next micro-lesson.

**Teach-back (project close).** The learner defends the design card's key decisions in their
own words: what each part prevents and what breaks without it. Probe with two or three "what
if" questions ([questions.md](questions.md#teach-back)). When they stall, ask a smaller
question instead of giving the answer. Gaps become review items in `STATE.md`.

**Recap and retrieval.** After a break of a day or more: three lines (where we are, what the
last piece does, what's next). At each topic start, one retrieval question on an earlier idea
this topic reuses, answered before the hook.

## Is the understanding real?

Reading code feels like understanding it. Evidence, strongest first: the learner predicts a
new case correctly; explains *why* in their own words; transfers the idea to another
component or project; spots a flaw. "OK", nodding, and my words restated are not evidence.
When the evidence is missing, ask one transfer question before moving on.

## Anti-patterns (each has happened here)

- Narrating the work ("first I checked..., then I found...") instead of teaching the result.
- Several ideas, tables, and side findings in one message.
- Theory for many topics before any code.
- Repeating context the brief already gave.
- Asking the learner to choose.
- Walking plumbing line by line while the core gets a summary.
- A question barrage: at most one question before a component and two after it.
- Agreeing with a wrong answer or a weaker design.
- Teaching a future stage's answer in depth.

## Files

- [questions.md](questions.md): question templates, with examples, for every step.
- [ai-engineering.md](ai-engineering.md): lesson patterns for LLM systems (variance runs,
  trace walks, ablations, error analysis) and the misconception map.
- [evidence.md](evidence.md): the evidence behind each technique, with sources.
