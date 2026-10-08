# Lesson Materials

Templates I fill while preparing a topic ([SKILL.md](SKILL.md), *Prepare a topic*), each with its
rules and a repo example. I run every script under the real configuration, in test mode per
command, before the lesson; `.env` is never edited.

## Demo script

```text
DEMO <id>:  <the idea; named to the learner only after Run 2>
Setup:      <commands, each with LLM_TEST_MODE=true; starting state; the fault, if any>
Tests:      <key test> pins <behavior>; untested: <one thing>   (the learner says both first)
Predict:    <closed question> A) ... B) ... C) ...  + "One sentence: why?"
Run 1:      <the failing or surprising run>  -> expected: <output excerpt>
Gap:        "You predicted X; the output is Y. Which line makes the difference?"
Run 2:      <the verified run>  -> expected: <output excerpt>
Idea:       <named now: the decision this run exposes, and the alternative it rejected>
Then:       one what-if; one "where in the code is that decided?" (a file link)
Fallback:   <both runs' saved output in mentor/sandbox/, if a live call misbehaves>
```

- One demo, one idea, named after the run; named before, the prediction is free.
- Run the case where the naive prediction fails, the failing run before the verified one. For
  model-driven behavior, run three to five times and show the spread
  ([variance run](ai-engineering.md#lesson-patterns)).
- Narrate decisions, not keystrokes. A missed prediction becomes a review item, by concept.

**Repo example (the failure contract).** Tests: `test_rag_fails_on_an_outage_but_raises_a_bug`
pins that an outage becomes `failed` while a bug raises; no test runs the real graph's router.
Predict: "The search key is invalid and the corpus has nothing. What does the envelope say? A)
`failed`, a service rejected the request; B) `failed`, nothing relevant anywhere; C) it raises."
Run 1, a labeled sandbox copy of `web_search_node` that reads `results` directly: B, because
Tavily returns the 401 inside its response, so the outage looks like an empty web. Run 2, the
verified code: A, since `search_results` raises it and `failure_kind` calls a 401 permanent.

## Lab types and lab card

| Type | The learner | Success the harness shows |
| :--- | :--- | :--- |
| Guided exploration | Runs a scenario; answers three to five questions from the output, trace, or state | Each answer cites an output line, trace step, or state field |
| Break-it | Applies one prepared fault and predicts its effect | The symptom, and the line that contains it |
| Find-the-bug | Gets a labeled sandbox copy with one planted defect and its symptom | The file, the root cause, the test that would catch it |
| Fault injection | Runs the real system with a transient or permanent failure injected | The trace or envelope shows which layer handled it, and why that layer |
| Eval probe | Runs an eval-lite set with one variable changed (prompt, tier, threshold) | The metric before and after, and whether the difference is noise |

- Faults come from env vars, input, stubs, or a labeled copy in `mentor/sandbox/`, never
  from `src/`, `tests/`, the index, or any other repo file; a fault switch the code lacks is
  added to the code first, with a test. An env var goes on the command line (`load_dotenv()` doesn't
  override a variable already set).
- One fault per task, for one skill: localize a fault, read a trace, or name the owning layer.
- The harness judges success (a test name, an output line, a trace shape, a metric), not me.
- Prediction before the fault run; diagnosis after it as symptom, cause, mechanism, fix; hints
  on request, in tiers; the debrief asks what production would need.

```text
LAB <id>:   <title>                                   Time box: <n> min
Skill:      <one of: localize a fault | read a trace | name the owning layer>
System:     <command, LLM_TEST_MODE=true, starting state>
Explore:    run it clean; <a question answered in the output or trace>
Predict:    "If <fault>, what happens?"  (written before the run)
Break:      <the fault: env var | input | stub | sandbox copy>; run; record the symptom
Diagnose:   symptom -> cause -> mechanism -> fix, with a link to the file
Success:    <exact output line | test name | trace shape>
Hints:      H1 where to look | H2 what to compare | H3 the answer
Debrief:    what production would need; a gap becomes a review item
```

**Repo example (name the owning layer).** System: a sandbox script that prints
`run_rag(build_rag_graph(), <off-corpus question>).to_text()`. Explore: the clean run ends
`partial` (answered from the web). Break: `TAVILY_API_KEY=invalid` on the command line. Success:
the output starts `[rag] status: failed (An external service rejected the request: ...`.
Diagnosis: a 401 is permanent, so `is_transient` is false, `TRANSIENT_RETRY` doesn't retry
`web_search`, and `run_rag` turns the error into a `failed` envelope.

## Text diagrams

