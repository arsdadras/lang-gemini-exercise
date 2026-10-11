# Decision Models: A Design Guide

[Decision models](README.md) › design guide. As of **2026-09-27**. Written for any role that
designs, plans, or reviews an AI step. It is a research draft:

- whether it becomes a library entry is the lead's call ([BR-003](../../briefs/BR-003-decision-points/agent-guidance.md));
- binding rules are the lead's ([ARCHITECTURE.md](../../../../docs/ARCHITECTURE.md)).

## In one minute

- **What it is.** A decision model answers typed questions about a state:
  - `choice`: one of your options;
  - `noul`: the probability that a statement holds;
  - `score`: a place on an ordered scale.

  It never writes text. Jev is the main hosted one; Laya and Open-Jev are open.
- **Strong at:**
  - bounded choices: which tool, which action, which route, which skill;
  - abstaining when nothing fits;
  - consistency;
  - many questions in one call;
  - here, about 0.45 s and $0.00002 per decision.
- **Weak at:**
  - generation and open reasoning;
  - implied conditions;
  - one broad question in place of several narrow ones;
  - non-English text;
  - authority-claiming injection.
- **More:** the full picture is in [capabilities.md](capabilities.md), and who builds what in
  [ecosystem.md](ecosystem.md).

## Find the decision points

Every AI step is a **generation point** (it writes) or a **decision point** (it picks, checks,
or scores). Look for decision points in three places:

1. **Around an agent's model:**
   - before a turn: model, specialist, skills, rules, memories;
   - during it: next tool or action, whether a call may run, which results stay in context;
   - after it: is it done, do the claims have evidence, does it follow the rules;
   - and around it: is a memory stale, is it worth recalling.
2. **At a graph's branches:** every conditional edge, grader, and gate in a LangGraph flow.
3. **In the work around the code:** CI checks, commit and PR honesty, semantic lint, and
   feedback on a learner's attempts.

## Choose the backend

Ask in order, judged at production load
([principles 2](../../../../library/governance/principles.md#2-know-the-context-of-best-practice-asl-e-shenakht-e-context)):

1. **Does it write?** Use an LLM. If a step decides *and* explains, split it: decide with a
   decider, and word it with an LLM or a template.
2. **Can code decide it?** Syntax, lookups, arithmetic, dates, and schemas belong in code, and
   code runs first. In our lint spike, the two rules a parser could decide were the decider's
   weak spots.
3. **Is there a labeled set, or will the stage build one?** With no labels there's no
   threshold, and no production use.
4. **Which mistake is cheaper?**
   - A security or trust decision may be *tightened* by a decider: add "ask" or "block", or stop
     and ask a person.
   - It is never *loosened* without a labeled red-team set and a lead decision (ARCHITECTURE
     principle 4).
   - The ecosystem's term for this is "escalate, never approve".
5. **Is the state safe and small?**
   - With user or third-party text in the state, the decider is never the only gate:
     authority-claiming injection succeeded 147 times in 200 in one study.
   - Filter out irrelevant context.
   - Limits: 32k tokens through OpenRouter, and 255 options.
6. **Is the input English?** Build a Finglish subset first, and escalate until it's measured.
   Spanish cost 3-6 points.

**How to read the answers:**

- **When 1 and 2 are no and 3 is yes, a decision model is a candidate.** The measurement picks
  among an LLM, a decider, and a cascade: the decider answers when confident, and the rest goes
  to an LLM or a person.
- **Don't adopt one because it's new.**
- **Don't reject one because today's traffic is small** (principles 2).

## Write the questions (Jev engineering)

1. **Operational questions:** could a new hire answer it the same way every time?
2. **One judgment per question.** Combine answers in code: rules, weights, or a small fitted
   model. Decomposition took one task from 62.6% to 95.0%.
3. **Close the answer set honestly:** add `other`, `none`, or `unclear`.
4. **Put the edge cases inside the question:** "a visit is not a move".
5. **Name every item a batched question is about.** Unnamed items decayed to 0.150 accuracy in
   one study.
6. **Label user-written content as data to judge, never instructions.**
7. **Keep instructions in English,** even when the state isn't.
8. **Measure every wording on labeled data, and version it like code.** Rewording is an API
   change.
9. **Never assert exact probabilities in tests;** they move by a few hundredths.

## Policies that recur

| Policy | Use it when |
| :--- | :--- |
| Threshold and escalation (a cascade) | The decider settles the clear cases; an LLM or a person takes the rest |
| Escalate, never approve | A gate on consequential actions or on "done": it can stop and ask, never grant |
| Three-way gate: act, block, or ask | An action is consequential, and people should see only the uncertain band |
| Menu-constrained choice | The options are finite and listed by code: tools, UI elements, legal moves |
| Named checks plus a rule in code | A policy with several reasons; each check becomes an audit reason |
| Speculative fan-out | Ask every question the flow might need in one call; ignore the irrelevant ones |
| Draft, verify, escalate | A generated answer must be supported by retrieved context |
| Evals that are guardrails | The same typed checks run on saved traces and live |
| Decision cache | Repeated states: key on model, questions, and state |

Sources and results for each: [capabilities.md](capabilities.md#patterns).

## Call Jev in this repo

Verified on 2026-09-27
([EV-2026-09-27-jev-openrouter](../../evidence/EV-2026-09-27-jev-openrouter/README.md)).

- **Access and API.** The OpenRouter key (`OPENROUTER_API_KEY`) reaches OpenRouter's System One
  API at base URL `https://openrouter.ai/api`. Pin `typesafe/jev-1.13`.
- **Client.** `langchain-typesafe`, an alpha release and **not a repo dependency**. Adding it
  would add one package and change no version; whether it enters is the lead's decision.

```python
import os

from langchain_typesafe import Noul, NoulCriteria, TypeSafeClassifier

decider = TypeSafeClassifier(
    model="typesafe/jev-1.13",
    base_url="https://openrouter.ai/api",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
result = decider.invoke({
    "state": {"question": question, "document": document},
    "questions": {
        "relevant": Noul(
            instructions="Does `document` contain information that helps answer `question`?",
            criteria=NoulCriteria(
                true="`document` states facts that answer or directly help answer `question`.",
                false="`document` is about something else, even if it shares words with it.",
            ),
        ),
    },
})
p_relevant = result.nouls["relevant"].noul  # probability of yes, 0-1
```

**Fitting it to the conventions:**

- **Retries (Convention 11):** the client has none, so give the call exactly one retry layer.
  Its errors subclass `langchain_core` model errors.
- **Cost:** the client drops OpenRouter's `usage.cost` and generation `id`. Compute the cost from
  input tokens at $0.042 per million.
- **Test mode:** `LLM_TEST_MODE` doesn't touch it today.
- **Tests:** unit tests inject a fake decider; live checks belong in eval-lite.

## Raising a use

- **Mentor:** a decision point met in a stage goes to the lead as a `request`, with this guide's
  answers.
- **Lead:** backends and dependencies go through the radar.
- **Any role:** to ask for a measurement, message the research office.

No role adds a dependency or rewires a call site outside its plan.
