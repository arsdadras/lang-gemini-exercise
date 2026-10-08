# Teaching Design Judgment: Techniques for Transferring an Expert's "Why" to an Advanced Learner

Scope: practical mentor technique for one-on-one chat lessons built on verified production code and
its decision records (ADRs, design cards). The learner is an experienced programmer who reviews the
code rather than typing it and must defend each design's "why" when a project closes. Evidence is one
line per technique. The technique cards (steps, worked example, when it works, failure modes) sit
under each section's **Inferences**, because the steps are my synthesis for this setting and not
procedures copied from a source. Worked examples use real agentlab decisions as `AGENTS.md` states
them (convention 11 on failures and retries, ADR-0005/HITL, ADR-0006, ADR-0007).

Research budget note: about 28 tool calls. Two PDFs (Klein & Borders 2016; the ECSEE 2023 kata
report) were read in full text. The other sources were read at abstract or snippet level; see Gaps.

---

## 1. Cognitive apprenticeship moves in practice (modeling, coaching, scaffolding/fading, articulation, reflection, exploration)

### Takeaway
The six moves carry over directly to a review-not-type setting when modeling means narrating the
*decision points* in finished code rather than the typing. For an advanced learner, support has to
fade faster than for a novice, because worked-example-style guidance stops helping, and can start to
hurt, as prior knowledge grows (expertise reversal).