Draw one for branches, loops, calls over time, or state across steps; never for a straight
pipeline or anything one sentence says.

1. One diagram answers one question, and that question is its caption.
2. At most about 12 boxes or rows; cut whatever the one idea doesn't need.
3. Label edges with their condition or payload; mark the part under discussion (`<== this`).
4. Two to four lines of explanation go directly under the diagram.
5. Build it in steps: the skeleton first, the new branch in the next message.
6. One anchor diagram per project, reused in lessons, recaps, and the study guide; change it by
   adding, not redrawing.

Box, for control flow. Caption: "Where does the rewrite loop stop?"
```text
[retrieve] -> [grade_chunks] --kept some--> [generate] -> [check_hallucination]
    ^               |
    |               +--none, retries used up--> [web_search]      <== this
    |               |
    |               +--none, retries < MAX_RETRIES--> [query_rewrite]
    |                                                        |
    +--------------------------------------------------------+
```
Under it: the stop lives in the router, `route_after_grading`, which reads `retries`; only
`query_rewrite` increments it.

Sequence, for calls over time. Caption: "When does the shell command run?"
```text
agent                  HITL middleware              user
  |-- execute(cmd) --------->|                        |
  |                          |-- action request ----->|   run paused, checkpointed
  |                          |<-- approve ------------|
  |<-- execute runs ---------|                        |
```

State flow, for fields across steps. Caption: "What does a second question on the same thread
start from?"

| Step | `question` | `search_query` | `retries` | Note |
| :--- | :--- | :--- | :--- | :--- |
| Q1 start | X | X | 0 | the caller resets both scratch fields |
| Q1 end | X | X, rewritten | 2 | budget used; web fallback |
| Q2, no reset | Y | X, rewritten | 2 | retrieves for X; one empty grading goes to the web |

## Resume note

After a break of a day or more: the charter's three-line recap, then one recall question.

```text
<position marker, e.g. R0 · Topic 2/4 · Demo>
Where we are:  <the topic and step>
Last piece:    <what it does and why, in one sentence>  -> <file link>
Next:          <the next step>
Recall:        <one question on the last piece, answered before we go on>
```

- After the answer, restate only what it shows is shaky; then one due review item, in its own
  message (one question per message). Now and then the recall is closed-book.
- The project's anchor diagram may carry a `<== we are here` marker.

## Study guide

One per project, written at its close, at `docs/study_guides/p<n>_<name>/MASTER_GUIDE.md`.
The existing P3 and P4 guides adopt this template when they are next revised, not before.

```text
1. The problem: what breaks without this system (one paragraph)
2. Architecture: the anchor diagram and a three-line caption
3. Five questions this project answers (question headings, one or two paragraphs each)
4. Decisions: | Decision | Options considered | Chosen | Why (named force) | Would flip if |
5. Worked example: one annotated run with purpose labels (1. build state, 2. route, ...)
6. Gotchas: | Symptom | Cause | Where handled | Test that pins it |
7. Production path: what changes at real load (link the design card)
8. Commands and file map: run, test, eval; core files as links
9. Retrieval questions: eight to ten, answers folded
10. Where it returns: concepts left thin, and the later stage that revisits each
```

- Section 3's headings are questions that came up or were missed in review, not topic names.
- Every "why" names an admissible force (production, sequencing, evidence, scope), and every
  decision row names what would flip it.
- One part is learner-made (section 5's labels or a concept map), produced in chat and
  corrected by me.
- Link, don't copy: ADRs, the design card, `AGENTS.md` gotchas, code. Nothing personal: no
  quotes, scores, or names. Section 9 seeds the review items.

## Review items table

The one record of gaps and their re-checks, kept in `STATE.md` under "Review items". The row
below is illustrative, not a record.

| Concept | Where seen | Gap type | Re-teach in | Last asked | Result | Next due |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `virtual_mode` confines file tools, not the shell | project, step | misconception | a later topic or lab | session | miss, ok | session |

- **Concept:** the idea in one line, never what the learner said.
- **Gap type:** knowledge (missing force or mechanism), judgment (missing alternative or
  boundary), misconception (a wrong claim), or recall (known once, not retrieved). Teach-back
  gaps are routed by [teach-back.md](teach-back.md).
- **Result:** every re-check in order (miss, partial, ok): the only outcome data the method has.
- **Next due:** next session, then about a week, three weeks, the next project close (the
  mentor's heuristic). A miss or partial pulls it closer; two ok in a row push it out; a row
  still ok at a project close is removed.
- Concept-level only: no quotes, rubric scores, or judgments of the person; repo docs may be
  shared.
