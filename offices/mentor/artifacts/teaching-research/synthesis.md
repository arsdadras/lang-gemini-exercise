# Rebuild the teach skill around verified probes

The five notes agree on one design fact: AI tutoring helped when the tutor carried an
expert-verified answer and the learner still did the thinking, while unguarded help raised
practice scores and then lowered independent performance
([Bastani et al. 2025](https://www.pnas.org/doi/10.1073/pnas.2422633122);
[Kestin et al. 2025](https://www.nature.com/articles/s41598-025-97652-6);
[Shen & Tamkin 2026](https://www.anthropic.com/research/AI-assistance-coding-skills)). For a
learner who reviews verified code by design, the rule to carry over is "don't do the
understanding for them". The current `teach` skill already has the right skeleton (prediction
first, why and what-if, failure-first hooks, variance runs), so the gains are in precision: write
each question's expected answer before asking it, let the prediction answer decide how much
scaffolding a mechanism gets, show competing designs before naming the chosen one, refute
misconceptions, script demos and labs failure-first, and run the teach-back as a probed defense
scored per decision. Evidence is strong (meta-analyses) for feedback content, self-explanation,
learning by teaching, problem-before-instruction, and retrieval; it is novice-only or indirect for
nearly every code-reading technique; and no study measures what experienced developers learn
from reviewing verified code. SKILL.md stays near its current length and points to three new
reference files.

Notes cited by alias and section: **CR** [code_reading_and_review.md](code_reading_and_review.md),
**DJ** [design_judgment_transfer.md](design_judgment_transfer.md), **AT**
[ai_tutor_behavior.md](ai_tutor_behavior.md), **LM** [lesson_materials.md](lesson_materials.md),
**AE** [teaching_ai_engineering.md](teaching_ai_engineering.md). Checked against the skill's
four files ([SKILL.md](../../.claude/skills/teach/SKILL.md),
[questions.md](../../.claude/skills/teach/questions.md),
[ai-engineering.md](../../.claude/skills/teach/ai-engineering.md),
[evidence.md](../../.claude/skills/teach/evidence.md)), the [charter](../../README.md), and the
lead's [pedagogy](../../../../library/teaching/pedagogy.md).

## 1. Bottom line: eight changes carry most of the value

1. **Fix the expected answer first:** write each question's answer and the misconception behind each likely wrong answer before asking; judge against that note; a wrong answer hears "not right" in sentence one.
2. **Probe, then scaffold:** the component's prediction question doubles as a probe, and its answer picks at most one extra technique card; depth follows the mechanism, not the person.
3. **Contrast, then tell, at the architecture step:** forces and competent options first, the learner predicts or ranks, then the decision, its reason, and its record.
4. **A trade-off ladder for "why":** force, mechanism ("point at the line"), breakage, scale, cost, alternative, reversal; two or three rungs, one question per message.
5. **Refute and feed forward:** name the wrong model, show where it fails, have the learner re-predict, end with a question that uses the correction; plumbing is told, never hinted.
6. **Demos and labs failure-first:** closed prediction, failing run before fixed run, one fault per lab, diagnosis as symptom, cause, mechanism, fix; faults never touch `src/`.
7. **Teach-back as a probed defense:** announced at project start, the mentor as a named tutee, six elements scored per decision, gaps routed by type into review items, never a close gate.
8. **Move detail out of SKILL.md** into `techniques.md`, `materials.md`, and `teach-back.md`; give evidence.md a population column and 16 new rows.

## 2. Change list: 30 edits across the four skill files

Strength labels follow evidence.md: MA (meta-analysis or systematic review), RCT, QE, Q
(qualitative), P (practitioner or vendor), Framework, Inference. The word after the semicolon
rates the evidence for *this* learner: strong, moderate, or weak. Proposed file names appear in
backticks because the files don't exist yet.

### SKILL.md (net about +12 lines; any procedure longer than two lines moves to a reference file)

**S1. CHANGE checklist items 3, 6, 7; ADD item 9** ("all eight" becomes "all nine").
- Item 3: "…one concrete example (one request traced before and after the change), the idea named, then the rule and where it stops applying." *DJ §7 (7.1). Evidence: [Fyfe et al. 2014](https://eric.ed.gov/?id=EJ1036777), systematic review, school and college math and science; moderate, novice-leaning.*
- Item 6: "…the last line is the learner's move (at most one question, answerable in one or two sentences) or the next step; no more than two messages in a row end without a question." *AT R5, R9. Evidence: the [study-mode prompt](https://simonwillison.net/2025/Jul/29/openai-introducing-study-mode/) (P) plus ICAP (review); the one-question limit is Inference; weak.*
- Item 7: "**Nothing to choose.** I decide the lesson's design, examples, and order, and give the reason. Predicting or ranking the verified design's choice is a question with a known answer, not a choice handed over." *Reconciles Principle 10 with DJ §2-3.*
- Item 9: "**Wrong versions are labeled.** An alternative, broken, or seeded variant says so in its first line, lives only in the sandbox, and never passes for the verified code." *DJ §7 (7.2); CR §9 step 6. Evidence: [Evans](https://jvns.ca/blog/confusing-explanations/), P; weak, but it protects the verified-code contract.*

**S2. ADD two bullets to *Prepare a topic*.**
- "For every question I will ask: the expected answer (from the code, a test, or a run) and the misconception each likely wrong answer reveals, written before asking. I judge the reply against this note, never against the learner's phrasing." *AT R1, R13. Evidence: [Bastani et al. 2025](https://www.pnas.org/doi/10.1073/pnas.2422633122), RCT, about 1,000 high-school students (the safe tutor carried the teacher's solution and common mistakes; unguided GPT-4 was wrong 49% of the time); ["Check My Work?"](https://arxiv.org/pdf/2506.10297), preprint benchmark (accuracy moves about 15 points toward the answer the user states); moderate.*
- "Each core component's three to five decision points: force, options, choice, typical wrong choice, what breaks, taken from the ADR, design card, or engineer's notes. A rationale I can't find goes to its owner as a request; I never fill it in from general knowledge." *DJ §2 (2.1). Evidence: [Tofel-Grehl & Feldon 2013](https://journals.sagepub.com/doi/abs/10.1177/1555343412474821), MA of expert-analysis-based training, g = 0.871, few studies, mostly medical; weak for design judgment, and it enforces Principle 4 anyway.*

**S3. CHANGE the *Prepare* bullet** "the demo and hands-on commands (run them)" to "the demo and
hands-on scripts (`materials.md`): commands, expected output, the planted failure, and a saved
output in case the live model misbehaves; I run both." *LM §1 rule 6, §2 rule 5. Evidence:
[instructor interview study](https://arxiv.org/html/2506.03402), Q; weak.*

**S4. CHANGE *Strategy and architecture*, first sentence** (keep the diagram and production-path
sentences): "Forces first, then two or three options a competent engineer might pick, differing
in one decision. The learner predicts which one ships and what failure the other invites; then I
give the decision, its reason tied to a production force (never to volume or 'our CLI doesn't
need it'), and its record (the contrast and rank-and-reveal cards in `techniques.md`)."
*CR §7; DJ §2 (2.2), §3 (3.1-3.2). Evidence: [Schwartz & Bransford 1998](http://aaalab.stanford.edu/assets/papers/earlier/A_time_for_telling.pdf), QE, college; [Patitsas et al. 2013](https://dl.acm.org/doi/10.1145/2493394.2493409), QE, 241 second-year CS students; [Sinha & Kapur 2021](https://journals.sagepub.com/doi/10.3102/00346543211019105), MA, g = 0.36, older learners benefit more; moderate.*

**S5. CHANGE the *Code walkthrough* bullets.**
- Before the code: "What the component is for, and one prediction question a wrong mental model would answer differently. The answer sets the depth (probe card): fluent and purpose-level means no labels or traces, straight to a contrast or what-if; shaky on a new framework mechanism means one sentence of the runtime model, a node-level trace table, and labeled chunks. Depth is per mechanism, not per learner." *CR §10, §6. Evidence: [Kalyuga 2007](https://link.springer.com/article/10.1007/s10648-007-9054-3), review (expertise reversal); [Kalyuga & Sweller](https://link.springer.com/article/10.1007/BF02504800), rapid first-step test, QE, outside programming; [Xie et al. 2018](https://www.benjixie.com/publication/sigcse-2018/), tracing strategy, RCT, 24 intro-course students, about 15% higher; moderate for the probe, weak for traces with experts.*
- After the code: "I narrate only the decision points, each in four beats: cue or force, options, choice, what the others would break. Routine lines get none. Chunks are labeled by purpose the first time a mechanism appears; the next time I mark the chunks and the learner names them." *DJ §1 (1.1); CR §5. Evidence: cognitive apprenticeship (Framework); [Morrison et al. 2015](https://dl.acm.org/doi/10.1145/2787622.2787733), subgoal labels, QE, intro-course (given vs learner-made direction unverified); weak.*
- Questions after: "One 'why this design?' (ladder); after its answer, one 'what if X changed?' that builds on it. When the probe showed fluency, the learner may review the component first as a PR against stated criteria, and my walkthrough becomes the reconciliation (PR card)." *AT R9; CR §1, §9. Evidence: [Bacchelli & Bird 2013](https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/), survey of 873 programmers plus 570 classified comments, and [Sadowski et al. 2018](https://sback.it/publications/icse2018seip.pdf), Google; professionals, knowledge transfer perceived or observed, not measured; weak to moderate.*

**S6. CHANGE *Answering the learner*.** Replace the "Wrong" bullet: "The first sentence says it's
wrong and names the exact error. A misconception gets the refutation move: name the wrong model,
show the one case where it fails, give the right model, have the learner re-predict that case. A
slip gets one hint on the topic's target idea, then the answer. Either way, end with one question
that makes the learner use the correction." Add: "API names, flags, file locations, and other
plumbing are told, never hinted. 'Just tell me' gets the full answer at once, then one short
check." Append to "Never agree": "I change position only on new evidence (a run, the source, a
test) and say which evidence would change it. Praise names the move, and only when earned."
*DJ §6 (6.1); AT R6-R8, R14-R16. Evidence: [Wisniewski et al. 2020](https://www.frontiersin.org/articles/10.3389/fpsyg.2019.03087/full), MA, 435 studies, high-information feedback d = 0.99 vs corrective 0.46; [Schroeder & Kucera 2022](https://pubmed.ncbi.nlm.nih.gov/35095236/), MA, refutation g = 0.41; [Kluger & DeNisi 1996](https://cris.huji.ac.il/en/publications/the-effects-of-feedback-interventions-on-performance-a-historical/), MA, 38% of feedback interventions lowered performance; strong, general populations. [Kapoor et al. 2025](https://arxiv.org/abs/2504.11146), preprint, 885 intro students, half bypassed hint guardrails; moderate for "tell plumbing".*

**S7. CHANGE *Demo*** (keep the variance-run and trace sentences): "Tests first: the learner says
what one key test pins and one thing no test covers. Then a closed prediction (A/B/C, or which
error text appears, plus one sentence why), recorded. We run the case where the naive prediction
fails, the failing run before the fixed one, and I name the idea after the run. Then one what-if
and one 'where in the code is that decided?'." *LM §1; CR §9 step 2. Evidence: [Crouch et al. 2004](https://mazur.harvard.edu/publications/classroom-demonstrations-learning-tools-or-entertainment), QE, physics undergraduates: watching a demo taught no more than no demo, predicting first did; [Rubin 2013](https://www.semanticscholar.org/paper/The-effectiveness-of-live-coding-to-teach-Rubin/8994b3dbf011725aa9a8b8e31a0d2565a9b33920), QE: live coding about equal to static code; moderate.*

**S8. CHANGE *Hands-on scenario*:** "One fault per task, picked for one skill (localize a fault,
read a trace, name the layer that owns a failure). A prediction before the fault run; a diagnosis
after it as symptom, cause, mechanism, fix. The harness judges success: a test name, an output
line, a trace shape. Faults come from env vars, input, stubs, or a sandbox copy, never `src/` or
other repo files; a fault switch the code lacks is a request to the engineer. Hints on request:
where to look, what to compare, the answer." *LM §2. Evidence: [MIT 6.5840 lab design](https://pdos.csail.mit.edu/6.824/labs/lab-raft1.html), course design with no outcome data; novice debugging studies seen only as snippets; weak.*

**S9. CHANGE *Teach-back*:** "Announced at the project start. The learner explains each key
decision with no ADR or code open; I play a named tutee (a competent engineer new to LangGraph, or
a skeptical reviewer) and ask three to five ladder questions; a stall gets a smaller question, not
the answer. Scoring and gap routing: `teach-back.md`." *DJ §5 (5.1); LM §7; AT R19. Evidence: [Kobayashi 2019](https://onlinelibrary.wiley.com/doi/10.1111/jpr.12221), MA, 28 studies, teaching g = 0.56, direct-teaching expectancy 0.50 vs 0.27; [Roscoe & Chi 2007](https://journals.sagepub.com/doi/abs/10.3102/0034654307309920), review: tutors default to telling, and tutee questions push them to build knowledge; strong for students, untested in written chat.*

**S10. CHANGE *Recap and retrieval*:** "Recall before restating. A resumed session opens with the
position marker and one recall question on the last piece; I restate only what the answer shows
is shaky, then give the next step (resume note). One older review item follows. At each topic
start, one retrieval question on an earlier idea the topic reuses, answered before the hook. Now
and then recall is closed-book, with no code on screen." *AT R19, R25, R26; LM §4, §6. Evidence: testing effect and [Dunlosky et al. 2013](https://doi.org/10.1177/1529100612453266) (already cited); classroom spacing is mixed, significant in 2 of 9 courses ([IJ STEM Ed. 2024](https://link.springer.com/article/10.1186/s40594-024-00468-5)), so keep it to one or two questions; moderate.*

**S11. ADD to *Is the understanding real?*:** "A one-sentence purpose check (questions.md,
Purpose) separates purpose-level understanding from line-by-line narration. A self-rating or
'does that make sense?' is never evidence." *CR §3; AT R12. Evidence: [Chen et al. 2020](https://zilles.cs.illinois.edu/papers/EiPE_rubric_sigcse_2020.pdf), rubric validation on 10,024 intro-course answers, explaining correlates with code writing at r = 0.555; moderate, novice.*

**S12. CHANGE *Anti-patterns*.** Replace "A question barrage: at most one question before a
component and two after it" with "More than one question in a message, or 'does that make sense?'
as the check". Add: "Full scaffolding (labels, line-level traces, narration) on a mechanism the
learner already reads fluently"; "A rationale filled in from general knowledge and presented as
the design's"; "Hints for plumbing, or withholding an answer the learner asked for". *CR §10; DJ
§2 (2.1); AT R7-R9, R12.*

**S13. CHANGE *Files*:** one line each for `techniques.md`, `materials.md`, `teach-back.md`.

### questions.md

**Q1. CHANGE the *Prediction* rules; ADD a "State" row.** Rules: "Ask only where a wrong mental
model answers differently; plain wiring gets none. Prefer a checkable answer: a path, a count, a
final value. Options (A/B/C) are fine when an open question would stall; then each wrong option
encodes one named misconception from the map, and the learner adds a one-line reason. After a
miss, one follow-up on the same idea with a new surface." Row: "After X, what does Y hold?", e.g.
"`grade_documents` returns `{"documents": relevant}`. After two rounds, what does `generate`
see?" *CR §1, §8. Evidence: [Lister et al. 2004](https://dl.acm.org/doi/10.1145/1041624.1041673), descriptive, 941 novices in seven countries; Peer Instruction from intro-course classrooms; weak to moderate.*

**Q2. ADD a *Purpose* section:** "In one sentence, at most 15 words: what is this for?" Hide the
docstring. The first time, show a line-by-line answer and a purpose-level answer on a different
fragment. Judge correct, purpose-level, unambiguous; give feedback on the weakest; follow with "for
every input?". Example `route_after_grading`: line-by-line "if documents, generate; else if
retries < MAX_RETRIES, rewrite; else web"; purpose-level "answer from the corpus if grading kept
anything; otherwise rewrite and retry, then fall back to the web." *CR §3; evidence as S11.*

**Q3. CHANGE *Why* into the trade-off ladder:** "Ask in order, two or three rungs per component;
rung 2 always makes the learner point at the line. (1) Force: what made this necessary? (2)
Mechanism: which line stops it? (3) Breakage: what breaks if we remove it or do it the obvious
way? (4) Scale: a hundred users, concurrent threads, an hour-long outage? (5) Cost: what does it
cost? (6) Alternative: the strongest rejected one, and when would it win? (7) Reversal: what would
make us undo it?" Keep the current Contrast, Protection, and Force examples as rungs 6, 3, 1. Add:
"Aim at how parts relate and what the whole is for; atom-level questions only for framework atoms
(`retry_policy`, `NotRequired`, `END`)." *DJ §4 (4.1); CR §2. Evidence: [Bisra et al. 2018](https://link.springer.com/article/10.1007/s10648-018-9434-x), MA, self-explanation prompts g = 0.55 (indirect); the ladder's order is synthesis and the Block Model a Framework without a trial; weak for the order.*

**Q4. CHANGE *What if*:** add a "Force" lever ("The search API now bills per call, or two users
share a thread, or the tool sends email: what is the smallest design change?") and extend
"Remove" with "…then walk the first production incident step by step." *DJ §1 (1.6), §3 (3.4), §4
(4.2); Inference; weak.*

**Q5. CHANGE the *Hint ladder* opening:** "Only for the topic's target idea. Plumbing, API names,
and flags are told outright, and 'just tell me' gets the answer at once plus one check." *AT R7,
R8; evidence as S6, plus the assistance dilemma (Koedinger & Aleven 2007, review).*

**Q6. ADD a *Decision* section, two templates.** Rank and reveal: "(Scenario, five to ten lines in
production terms.) Rank options A-D and give two to four sentences of reasons"; the options
include the design's choice, a competent novice's, and one that breaks only at load; after the
reveal, "What did the design weigh that you didn't?". Reconstruct: "Here are ADR-NNNN's context
and forces. What would you decide, which two alternatives would you reject, what consequence
would hurt?", then the full record and the diff. *DJ §2 (2.2), §3 (3.1). Evidence: [Klein & Borders 2016](https://journals.sagepub.com/doi/abs/10.1177/1555343416636515), field evaluations, Marines (N = 59) matched expert rankings 28% better, soldiers (N = 30) 21%; plus productive failure (MA); weak to moderate, no software study.*

**Q7. CHANGE *Retrieval*:** "Ask for explanation, not recognition ('why does the fallback re-raise
the primary's error, and what does that break?', not 'which error is re-raised?'). At a session
start, one older review item joins the last session's." *LM §4.*

**Q8. CHANGE *Transfer*:** add a topic-close shape, "In three to five sentences: the force, the
decision, the mechanism, the rejected alternative, what breaks if it's violated", rejecting a
paraphrase of the ADR and asking for one element the record lacks. *DJ §1 (1.4). Evidence:
articulation (Framework) plus self-explanation (MA); weak to moderate.*

**Q9. ADD a *Review* section:** "Before the diff: what must a correct change do? Two or three
criteria." "With the tests: which behavior does this test pin, and what stays untested?" "After:
two to four comments in the reviewer's voice: a question, a suggestion, or an approval with its
reason." *CR §9; DJ §8 (8.1); evidence as S5.*

**Q10. CHANGE *Teach-back*:** keep the three prompts; REMOVE the "Scoring" paragraph and point to
`teach-back.md`, which merges the notes' two rubrics.

### ai-engineering.md

**A1. ADD rows to *Misconception map*** under the note "seeded from `AGENTS.md` gotchas; grown from
observed misses". *CR §8 and Gaps; DJ §2 (2.2), §6; LM §1-2. Evidence: no published catalog exists; P (the repo's incident history).*

| Misconception | Question that exposes it | Pattern that corrects it |
| :--- | :--- | :--- |
| "A node retry is harmless" | "When this node retries, what runs again?" | Failure overlay on a trace; fault lab |
| "Returned updates accumulate" | "After two rounds, what does the next node see?" | Per-step state diff |
| "Scratch state resets itself" | "Same thread, second question, no reset: which path runs?" | Follow-up run on the same thread |
| "Replay rewinds side effects" | "After replaying to step 3, does the file exist?" | Time-travel demo (P4) |
| "`virtual_mode` sandboxes the shell" | "Which control stops `cat ../../.env`?" | Rank and reveal on safeguards |
| "The surfaced error is the last provider's" | "Primary timed out, fallback hit a 429: which error surfaces?" | Fallback lab |

**A2. ADD a pattern row "Grader or agent?":** a failing transcript; the learner says whether the
agent or the grader failed and names the evidence; the outcome state settles it. Fits graders and
eval-lite. *AE §5. Evidence: [Anthropic 2026](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), P.*

**A3. CHANGE the *Variance run* row:** append "after a change, ask whether the spread moved, not
only the mean." *AE §5.*

**A4. ADD three *Sequencing rules*:** "Compare the learner's failure categories with a published
taxonomy (MAST) only after they have built their own." "Every demo shows one failure and its
trace; every project close carries one measured claim (a pass count before and after, over k
runs)." "Teach failure contracts, retry layering, and timeouts from the repo's own conventions;
outside sources barely cover them." *AE §1, §4, §6. Evidence: course designs without outcome data, plus Inference; weak.*

### evidence.md

**E1. CHANGE the table shape:** add a Population column, filled for existing rows from the notes
(PRIMM: 493 pupils aged 11-14; Crouch: physics undergraduates; Bastani: about 1,000 high-school
students; Kestin: 194 Harvard physics students); relabel "MA-level review" as "Review"; add a
header line saying rows from these notes aren't Crossref-checked yet and join MN-012's audit.

**E2. CHANGE three rows.** Teach-back: add Kobayashi 2019 and Roscoe & Chi 2007, strength MA.
"Hints before answers" becomes "Teach from the verified answer; hints only on the target idea",
with Bastani's details (49% error rate; the teacher's solution in the prompt) and Kapoor. "Depth
follows judgment": Kalyuga 2003 is a review, not an MA; add Kalyuga 2007 and the rapid-diagnostic
study, and note a 2025 meta-analysis exists but was not read.

**E3. ADD rows, one line each** (each source link is the one given with its S- or Q-item above):

| Technique | Finding | Design, population | Strength |
| :--- | :--- | :--- | :--- |
| Purpose check | Explaining correlates with writing code, r = 0.555 | Rubric validation, intro and data-structures students | QE, novices |
| Trace table | A 5-10 minute tracing strategy scored about 15% higher | RCT, 24 intro students | RCT, small |
| Design contrast | Comparing solutions improved learning (replication) | QE, 241 second-year CS students | QE |
| Rank and reveal | Matched expert rankings 28% and 21% better | Field evaluations, Marines and soldiers | QE, other domain |
| Surfacing expert rationale | Expert-analysis-based training g = 0.871 | MA, few studies, mostly medical | MA, other domain |
| Refutation | g = 0.41 over 44 comparisons | MA, school and college | MA |
| No self-level feedback | 38% of feedback interventions lowered performance | MA, 607 effect sizes | MA |
| Learning by teaching | Teaching g = 0.56; direct expectancy 0.50 vs 0.27 | MA, 28 studies, students | MA |
| Probing tutee | Tutors default to telling; tutee questions push them to build knowledge | Review, peer tutors | Review |
| PR review | Review yields knowledge transfer more than found defects | Surveys and 570 comments, Microsoft | Q, professionals |
| PR review | Education is a core expectation of review | Interviews and logs, Google | Q, professionals |
| AI help and skill | AI group 50% vs 67%; comprehension-seeking patterns 65% or more | RCT, 52 mostly junior developers | RCT, preprint |
| Tell plumbing | Half bypassed hint guardrails | Deployment, 885 intro students | QE, preprint |
| Fix the answer first | Accuracy moves about 15 points toward the user's stated answer | Benchmark | P, preprint |
| Demo, not typing | Live coding about equal to static code | QE, intro course | QE, novices |
| Spacing kept cheap | Significant in 2 of 9 courses | QE, undergraduate STEM | QE, mixed |

## 3. Three reference files keep SKILL.md short

**`techniques.md` (new, about 170 lines).** Step cards the mentor opens when a probe or a plan
calls for one; SKILL.md names the card, the card holds the steps. Card shape: When; Steps (at most
six); Repo example; Backfires for this learner; Evidence (one line). Cards and their sources:
(1) probe and scaffold, with the per-component menu of the required prediction, why, and what-if
plus at most one card (CR §10; DJ §1.3); (2) runtime model and trace table: one-sentence notional
machine, node-level table, path ladder, per-step diff, one overlay at a time (CR §6); (3)
purpose-labeled chunks fading from given, to marked, to learner-made (CR §5); (4) decision-point
narration in four beats (DJ §1.1); (5) design contrast pair, one variable, a competent alternative
run from the sandbox (CR §7; DJ §3.2); (6) rank and reveal with a minority view when honest (DJ
§2.2; AE §6's design kata is its architecture-scale form); (7) reconstruct the decision and ADR
ablation (DJ §3.1, §3.4); (8) review the verified PR: intent and tests first, three lenses
(correctness under failure, conventions, production path), reconcile with the engineer's
rationale, real findings to the engineer (CR §9; DJ §8.1); (9) refutation and five-part feedback
(DJ §6.1; AT §5); (10) fading ladder L1-L4 per decision type, up after two unaided correct answers,
down after a miss, starting at L2 for types seen before (DJ §1.3); (11) optional opener for a large
unfamiliar file: first glance, five most important lines compared, the "why" of two decisions
(CR §4).

**`materials.md` (new, about 140 lines).** Templates filled while preparing: (1) demo script (LM
§1); (2) lab types table and lab card (LM §2); (3) text diagrams: box, sequence, and state-flow
formats, with six rules (the caption is the question; at most 12 elements; labeled edges;
explanation directly under; built in steps; one anchor diagram reused) (LM §3); (4) resume note,
recall question first (LM §6; AT §8); (5) study-guide template of ten sections with its rules:
question-led headings, a decision table with a named force and a flip trigger, one learner-made
part, links not copies (LM §5); the existing P3 and P4 guides adopt it only when next revised;
(6) review-items format: one table merging LM's gap log and review ledger, kept in STATE.md's
"Review items", with columns concept, where seen, gap type, re-teach in, last asked, result, next
due (LM §4, §7; DJ §5).

**`teach-back.md` (new, about 50 lines).** The project-close defense, loaded only then. Outline:
announce at Session 0; set-up (each design-card decision in 8-12 lines, nothing open, to a named
tutee); probing (three to five ladder questions: why-not, what-if, show-me-the-line); per-decision
scoring on six elements, 0 or 1 each (claim, force, mechanism, rejected alternative with its
winning condition, failure if violated, boundary) plus one project-level changed-force transfer
question; gap routing (missing force or mechanism is a knowledge gap, re-taught with a contrast;
missing alternative or boundary is a judgment gap, given a rank-and-reveal item; a wrong claim is
a misconception, refuted); recording (concept-level review items only); and the six-prompt
design-defense bank (LM §7). Sources: DJ §5, LM §7, current questions.md. DJ's six elements cover
LM's five criteria once the transfer question is added, and they match the pedagogy's unit of
assessment, the design card's key decisions.

**No new skill.** Every technique runs inside a lesson step the `teach` skill already governs,
and reference files give the same load-on-demand. The trigger to revisit: topic preparation
(expected answers, decision tables, demo and lab scripts for a whole stage) grows into its own
multi-step workflow, which would suit a separate prepare skill.

## 4. Conflicts and cautions: where the evidence thins or the rules collide

**Where the notes disagree.**
- *Two teach-back rubrics:* DJ §5 scores six elements 0/1 per decision, LM §7 five criteria 1-3; merged as above.
- *Retrieval load:* LM §4 asks three questions every session start, AT R25 one or two, and AT R9 one per message. Use one or two, one at a time; LM's own classroom evidence is mixed.
- *Struggle or tell:* DJ's predict-then-reveal and reconstruct lean on productive failure, while AT R6 says explain new concepts directly. Both give the same condition: forces first, ask only what is one inference away, tell vocabulary and API names.
- *`file:line` anchors:* AT R22 wants excerpts with `file:line`, but SKILL item 1 keeps them out of lessons, a recorded learner preference. Keep the skill's rule (excerpt or diff plus a clickable file link); R22's form is untested inference.
- *Confidence ratings:* CR §8 asks for confidence 1-3; AT R12 says self-ratings aren't evidence. Drop them; the one-line reason does the diagnostic work.
- *Fading vs priors:* expertise reversal says fade, but CR §10 warns an expert's priors (a sequential call stack, mutation, "a retry is harmless") are where scaffolding must stay. Fade per mechanism.
- *Written teach-back:* a 2016 study (authors unverified; LM §7) found explaining on video helped and writing did not. A chat teach-back is written, so its value rests on the tutee's probing, untested in chat.

**Evidence that is novice-only or weak.** Novices or pupils only: PRIMM (ages 11-14),
explain-in-plain-English, subgoal labels, the tracing strategy (N = 24), Lister's multiple-choice
study, Peer Instruction, Crouch (physics), concreteness fading, classroom spacing. Another domain
and outcome: ShadowBox (military and fire service, measured as agreement with experts) and the
expert-analysis meta-analysis (mostly medical). No outcome data at all: the Block Model, code
reading clubs, katas (11 of 26 respondents), decision-point narration, the 6.5840 lab design, the
study-guide and resume-note formats, and the chat-format rules (R9, R20-R23). Professionals but
perceived outcomes: the code review studies. Every AI-tutor trial used students or junior
developers on introductory material; Shen & Tamkin is nearest (subgroups of 2 to 7), and several
are preprints. The mentor's own choices, to be labeled as such: DJ's 5/6 close threshold, the
L1-L4 promotion rule, the review intervals, and the 15-word limit applied to design-level code.

**Possible conflicts with the charter or pedagogy.**
- *Rubric as a close gate:* DJ §5 step 6 closes a project only at 5/6 or better. That conflicts with the Definition of Done and Principle 10 (closing is the user's), so the rubric feeds review items only.
- *Labs that edit repo files:* LM §2's "move one docs folder" breaks "the repo is always the engineer's verified, clean version" and the charter's no-code rule outside sandbox variations; hence S8's fault sources.
- *PR review replacing the walkthrough:* the pedagogy's delivery invariant has the mentor walk the core. Use PR review as a complement for fluent components, and ask the lead before making it the default.
- *Personal data in repo records:* LM §7's portfolio of quoted answers and scores conflicts with Principle 12 (repo docs may be shared). Keep review items at the concept level.
- *The charter's own lines:* the charter opens a resumed session with a three-line recap, while S10 puts recall first. The charter is the mentor's, so update its "Keeping momentum" line in the same change (Principle 8), and add the teach-back announcement to its Session 0 bookend.
- *Tables in lessons:* trace tables and A/B/C options sit near "no verdict tables" (SKILL item 1). A table that *is* the message's one example is teaching; tables of findings stay out.
- *Turn budget:* every card costs turns, and the charter caps a topic at one sitting and three components, hence at most one extra card per component. The learner's explicit requests to skip a step (R0 Topic 1 skipped tests and demo) override the defaults and are recorded.

## 5. Open questions worth a verified study

1. **Reviewing vs writing:** is there any controlled or quasi-experimental evidence that experienced developers learn as well from reviewing verified code as from writing it? It underpins ADR-0023; extend MN-012.
2. **Chat teach-back:** does an interactive written teach-back keep the learning-by-teaching effect? Read Kobayashi 2024 (interactivity as a moderator) and verify the 2016 video-vs-writing study. Decides `teach-back.md`'s format.
3. **Expertise reversal in professionals:** what are the pooled effects and moderators in the 2025 *Learning and Instruction* meta-analysis, and is there a rapid first-step test for programming? Sets the probe card's thresholds.
4. **Given vs learner-made labels:** which direction did Morrison et al. 2015 find? Decides the second stage of label fading.
5. **A rubric for design rationale:** is there a validated rubric for architecture explanations or design reviews, including health-care teach-back protocols (not yet searched)? Tests the six elements.
6. **Framework misconceptions:** is there a catalog of LangGraph and agent-framework misconceptions from forums, issue trackers, or course Q&A? It would ground distractors beyond the repo's gotchas.
7. **Sycophancy in tutoring:** does verify-then-respond (Daheim 2024) hold for current Claude-class models in multi-turn tutoring, and what are the per-model results in "Check My Work?"? Sizes S2's procedure.
8. **Spacing and contrasts:** what spacing intervals suit a months-long one-on-one adult curriculum, what are Patitsas 2013's effect sizes, and are contrasts better shown together or in sequence? Sets due dates and the architecture step's form.

## Conclusion

The skill's structure is already where the evidence points; what it lacks is precision at the
moment of each move. The one feature every AI tutor that helped had in common was an
expert-verified answer prepared before the conversation. That is S2, and it is also the only
procedural defense against the drift toward the learner's phrasing that the sycophancy work
measures.

The evidence gap sits exactly where this curriculum lives. No study measures what experienced
engineers learn from reviewing verified code, so the mentor's own records are the only data on
whether the method works: the logged predictions, their misses, and the re-check results of
review items. If the review-items table keeps each re-check's result, the curriculum becomes its
own small longitudinal eval, and it applies to teaching the rules it teaches about LLM systems:
look at the data, and measure before tweaking.