### Cited Findings
- Cognitive apprenticeship is instruction that "makes thinking visible". Its six components are modeling, coaching, scaffolding (with fading), articulation, reflection, and exploration — [ISLS research topic page](https://www.isls.org/research-topics/cognitive-apprenticeship/)
- Live coding means the instructor thinks aloud while writing real code. A Koli Calling 2018 study found students rated it useful: it made the programming process easier to understand and helped them learn debugging (student-perception data) — [Raj et al. 2018, ACM](https://dl.acm.org/doi/10.1145/3279720.3279725); [PDF](https://pages.cs.wisc.edu/~gerald/papers/LiveCoding.pdf)
- In an IEEE Transactions on Education 2022 experiment, students who watched experts' flowcharting or coding process videos annotated with reflection notes improved their coding skills — [ERIC EJ1353386](https://eric.ed.gov/?id=EJ1353386); [ACM](https://dl.acm.org/doi/abs/10.1109/TE.2022.3155884)
- Instructors report that live coding lets them model good habits and conventions. They also report barriers such as performance pressure ("gladiator ring") — [Live Coding: Instructors' Perspectives, arXiv 2025](https://arxiv.org/html/2506.03402); [Barriers and Benefits of Live Coding, arXiv 2025](https://arxiv.org/html/2504.02585)
- Expertise reversal: worked examples helped learners with little prior knowledge but lost their effect, and even hampered learning, for more knowledgeable learners. Guidance that removes load for novices adds load for experts — [Kalyuga 2007, Educational Psychology Review](https://link.springer.com/article/10.1007/s10648-007-9054-3); [overview](https://en.wikipedia.org/wiki/Expertise_reversal_effect)
- Self-explanation prompts: 64 reports, 69 effect sizes, overall g = 0.55 (random effects). This covers studying worked problems, solving problems, and studying text — [Bisra et al. 2018, EPR](https://link.springer.com/article/10.1007/s10648-018-9434-x); [BPS digest (~6,000 participants)](https://www.bps.org.uk/research-digest/self-explanation-powerful-learning-technique-according-meta-analysis-64-studies)

### Inferences

#### Technique 1.1: Decision-point narration (modeling on finished code)
**Steps.**
1. Pick one component whose core is 30-80 lines.
2. Before showing the code, list its 3-5 decision points: where a reasonable engineer could have done something else.
3. Walk the code top-down. At each decision point, narrate four beats in the expert's voice: *what I noticed* (the cue or force), *what I considered* (2-3 options), *what I chose*, and *what would break with the others*.
4. Skip narration on plumbing. Link it and move on.
5. End by restating the decision points as a numbered list; the learner will be asked about these later.

**Worked example (one retry layer per call).** At the node that calls web search, narrate: "Cue: this node makes one external call that isn't a model. Options: (a) no retry, (b) retry here with `TRANSIENT_RETRY` and `retry_on=is_transient`, (c) retry here *and* in the tool. I chose (b) because the provider SDK already retries model calls and the model fallback already switches providers. If this node also contained a model call, a node retry would re-run it. That's why the rule is one external dependency per node. Option (c) stacks layers: if each layer tried 3 times, one flaky call could become up to 9 or 27 attempts against a rate-limited API."

**When it works / failure modes.** Works when the narration is about *forces*, not syntax. It fails in three ways: (a) narrating everything, which buries the 3-5 decisions in plumbing; (b) presenting the choice as obvious, which hides the alternatives (the curse of knowledge); (c) for this learner, continuing to narrate after the learner can already produce the rationale. That last one is expertise reversal, so fade it (1.3).

#### Technique 1.2: Predict, then reveal (coaching)
**Steps.**
1. Show the problem and the forces (not the code).
2. Ask for a one-line prediction: "Where would you put the retry, and how many layers?"
3. Reveal the code.
4. Ask the learner to self-explain the difference between the prediction and the code: "Which force did the code respond to that your prediction didn't?"
5. Coach only on the gap.

**Worked example (failure envelope).** Before showing `run_*`: "A web-search specialist times out. What should the coordinator receive?" A typical prediction is "an exception". Reveal the `failed` envelope with `failure_reason`, then ask: "Why would anything `failure_kind` can't classify still raise?" The answer: an unclassified failure is a bug, and swallowing it would hide defects behind a normal-looking result.

**When it works / failure modes.** Self-explanation (g = 0.55) is the evidence anchor. Prediction fails when the forces weren't given first, because the learner then guesses. It also fails when the reveal comes with an immediate full explanation, which removes the self-explanation step.

#### Technique 1.3: Fading ladder across a project
Four support levels per recurring decision type (retries, failure contracts, HITL, state reset):
- **L1:** The mentor narrates (1.1).
- **L2:** The mentor asks, with a hint about which force to look for.
- **L3:** The mentor asks with no hint.
- **L4:** The learner critiques a *new* variant the mentor wrote (for example, a node with two external calls).

Move up a level after two correct unaided answers on that decision type, and drop back one level after a miss.

**Failure modes.** Fading on a schedule instead of on performance. Starting a strong learner at L1, which is the expertise-reversal cost; with this learner, begin at L2 for any decision type already seen in an earlier project.

#### Technique 1.4: Articulation card (one paragraph, learner's words)
After each topic, the learner writes 3-5 sentences in a fixed shape: *force → decision → mechanism → rejected alternative → what breaks if violated*. The mentor gives feedback on the card (section 6). The cards become the material the learner defends at project close.

**Failure mode.** Accepting a card that paraphrases the ADR. Require at least one element that is not in the ADR: an original failure scenario or a load condition.

#### Technique 1.5: Reflection as a rationale diff
After a reveal (1.2 or 2.2), the learner writes one line: "What the expert considered that I didn't." This is ShadowBox's reflection step (section 2) and gives the mentor the learner's own gap diagnosis.

#### Technique 1.6: Exploration via a changed force
Near the end of a project, change one force and ask for a redesign. Examples: "the search API now bills per call", "two users share one thread", "the tool now sends email". The learner proposes; the mentor critiques as a reviewer would. This is the transfer test.

### Gaps
- I found no controlled study of design-level (architecture) think-aloud modeling. The live-coding evidence is at the level of coding and debugging, mostly with introductory students, and much of it is self-report.
- I did not retrieve the original Collins, Brown & Newman (1989) text or a software-engineering-specific cognitive apprenticeship evaluation. The ResearchGate chapter "Cognitive apprenticeship in educational practice" surfaced but was not read.

---

## 2. Surfacing tacit expert knowledge for teaching (CTA, Critical Decision Method, decision-point walkthroughs)

### Takeaway
Instruction built on cognitive task analysis (CTA) of experts shows large effects in a small, varied
evidence base. The most directly usable format for a chat mentor is ShadowBox: a scenario interrupted
at decision points; the learner ranks options and writes a rationale; the expert ranking and
synthesized rationale are revealed; the learner writes down what the expert noticed that they missed.

### Cited Findings
- A meta-analysis of CTA-based training found a large overall effect (Hedges' g = 0.871). The authors note substantial variation by method and context and a relatively small evidence base — [Tofel-Grehl & Feldon 2013, JCEDM](https://journals.sagepub.com/doi/abs/10.1177/1555343412474821); [open PDF](https://digitalcommons.usu.edu/cgi/viewcontent.cgi?article=1346&context=itls_facpub)
- The Critical Decision Method (CDM) is a CTA method of multiple-pass retrospection over a real incident, guided by probe questions. It has been used with design engineers and computer programmers among other experts, for system development and instructional design. A two-hour interview often yields 20-30 transcript pages — [Hoffman, Crandall & Shadbolt 1998, Human Factors](https://journals.sagepub.com/doi/10.1518/001872098779480442); [Semantic Scholar](https://www.semanticscholar.org/paper/Use-of-the-Critical-Decision-Method-to-Elicit-A-in-Hoffman-Crandall/ee0c190ab6c6079a648f4f8d9fd70882a9b216c8)
- **ShadowBox mechanics** (Klein & Borders 2016, full text read):
  - A realistic scenario is periodically interrupted by decision points.
  - The trainee rank-orders typically 3-6 options. The decision questions are which action to take, which goals to prioritize, which cues to monitor, and what information to seek.
  - The trainee writes a rationale, then sees the expert panel's rankings plus a synthesized rationale.
  - The trainee compares rationales and describes "what the SMEs noticed and considered that the trainees had not".
  - There is no claim of one correct answer, and a minority expert view is included where experts disagreed.

  — [Klein & Borders 2016, JCEDM](https://journals.sagepub.com/doi/abs/10.1177/1555343416636515); [PDF](https://www.shadowboxtraining.com/wp-content/uploads/2021/05/The_ShadowBox_Approach_to_Cognitive_Skills_Trainin.pdf)
- **ShadowBox evidence** (same source):
  - Evaluation 1: 3 hours of nonfacilitated paper training, U.S. Marines, N = 59. Match to expert rankings improved 28% vs. a no-feedback group.
  - Evaluation 2: 1 hour on a tablet, soldiers, N = 30. Improvement of 21%.
  - Original firefighter study (Hintze 2008): the expert-feedback group improved 18% vs. no feedback (F = 14.09, p < .001).
  - The outcome measure is agreement with expert rankings, not field performance.

  — [Klein & Borders 2016](https://journals.sagepub.com/doi/abs/10.1177/1555343416636515)
- Klein & Borders state that Tactical Decision Games run in a small group by a *skilled* facilitator probably train better than ShadowBox ("although we do not have data"). They report disappointing results with mediocre facilitators, because TDGs don't specify how to evaluate responses or query reasons — [Klein & Borders 2016 PDF](https://www.shadowboxtraining.com/wp-content/uploads/2021/05/The_ShadowBox_Approach_to_Cognitive_Skills_Trainin.pdf)
- They also give a reason for the method: subject-matter experts are good at the skill but often not at teaching it, which makes expert availability the bottleneck in cognitive-skill training — same source

### Inferences

#### Technique 2.1: Mentor-side CDM on the code before the lesson (surfacing)
The mentor is the one who "interviews" the expert artifacts (ADR, design card, engineer's notes, commit history) before teaching. When a rationale is missing, the mentor sends a request to the engineer or lead.

**Steps**, following the CDM's multiple passes:
1. **Incident:** pick the concrete event or force that triggered the decision (for example, "RunnableWithFallbacks re-raised the primary's error").
2. **Timeline:** what happened in what order, and what the code looked like before.
3. **Deepening probes** per decision point: What cue signaled a problem? What were the goals? What options existed? Why was this one chosen? What would a less experienced engineer have done?
4. **What-if probes:** what if the load were 100x, the tool were irreversible, or the provider were down for an hour?
5. Output a **decision requirements table**, one row per decision: cue | decision | rule | why | typical novice error | what breaks if violated.

The typical-novice-error column is what makes the table teachable.

**Worked example (ADR-0007 built-in model fallback).** Row:
- **Cue:** a provider outage or rate limit on the primary model.
- **Decision:** `make_model_fallback(tier, primary=provider)` and never a manual retry wrapper.
- **Rule:** bind structured output to each model *before* `with_fallbacks`.
- **Why:** `RunnableWithFallbacks` has neither `bind_tools` nor `with_structured_output`.
- **Novice error:** calling `.with_structured_output()` on the fallback object.
- **Breaks:** an AttributeError at build time; and when every model fails, the error you see is the primary's, which can mislead debugging.

**When it works / failure modes.** It works when ADRs record the context and rejected alternatives. It fails when the mentor fills missing rationale from general knowledge and presents it as the expert's. In that case, mark the row "mentor inference" and ask the owner. Sweep names such as incident/timeline/deepening/what-if follow standard CDM descriptions; see Gaps.

#### Technique 2.2: ShadowBox decision-point lesson (transferring)
**Steps.**
1. Write a 5-10 line scenario in production terms (users, load, failure).
2. Stop at one decision point and offer 3-5 plausible options. Include the one the codebase chose, one a competent novice would choose, and one that is fine at small scale but breaks at production load.
3. The learner ranks all options and writes a rationale of 2-4 sentences.
4. Reveal the expert ranking with a synthesized rationale, including a minority view where one is honest (for example, a defensible alternative the lead rejected).
5. The learner writes "what the expert noticed that I didn't", and the mentor adds feedback only on that delta.
6. Record the delta in the learner's gap log.

**Worked example (human approval before a consequential tool).** Scenario: "The P4 interpreter agent can run shell commands in a sandbox. A user asks it to clean up old files." Decision: "Which safeguard matters most?" Options:
- (A) A stronger system prompt forbidding deletions.
- (B) `HumanInTheLoopMiddleware` on `execute`, with an `InterruptOnConfig` `when` predicate that narrows it per call by args.
- (C) Confine the file tools with `virtual_mode=True`.
- (D) Pass `build_sandbox_env()` so the shell gets no secrets.

Expert ranking with rationale: B and D are both boundaries, and neither can substitute for the other. D protects secrets (ADR-0005); B protects against irreversible actions. C does *not* confine shell commands (a Gotchas entry). A is not a control at all: low-tier models sometimes claim actions they never took. The minority view, that D is ranked above B, is defensible when secret exposure is the worse failure. What the learner typically misses: that `virtual_mode` confines file tools but not the shell.

**When it works / failure modes.** It works because the options carry the tacit discriminations (the cue the expert watches). It fails when:
- the options are strawmen, so the learner ranks by elimination;
- one option is framed as "the right answer" with no rationale, turning it into a quiz;
- the rationale step is skipped, since the evidence is for rank-plus-rationale-plus-comparison;
- scenarios are too far from the code the learner actually reviewed.

### Gaps
- I did not verify the exact CDM sweep names and probe lists from a primary source this session. They follow the standard description (Crandall, Klein & Hoffman, *Working Minds*, 2006), which I did not retrieve. The Hoffman et al. abstract confirms only "multiple-pass" retrospection "guided by probe questions".
- No ShadowBox study in software engineering was found. All evaluations are military, fire, or police, and they measure match to expert rankings, not transfer to real work.
- The Tofel-Grehl & Feldon effect size (g = 0.871) comes from a small, heterogeneous set of studies, mostly medical and procedural. Its transfer to design judgment is unverified.

---

## 3. Teaching with decision records (ADR reading, reconstruct-the-decision, kata, design review, case method)

### Takeaway
I found no controlled study of ADR-reading exercises. The strongest nearby evidence supports asking
the learner to work on the problem and contrast cases *before* being told the answer (contrasting
cases, then telling; problem solving before instruction). That makes "reconstruct the hidden
decision, then read the ADR" the best-supported ADR format. Architecture katas and role-based decision
exercises have only experience-report-level support.

### Cited Findings
- Schwartz & Bransford 1998: in 3 classroom studies, college students who analyzed contrasting cases and *then* heard a lecture did substantially better than those who read feature descriptions, summarized text, or analyzed cases twice with no lecture. Noticing distinctions creates "a time for telling" — [A Time for Telling (PDF)](http://aaalab.stanford.edu/assets/papers/earlier/A_time_for_telling.pdf); [summary by L. Margulieux](https://laurenmarg.com/2023/05/03/article-summary-schwartz-bransford-1998-a-time-for-telling-constructivism/)
- Productive failure meta-analysis: 53 studies, 166 comparisons, over 12,000 participants. Problem solving followed by instruction beat instruction followed by problem solving, g = 0.36 [0.20-0.51], and g = 0.37-0.58 with high fidelity to productive-failure design. The effect favored instruction-first for young children (grades 2-5) and for domain-general skills — [Sinha & Kapur 2021, Review of Educational Research](https://journals.sagepub.com/doi/10.3102/00346543211019105); [PDF](https://janfasen.nl/wp-content/uploads/2023/05/Sinha-and-Kapur-PS-I.pdf)
- Teaching architecture decision making: two experiments at a Spanish university. Undergraduates took roles in collaborative decision tasks and used a decision-modeling tool to capture and *challenge* design decisions. The authors note that novices' decision processes are fragmented and non-linear and that cognitive bias makes the topic hard to teach — [Springer chapter, 2020](https://link.springer.com/chapter/10.1007/978-3-030-58923-3_16); [ResearchGate](https://researchgate.net/publication/344273829_Teaching_Students_Software_Architecture_Decision_Making)
- **Architectural kata in a software architecture course** (ECSEE 2023 experience report, full text read):
  - Format: 26 students in 5 teams of 5-6, 40 minutes to identify drivers and design, then a presented "vision" with peer questions and voting.
  - Survey: 11 of 26 responded (42%). Students reported gains in identifying non-functional requirements, elaborating assumptions, and trade-off decision making.
  - Problems: 40 minutes was insufficient, and 20% felt it gave limited help with evaluation assignments.
  - Ted Neward's original format has three phases (discussion, peer review, voting), with the moderator playing the customer.

  — [ACM](https://dl.acm.org/doi/10.1145/3593663.3593694); [PDF](https://www.diva-portal.org/smash/get/diva2:1786035/FULLTEXT01.pdf)
- Kata practitioners advise asking participants to note the decisions that required trade-offs as they go, because those make the richest debrief — [search summary of kata practice sources](https://www.grahamlea.com/2015/08/design-kata-learn-software-architecture/) (practitioner blog; not independently verified)

### Inferences

#### Technique 3.1: Reconstruct the decision (hidden-decision ADR)
**Steps.**
1. Give the ADR's Context and forces only; hide the Decision, Consequences, and Alternatives.
2. The learner writes (a) a decision, (b) two alternatives they rejected and why, and (c) one consequence they expect to hurt.
3. Reveal the full ADR.
4. The learner diffs: what matches, what the ADR weighed that they didn't, and any consequence they found that the ADR doesn't list.
5. The mentor gives feedback on the diff (section 6), not on the whole answer.

**Worked example (ADR-0006, remove agent registry).** Context given: "Agents were looked up by name from a registry; there was one consumer per agent." The learner proposes keeping it "for extensibility". After the reveal, the diff names the rule the ADR applied (Principle 3: an observed shape before abstraction; one consumer means keep it local) and asks when the decision should flip: "What trigger (how many identical instances) would justify a registry again?"

**When it works / failure modes.** Productive-failure evidence supports struggling first, *then* receiving the canonical explanation. That means the reveal must be a full explanation, not just "here's the answer". Failure modes:
- hiding forces that the ADR's context only implies, so the learner can't possibly reconstruct the decision;
- ADRs with no Alternatives section (fix the record first, via the lead);
- using it on a decision type the learner has already mastered, which is expertise reversal again.

#### Technique 3.2: Contrasting code pair
**Steps.**
1. Show two short versions of the same component that differ in exactly one design decision.
2. Ask: "Which one would you ship, and what failure does the other invite?"
3. Only after the learner names the distinction, deliver the rule and its ADR link: the "time for telling".

**Worked example (workflow vs agent).**
- Version A: a `StateGraph` with fixed nodes (retrieve → grade → answer).
- Version B: an agent that has `retrieve` as a tool and decides when to call it.

Distinctions to discover: A has a fixed path, predictable cost and latency, per-node retries, and node-level tests. B adapts to open-ended questions but may skip retrieval or loop, and its behavior is only testable with a scripted fake model. The rule to tell afterwards: use a workflow when the steps are known in advance, and an agent when the path depends on intermediate results.

**Failure modes.** Pairs that differ in more than one dimension, which makes the contrast unreadable. Telling the rule before the learner has noticed the difference.

#### Technique 3.3: Design review simulation (solo kata)
**Steps.**
1. The mentor plays customer and reviewer panel.
2. Give a short requirement with a production force, for example: "the brief agent now runs nightly for 10,000 users."
3. The learner has a timebox and presents in 5-8 lines: drivers, decision, rejected alternative, risk.
4. The mentor asks 3 reviewer questions from the ladder in section 4.
5. Verdict: approve, approve with changes, or reject, with reasons.
6. The learner writes one line on the trade-off they'd defend.

**When it works / failure modes.** Evidence is experience-report only (the ECSEE kata report). Timeboxes that are too short were the main reported problem, so allow at least one follow-up round. Solo katas lose peer critique; the mentor must actively play a skeptic rather than approve.

#### Technique 3.4: ADR ablation
"Delete this decision. Walk me through the first incident in production." The learner narrates the failure chain step by step.

**Example (ADR-0003, identity via runtime context).** "Drop `context=UserContext(...)` and read `user_id` from `configurable` inside the store factory." Expected chain: `Runtime` has no `config`, so identity silently becomes the default. Every user then writes to one namespace, which becomes a cross-tenant memory leak.

### Gaps
- No controlled evidence was found for ADR-reading or reconstruct-the-decision exercises specifically, for studio critique in software engineering, or for the engineering case method. I did not search the latter two this session because of the budget.
- Schwartz et al. 2011, "Practicing versus inventing with contrasting cases" (Journal of Educational Psychology), surfaced but was not read — [PDF](https://cadrek12.org/sites/default/files/Schwartz.Chase_.Oppezzo.Chin_2011_PracticingVsInventing.pdf).

---

## 4. Questions that teach trade-offs ("what breaks if", "what force made this necessary", "at 100x load", counterfactual and ablation)

### Takeaway
The evidence behind these questions is indirect: self-explanation prompts (g = 0.55) and ShadowBox's
four decision-question types (action, goal priority, cues to monitor, information to seek). No study
compared specific trade-off question formats. A fixed question ladder, asked in order, is the
practical form.

### Cited Findings
- Self-explanation prompts improve learning, g = 0.55 over 64 reports. The effect was examined across the kinds of prompts used and the type of learning task — [Bisra et al. 2018](https://link.springer.com/article/10.1007/s10648-018-9434-x)
- ShadowBox decision questions are not only "which action". They also ask which goals to prioritize, which cues to monitor, and what information to seek — [Klein & Borders 2016](https://journals.sagepub.com/doi/abs/10.1177/1555343416636515)
- The CDM uses "what-if" style probes as part of its multi-pass retrospection (hypothetical variations on an incident) — [Hoffman, Crandall & Shadbolt 1998](https://journals.sagepub.com/doi/10.1518/001872098779480442) (probe-level detail not verified; see section 2 gaps)
- Novice architects struggle to compare technological alternatives and move from problem to solution space — [Teaching Students Software Architecture Decision Making, 2020](https://link.springer.com/chapter/10.1007/978-3-030-58923-3_16)

### Inferences

#### Technique 4.1: The trade-off question ladder
Ask the questions in this order; each assumes the previous answer.
1. **Force:** "What made this necessary? What goes wrong without it?"
2. **Mechanism:** "Exactly how does the code stop that from happening? Point to the line."
3. **Breakage:** "What breaks if we remove it or do it the obvious way?" (ablation)
4. **Scale:** "What changes at 100x users, concurrent threads, or a 1-hour provider outage?"
5. **Cost:** "What does this decision cost: latency, complexity, a failure mode it introduces?"
6. **Alternative:** "What's the strongest rejected alternative, and when would it win?"
7. **Reversal condition:** "What observation would make you undo this decision?"

**Worked example (one retry layer per call).**
1. Force: retries multiply and re-run expensive or non-idempotent work.
2. Mechanism: `TRANSIENT_RETRY` on the node with `retry_on=is_transient`, and one external dependency per node.
3. Breakage: wrap a model call in node retry, and every retry repeats the model call, on top of SDK retries and fallback.
4. Scale: stacked retries amplify load on a provider that is already rate-limited (a retry storm).
5. Cost: more nodes.
6. Alternative: a single global retry policy.
7. Reversal condition: if a provider SDK stopped retrying, the rule for model calls would change.

**When it works / failure modes.** It works when the learner must point to code at step 2, which blocks fluent-sounding but ungrounded answers. It fails when the mentor asks steps 4-7 before 1-3 are solid, which produces speculation without a mechanism. Asking all seven every time also fails: pick the 2-3 that carry the lesson.

#### Technique 4.2: Counterfactual swap (one force at a time)
Change a single premise and ask for the smallest design change. Examples:
- "The specialist's result is consumed by a batch job, not a coordinator. Does the envelope-instead-of-raise decision still hold?" Answer: yes, and more strongly, because partial results beat a crashed batch.
- "The tool is read-only. Is HITL still required?" Answer: no. HITL is for consequential tools, and the `when` predicate narrows it per call.

### Gaps
- I found no study comparing specific trade-off question formats (ablation vs. scale vs. counterfactual) for software design. The ladder is synthesis.

---

## 5. Teach-back / learning-by-teaching protocols

### Takeaway
Preparing to teach and then actually teaching produce moderate gains (g ≈ 0.35 and 0.56), larger
when the learner expects to teach directly. The gain depends on the learner *building* knowledge
rather than *telling* it, and tutee questions are what trigger that. So a teach-back is only as good
as the mentor's probing.

### Cited Findings
- Kobayashi 2019 meta-analysis of 28 studies: preparing-to-teach g = 0.35; teaching after preparing g = 0.56. Effects held for deep and surface learning and after a delay. Expecting to teach directly gave g = 0.50 vs. 0.27 for indirect teaching — [Kobayashi 2019, Japanese Psychological Research](https://onlinelibrary.wiley.com/doi/10.1111/jpr.12221)
- Roscoe & Chi 2007 review: peer tutors show a pervasive "knowledge-telling bias", delivering knowledge rather than building it, even when trained. Tutee questions moved tutors toward reflective knowledge-building, and tutors who engaged in knowledge-building showed the largest gains in deep learning — [Roscoe & Chi 2007, Review of Educational Research](https://journals.sagepub.com/doi/abs/10.3102/0034654307309920)
- A 2024 meta-analysis examines interactivity as a moderator of learning by preparing to teach and teaching — [Kobayashi 2024, Educational Psychology Review](https://link.springer.com/article/10.1007/s10648-024-09871-4) (abstract not read; effect sizes not verified)
- Interactivity is proposed as a potential determinant of learning by teaching — [Frontiers in Psychology 2018](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2018.02755/full) (not read in full)

### Inferences

#### Technique 5.1: Teach-back with a probing tutee (project-close defense)
**Steps.**
1. **Announce it early.** At the start of a project, tell the learner they will teach one component to "a new engineer joining the team" at close. Direct-teaching expectancy had the larger effect.
2. **The teach.** The learner explains one design decision in 8-12 lines, with no ADR open.
3. **The mentor plays a specific tutee,** such as a competent engineer who has never seen LangGraph, or a skeptical reviewer. It asks 3-5 deep questions from the ladder in section 4: why-not questions, what-if questions, and "show me the line".
4. **Score** each decision on six elements, 0/1 each:
   1. claim (what was decided);
   2. force (why it was needed);
   3. mechanism (how the code enforces it);
   4. rejected alternative (with its winning condition);
   5. failure mode if violated;
   6. boundary (where the rule stops applying).
5. **Handle gaps by type:**
   - A missing force or mechanism is a knowledge gap. Re-teach with a contrasting pair (3.2), then re-probe in the next session.
   - A missing alternative or boundary is a judgment gap. Assign a ShadowBox item (2.2) on that decision type.
   - A wrong claim is a misconception. Use a refutation move (6.1).
6. **Log it.** Record the score per decision in the gap log. Close the project only when every core decision scores at least 5/6. (That threshold is my choice, not from a source.)

**Worked example (specialists return an envelope instead of raising).** The learner teaches: "Specialists return `failed` with `failure_reason` so the coordinator doesn't crash." The mentor-as-tutee asks:
- "So do you catch every exception?" This probes the boundary. Expected answer: no. Anything `failure_kind` can't classify raises, because it's a bug.
- "Why not let the coordinator catch?" This probes the alternative: it would couple every caller to every specialist's failure types, and the typed contract is lost.
- "Where does the retry happen, then?" This probes the link to the retry rule: inside the specialist, one layer, before the envelope is built.

**When it works / failure modes.** It works when the questions force knowledge-building. It fails when the mentor-tutee nods along, which lets the knowledge-telling bias run unchecked; when the learner reads the ADR back instead of explaining it; and when the rubric gets scored but the gap never gets re-probed.

### Gaps
- I found no validated rubric for scoring design-rationale teach-backs. The six-element rubric is synthesis. I did not research health-care teach-back protocols this session.

---

## 6. Feedback on the learner's answers

### Takeaway
Feedback helps on average, but it varies widely and backfires in a large minority of cases. It works
best when it is information-rich, covering what was wrong, why, and how to fix it, and it gets worse
as it moves toward the self, as praise does. Explicitly naming and refuting a misconception beats
simply presenting the correct view.

### Cited Findings
- Wisniewski, Zierer & Hattie 2020: 435 studies, 994 effect sizes, over 61,000 participants. Overall d = 0.48 with high heterogeneity. By type:
  - high-information feedback: d = 0.99;
  - corrective feedback: d = 0.46;
  - reinforcement/punishment: d = 0.24.

  Feedback had more impact on cognitive and motor outcomes than on motivational ones. The paper summarizes that students benefit most when feedback shows what the mistakes were, why they were made, and how to avoid them — [Frontiers in Psychology](https://www.frontiersin.org/articles/10.3389/fpsyg.2019.03087/full)
- Kluger & DeNisi 1996: 607 effect sizes and 23,663 observations. Average d = 0.41, but 38% of feedback interventions *decreased* performance. Effectiveness drops as feedback moves attention up from the task toward the self — [Hebrew University record](https://cris.huji.ac.il/en/publications/the-effects-of-feedback-interventions-on-performance-a-historical/); [ResearchGate](https://www.researchgate.net/publication/232458848_The_Effects_of_Feedback_Interventions_on_Performance_A_Historical_Review_a_Meta-Analysis_and_a_Preliminary_Feedback_Intervention_Theory)
- Refutation text meta-analysis: g = 0.41 over 44 comparisons and 3,869 participants vs. non-refutation conditions — [Schroeder & Kucera 2022, PubMed](https://pubmed.ncbi.nlm.nih.gov/35095236/). A larger 2024 meta-analysis (76 studies, 294 effect sizes) found a consistent advantage of refutation texts for confronting misconceptions — [Educational Psychologist](https://www.tandfonline.com/doi/abs/10.1080/00461520.2024.2365628)
- The task / process / self-regulation / self levels come from Hattie & Timperley (2007). Wisniewski et al. describe high-information feedback as information at the task, process, and sometimes self-regulation level — [Wisniewski et al. 2020](https://www.frontiersin.org/articles/10.3389/fpsyg.2019.03087/full)

### Inferences

#### Technique 6.1: Five-part feedback on a design answer
**Steps.**
1. **Locate:** quote the specific claim being judged.
2. **Verdict on the claim,** not the person: correct, partly correct, or wrong.
3. **What's right,** at process level (for example, "you traced the failure from the tool up to the coordinator").
4. **The gap:** the missing force, mechanism, or boundary, and *why it matters* in one line.
5. **Feed-forward:** one question or micro-task the learner answers next, one that forces them to use the correction.

**Refutation variant (for a misconception):** name the wrong model → say plainly that it's wrong → show the specific case where it fails → give the correct model → have the learner re-predict that case. (This four-move structure is how refutation texts are commonly described; I did not verify it against the meta-analyses.)

**Worked example.** The learner says: "`virtual_mode=True` makes the interpreter safe."
1. Verdict: partly correct.
2. Right: file tools *are* confined.
3. Gap: the shell is not confined. `virtual_mode` confines the file tools, not shell commands, so a shell command can read outside the sandbox root. That's why ADR-0005 adds `build_sandbox_env()` and why `execute` needs HITL.
4. Feed-forward: "Which of our three controls stops `cat ../../.env` in the shell, and which stops `rm -rf` of the sandbox?"

**Avoid:**
- Generic praise ("great answer!"), which is self-level;
- vague notes ("think about failure more");
- correcting everything at once;
- giving the full correct answer with no feed-forward task, which is corrective-only feedback with the smaller effect.

### Gaps
- None of these meta-analyses isolates advanced adult learners in software design. I did not read the Hattie & Timperley 2007 original this session.

---

## 7. Explanation craft for technical teaching in text

### Takeaway
Start concrete and fade to the abstract rule. Use one realistic running example, introduce one
concept at a time, explain why before what, and say explicitly when you're showing the wrong way.
Julia Evans' catalog of confusing-explanation patterns works as a practical checklist for chat
lessons.

### Cited Findings
- Concreteness fading, a systematic review in math and science: begin with concrete representations, then explicitly and gradually fade to the abstract. Proposed benefits include grounding opaque symbols and stripping away extraneous concrete detail to reach the generalizable structure — [Fyfe, McNeil, Son & Goldstone 2014, EPR (ERIC)](https://eric.ed.gov/?id=EJ1036777); [PDF](https://www.researchgate.net/profile/Emily-Fyfe/publication/262943993_Concreteness_Fading_in_Mathematics_and_Science_Instruction_A_Systematic_Review/links/54b69f030cf2e68eb27eb926/Concreteness-Fading-in-Mathematics-and-Science-Instruction-A-Systematic-Review.pdf)
- **Julia Evans, "Patterns in confusing explanations"** (paraphrased):
  1. Outdated assumptions about the reader.
  2. Inconsistent assumed knowledge; pick one specific reader.
  3. Strained analogies; keep them to 1-2 sentences, one idea.
  4. Illustrations that don't match the tone.
  5. Unrealistic examples.
  6. Meaningless jargon.
  7. Missing key information.
  8. Too many concepts at once.
  9. Starting abstract.
  10. Unsupported statements.
  11. No examples.
  12. Showing the "wrong" way without saying it's wrong.
  13. "What" without "why".

  — [jvns.ca](https://jvns.ca/blog/confusing-explanations/)
- Evans aims to explain without dumbing down or leaving out the important technical parts, writing like one human talking to another — [jvns.ca home](https://jvns.ca/); [Chris Coyier on Evans](https://chriscoyier.net/2023/09/06/julia-evans-on-blogging/)

### Inferences

#### Technique 7.1: Concrete trace → pattern → rule → boundary (concreteness fading in text)
**Steps.**
1. **Concrete trace:** one real run, for example "the Tavily call timed out at 14:02; here are the three attempts in the log".
2. **Pattern:** "the node retried; the model call didn't repeat because it lives in another node".
3. **Rule:** quote the one-line rule and link its owning file (AGENTS.md convention 11).
4. **Boundary:** "the rule doesn't apply to model calls, which get SDK retries plus fallback".

Keep the same running example across the whole topic.

**Failure mode.** Staying concrete and never stating the rule, which leaves the lesson unfaded; the learner then can't recognize the pattern in new code.

#### Technique 7.2: Pre-send checklist for a chat lesson (from Evans' patterns)
1. Does every term appear with an example the first time?
2. Is there exactly one new concept in this message?
3. Is the "why" stated before the mechanism?
4. Is any analogy one or two sentences, tied to something the learner already knows (for example, "retry layers are like nested `try/except` loops, each multiplying attempts")?
5. If I show the wrong design, do I say "this is the wrong version" first?
6. Is the example realistic, meaning real code from this repo rather than `foo/bar`?

### Gaps
- Budget did not allow retrieving Josh Comeau's, Bartosz Ciechanowski's, or Stripe/Google engineering-education writing. I cannot cite their specific techniques. The research on progressive disclosure, signposting, and the curse of knowledge was not retrieved either.

---

## 8. Industry mentoring practices that transfer (pairing, review-based mentoring, onboarding)

### Takeaway
Code review in industry turns out to be less about finding defects and more about knowledge
transfer, team awareness, and generating alternative solutions. That makes "the learner reviews the
engineer's PR, and the mentor reviews the review" a natural fit for a review-not-type learner. Pair
programming evidence favors less-skilled partners and complex tasks for quality, with effort costs.

### Cited Findings
- Bacchelli & Bird 2013 (Microsoft; observation, interviews, surveys, and classified review comments): finding defects is the main *motivation* for review, but reviews turn out to be less about defects than expected. They also deliver knowledge transfer, team awareness, and alternative solutions. Understanding the code and the change is the key reviewing need, and tools meet it poorly — [ICSE 2013 PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/ICSE202013-codereview.pdf); [Microsoft Research](https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/)
- Hannay, Dybå, Arisholm & Sjøberg 2009, a pair-programming meta-analysis:
  - small positive effect on quality;
  - medium positive effect on duration;
  - medium negative effect on effort.

  Pairing yielded higher quality on complex tasks and was faster on simple ones; less-skilled pairs benefited most. There were signs of publication bias — [Information and Software Technology](https://www.sciencedirect.com/science/article/abs/pii/S0950584909000123); [ACM](https://dl.acm.org/doi/10.1016/j.infsof.2009.02.001)

### Inferences

#### Technique 8.1: Review the engineer's PR, then get the review reviewed
**Steps.**
1. The learner gets a real PR diff from the engineer and a review charter: "find the 3 decisions in this diff, name the force behind each, and write one question you'd ask the author".
2. The learner posts the review, in chat.
3. The mentor reviews the review: missed decisions, questions that were really requests for information versus questions that probed a decision, and any misread code.
4. The mentor asks the learner to answer their own best question from the code.

**Worked example.** A diff that adds `ToolRetryMiddleware` to an agent's search tool. A good review finds three things:
- (a) the retry is scoped to the tool, not the agent loop;
- (b) `retry_on=is_transient`, so a 400 isn't retried;
- (c) no node-level retry was added around the agent, so there's still one layer.

A missed item, for example not noticing (c), becomes a ShadowBox item.

**When it works / failure modes.** It fails when the charter is absent, so the learner comments on style; or when the PR is too large, since the study found understanding the change is the bottleneck.

#### Technique 8.2: Learner-as-navigator pairing
The learner directs a small change in words, and the mentor or engineer types. This matches review-not-type, and the learner must articulate each decision before it's made. Use it for complex design changes, where the quality benefit is reported, not routine edits.

**Failure mode.** The typist silently fixes the learner's design, which hides the gap. Type what was said, and let the test or review reveal the flaw.

### Gaps
- I did not retrieve onboarding-program research (for example, Google or Microsoft onboarding studies) or evaluations of "strong-style" pairing, so neither can be cited here.
