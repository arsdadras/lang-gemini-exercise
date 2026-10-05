# Designing a Mentor's Teaching Materials (demos, labs, diagrams, review, study guides, recaps, assessment)

Scope: practical formats, templates, and steps for an advanced learner who reviews verified code
rather than typing it, runs demos and scenarios, and does a teach-back at each project close.
Evidence is one line per practice. Worked examples use this repo's real components and gotchas
(from `AGENTS.md`): RAG graph (`lab-rag`), sandbox interpreter with HITL (`lab-interpreter`),
model fallback, retries and failure envelopes, checkpointer time travel, P5 eval-lite.

Research budget note: 25 tool calls. Several ACM full texts returned HTTP 403, so some findings
come from abstracts or search snippets; each such case is flagged.

## 1. Live demos and live coding: how to script a demo so it teaches

### Takeaway
The measurable gain comes from making the learner commit to a prediction before the run, not
from watching code being typed: passive watching of a demo teaches about as much as no demo,
and live coding has not been shown to beat static code on exam outcomes. For a learner who does
not type, the right form is a scripted "predict, run, explain the gap, investigate" demo with a
deliberately chosen failing run.

### Cited Findings
- Crouch, Fagen, Callan, Mazur (2004), physics lectures, compared modes of presenting the same demos: students who passively observed understood the concept no better than students who saw no demo; students who predicted the outcome first showed significantly greater understanding; the prediction step costs about two minutes. — [Mazur Group summary](https://mazur.harvard.edu/publications/classroom-demonstrations-learning-tools-or-entertainment); [Am. J. Phys. 72, 835](https://pubs.aip.org/aapt/ajp/article-abstract/72/6/835/1056067/Classroom-demonstrations-Learning-tools-or); [full text PDF](https://www.otffeo.on.ca/wp-content/uploads/sites/2/2014/11/Mazur_demo-article.pdf)
- Rubin (2013, SIGCSE), four CS1 lecture sections, two live-coding vs two static-code: live coding "as good as if not better than" static examples (no large effect claimed). — [Semantic Scholar record](https://www.semanticscholar.org/paper/The-effectiveness-of-live-coding-to-teach-Rubin/8994b3dbf011725aa9a8b8e31a0d2565a9b33920); [search summary via ACM listing](https://dl.acm.org/doi/10.1145/3587102.3588846)
- Raj et al. (2018, Koli Calling), grounded-theory analysis of student feedback on a live-coding intervention: students said it makes the programming process understandable, teaches debugging, and exposes good practices; students preferred coding along to watching. (Self-report, not learning outcomes.) — [ACM](https://dl.acm.org/doi/10.1145/3279720.3279725); [PDF](https://pages.cs.wisc.edu/~gerald/papers/LiveCoding.pdf)
- Selvaraj, Zhang, Porter, Raj (2021, ITiCSE), literature review: live coding is recommended as a best practice but is often run in a way that leaves students passive while the instructor narrates. — [ACM PDF](https://dl.acm.org/doi/pdf/10.1145/3430665.3456382) (abstract-level; full text 403)
- Shah et al. (2023, ICER) and Raj et al. (2020): live coding "not conclusively shown to significantly improve measurable student learning outcomes"; Raj et al. 2020 report it reduces extraneous load by presenting code step by step. — as summarized in [Live Coding in Programming Classes: Instructors' Perspectives (arXiv 2506.03402)](https://arxiv.org/html/2506.03402); original [ICER 2023](https://dl.acm.org/doi/10.1145/3568813.3600122)
- "Active Live Coding" (in-class coding activities plus peer discussion) vs traditional live coding, about 530 CS1 students: no improvement in learning or programming process. — [TOCE 2025](https://dl.acm.org/doi/10.1145/3743686); [NSF PAR](https://par.nsf.gov/biblio/10599712-empirical-evaluation-active-live-coding-cs1)
- Instructor practice (interview study, 2025): advanced-topic instructors prepare full solutions in advance to reduce stress; some separate "explain first, then show" for complex material; deliberate mistakes are used, but one instructor limits them to simple code to avoid confusion; time estimates are unreliable because of questions. — [arXiv 2506.03402](https://arxiv.org/html/2506.03402)
- Nederbragt et al., "Ten quick tips for teaching with participatory live coding" (PLOS Comp Bio, 2020): go slowly and re-read output; mirror the learner's environment; stick to tested lesson material and park off-topic questions; embrace mistakes ("positive error framing"); draw diagrams progressively; have learners predict the next line. — [PLOS Comp Bio](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008090)
- The Carpentries instructor training: instructor mistakes let learners see how errors are diagnosed and fixed ("positive error framing"). — [Live Coding is a Skill](https://carpentries.github.io/instructor-training/17-live)
- PRIMM (Sentance et al., since 2017): Predict, Run, Investigate, Modify, Make; "reading before writing"; Investigate includes tracing, annotating, debugging, explaining. — [PRIMM project](https://computingeducationresearch.org/projects/primm/); [KSU textbook chapter](https://textbooks.cs.ksu.edu/tlcs/4-designing-cs-lessons/07-primm/)

### Inferences

**Rules for a teaching demo (this learner does not type):**
1. One demo, one idea. State the idea only after the run, not before (otherwise the prediction is free).
2. Written prediction first. The learner answers a closed question (A/B/C or "which error text appears") plus one sentence of "why". The mentor records it verbatim; it becomes portfolio evidence and a review-question source.
3. Pick the run where the naive prediction is wrong. A demo that confirms the obvious teaches nothing that reading didn't.
4. Show the failing run before the fix. Failing run -> learner explains the gap between prediction and output -> then the fix or the design that prevents it.
5. Narrate decisions, not keystrokes. For each step say what was chosen and what was rejected ("structured output is bound before `with_fallbacks`, because ...").
6. Script the demo fully (commands, expected output, the planted failure, a fallback if the live model misbehaves). Live runs use `LLM_TEST_MODE=true` per command. Improvise only on questions.
7. Investigate after, with the learner driving the questions: "what would change if ...", "where in the code is that decided". Mapped to PRIMM's Investigate step.
8. Keep a "parking lot" for off-topic questions; answer them at the topic boundary.

**Demo script template:**
```
DEMO <id>: <one-line idea, hidden until step 5>
Setup:       <command(s), env: LLM_TEST_MODE=true, starting state>
Question:    <closed prediction question>  Options: A/B/C
Why-prompt:  "One sentence: why do you expect that?"
Run 1:       <command>  -> expected (failing / surprising) output: <excerpt>
Gap:         "Your prediction was X, output is Y. What explains the difference?"
Decision:    <the design choice this exposes; the alternative that was rejected and why>
Run 2:       <the fixed / contrasting run>  -> expected output: <excerpt>
Investigate: 2-3 what-if questions; one "where in the code" question with a file link
Record:      prediction, explanation quality, open gaps -> gap log
Fallback:    <saved transcript/output if the live model call fails>
```

**Worked example (checkpointer time travel vs sandbox files, P4):**
- Setup: `LLM_TEST_MODE=true uv run lab-interpreter`, ask it to write `result.csv` in the sandbox at step 5, then `replay` to step 3.
- Question: "After replaying to step 3, does `result.csv` exist? A) no, time travel rewound it; B) yes, the file survives; C) the replay fails."
- Run 1: the file is still there (a checkpointer snapshots graph state, not files on disk).
- Gap: the learner explains why state rewound but the disk did not.
- Decision: why the repo keeps side effects outside graph state, and what a production design needs (idempotent side effects, a sandbox diff) to make replay safe.
- Investigate: "What would a replay do to a tool that sends an email?" "Where is the sandbox diff helper, and what does it compare?"

### Gaps
- No study found on demos for a single advanced adult learner (all evidence is classroom, mostly CS1 or physics); transfer to one-on-one senior-level teaching is an inference.
- Could not retrieve the exact Crouch et al. percentages or the Rubin 2013 effect sizes (paywalled); only the directional findings are cited.

## 2. Hands-on labs for a learner who runs and probes a real system

### Takeaway
Strong systems courses give the learner a real system, an automated harness that injects faults
and prints observable pass/fail output, and explicit debugging guidance; CS-ed work on debugging
supports purposely injected, pre-selected faults and scaffolded diagnosis. For a reviewer-learner,
the lab is "predict, run, break, diagnose, explain", with a success condition the learner can see
in output or a trace.

### Cited Findings
- MIT 6.5840 Raft lab: split into parts 3A to 3D with separate deadlines; the tester "can tell labrpc to delay RPCs, re-order them, and discard them"; tests cover leader failure, partitions, crashes; success is a visible line like "Passed -- time 3.5s #peers 3 #RPCs 32"; students are told to run with `-race`, run tests many times, add their own annotations to the visualizer, and that "the most challenging part of this lab may be the debugging"; students follow Figure 2 of the Raft paper. — [6.5840 Lab 3: Raft](https://pdos.csail.mit.edu/6.824/labs/lab-raft1.html)
- 6.5840 test harness checks robustness under dropped or reordered packets, partitions, crashes and restarts, and load. — [student repo summarizing the labs](https://github.com/abdellani/mit-6.5840-labs) (secondary)
- Error-correction exercises: learners read code with purposely injected errors; the teacher selects which errors to inject according to the debugging skill targeted. — [ERIC ED557252](https://files.eric.ed.gov/fulltext/ED557252.pdf) (from search snippet)
- Systematic review of debugging interventions (TOCE 2024): interventions fall into four categories, metacognitive scaffolding, simplification, constraints, and hints. — [ACM TOCE 10.1145/3690652](https://dl.acm.org/doi/10.1145/3690652) (snippet only; full text 403)
- Low-performing students struggle most in the "diagnose the fault" phase; beginners tend to edit-and-test rather than localize the fault. — [Analysis of a Process for Introductory Debugging (ACE 2021)](https://dx.doi.org/10.1145/3441636.3442300); [Empirical Study of Debugging Patterns (SIGCSE 2017)](https://www.cs.kent.edu/~jmaletic/papers/SIGCSE17.pdf) (both from search snippets; attribution of each sentence to each paper not verified)
- An adaptation of Interactive Lecture Demonstrations to debugging ("ILDBug"): predict the bug from program output, trace and fix, then reflect on the debugging process. — seen in results for [Towards more effective testing and debugging education (Illinois IDEALS)](https://www.ideals.illinois.edu/items/136251) (snippet; exact source attribution uncertain)
- PRIMM's Investigate and Modify stages give a ladder from reading to small modifications before making. — [PRIMM](https://computingeducationresearch.org/projects/primm/)
- fast.ai "whole game" (after David Perkins, *Making Learning Whole*): learners run a working end-to-end system first and learn internals later. — [course.fast.ai](https://course.fast.ai/); [Perkins and fast.ai commentary](https://medium.com/@minhaaj/fast-ai-david-perkins-pedagogy-1f0155639e76) (secondary)

### Inferences

**Lab types that fit a reviewer-learner (no typing required, probing encouraged):**
| Type | Learner does | Observable success condition |
| :--- | :--- | :--- |
| Guided exploration | Runs a scenario, answers 3-5 questions whose answers are in output, trace, or state | Answers cite a concrete output line, trace span, or state field |
| Break-it | Applies one prepared fault (config, env var, renamed file, stubbed tool) and predicts the effect | Prediction written first; the actual symptom named; the protecting mechanism located in code |
| Find-the-bug | Gets a branch or patch with one planted defect, a symptom, and a failing test or run | Names the file and line, the root cause, and the test that would have caught it |
| Fault injection | Runs the real system with an injected transient or permanent failure | Trace shows the expected retry/fallback/envelope; learner explains why exactly that layer handled it |
| Eval probe | Runs an eval-lite set, changes one variable (prompt, tier, threshold) | States the metric before and after and whether the difference is noise |

**Rules:**
1. The harness, not the mentor, judges success: a test name, an output line, a trace, a metric. (6.5840 pattern.)
2. One fault per task, pre-selected for the skill targeted (localizing, reading traces, knowing which layer owns a failure).
3. Require a written prediction before each fault run and a one-paragraph diagnosis after, in "symptom -> cause -> mechanism -> fix" order. This targets the diagnose phase where learners struggle.
4. Scaffold diagnosis with hints in tiers (where to look -> what to compare -> the answer), released on request.
5. Run the lab yourself under the real configuration before handing it over, and store the expected output.
6. End each lab with "what would production need here?" (the design card's production path).

**Lab card template:**
```
LAB <id>: <title>                       Time box: <n> min
Goal (skill):      <e.g., locate which layer owns a failure>
System:            <command, env (LLM_TEST_MODE=true), starting state>
Task 1 (explore):  run X; answer: <question with an answer visible in output/trace>
Task 2 (predict):  "If we inject <fault>, what happens?"  -> write prediction
Task 3 (break):    apply <fault>; run; record the symptom
Task 4 (diagnose): symptom -> cause -> mechanism -> fix, with file:line links
Success:           <exact output line / test name / trace shape>
Hints:             H1 where to look | H2 what to compare | H3 answer
Debrief:           production question; gaps -> gap log
```

**Worked examples (agentic AI):**
- Break-it (RAG corpus, P2): move one docs folder the index glob reads, rebuild the index, rerun a question in `lab-rag`. Prediction: "error, or silent?" Success: the learner reports the chunk count before and after and the degraded answer, and explains that a glob matching nothing fails silently; debrief asks for the guard (assert non-empty corpus per source).
- Fault injection (retries, P1/P3): stub the web-search tool to raise a transient error twice, then a permanent one. Success: the trace shows exactly one retry layer (`ToolRetryMiddleware` with `retry_on=is_transient`), and the specialist boundary returns a `failed` envelope with `failure_reason` for the permanent error. Diagnosis question: "Why is the model call itself not wrapped in a retry?"
- Find-the-bug (HITL, P4): a patch renames a consequential tool; approval prompts silently stop appearing. Symptom given: "the agent executed without asking". Success: the learner finds that `HumanInTheLoopMiddleware` matches exact tool names, and names the test that should pin the name.
- Fallback probe: force the primary and the fallback provider to fail; predict which error surfaces. Success: the learner sees the primary's error re-raised and explains why debugging must not trust the surfaced provider name.

### Gaps
- Could not retrieve CMU or Stanford lab handouts or Karpathy's materials within budget; no primary source on their lab design is cited here.
- No study found that measures "break-it" labs for experienced adult engineers specifically; the design rules are extrapolated from 6.5840's harness pattern and novice debugging research.

## 3. Diagrams in text-based teaching

### Takeaway
Keep diagrams small, place the explanation right next to them, strip everything not needed for the
one idea, and build them up in steps; these are Mayer's coherence, signaling, spatial contiguity
and segmenting principles, which have consistent experimental support. In a text channel, that
means an ASCII box diagram, a sequence sketch, or a state-flow table of about 5-12 elements, one
per idea.

### Cited Findings
- Coherence (exclude extraneous material), signaling (cues that highlight organization), spatial contiguity (words next to the picture), and segmenting (break into learner-paced parts) are principles with experimental support. — [Mayer and Fiorella, Cambridge Handbook of Multimedia Learning ch. 12](https://www.cambridge.org/core/books/abs/cambridge-handbook-of-multimedia-learning/principles-for-reducing-extraneous-processing-in-multimedia-learning-coherence-signaling-redundancy-spatial-contiguity-and-temporal-contiguity-principles/CD5B7AE1279A9AB81F8EEBB53DBEC86E); [chapter PDF](https://edtechuvic.ca/wp-content/uploads/sites/11/2022/09/principles-for-reducing-extraneous-processing-in-multimedia-learning-coherence-signaling-redundancy-spatial-contiguity-and-temporal-contiguity-principles.pdf)
- Reported effect sizes differ by source: one summary gives coherence d = 0.70, signaling d = 0.46, spatial contiguity d = 0.79, segmenting d = 0.70; another reports coherence supported in 23 of 23 tests (median d = 0.86) and spatial contiguity in 22 of 22 (median d = 1.10). These come from search snippets and could not be matched to a specific edition; treat as "consistently positive, medium to large", not as exact values. — [Mayer 2017, J. Computer Assisted Learning](https://onlinelibrary.wiley.com/doi/abs/10.1111/jcal.12197); [Cambridge Handbook ch. 12](https://www.cambridge.org/core/books/abs/cambridge-handbook-of-multimedia-learning/principles-for-reducing-extraneous-processing-in-multimedia-learning-coherence-signaling-redundancy-spatial-contiguity-and-temporal-contiguity-principles/CD5B7AE1279A9AB81F8EEBB53DBEC86E)
- Live-coding tip: draw diagrams progressively rather than showing a finished one; grounded in dual coding (Clark and Paivio 1991). — [Nederbragt et al. 2020, tip 6](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008090)
- Concept and knowledge maps: meta-analysis of 55 studies (67 effect sizes, 5,818 participants) found increased retention, with effects small to large depending on use (constructing vs studying) and comparison. — [Nesbit and Adesope 2006, RER](https://journals.sagepub.com/doi/10.3102/00346543076003413); [PDF](https://www.sfu.ca/~jcnesbit/research/NesbitAdesope2006.pdf)

### Inferences

**When a diagram helps (use one):** control flow with branches or loops (graph wiring), who-calls-whom over time (interrupt/resume, delegation), state that changes across steps, layer boundaries (dependency direction). **When it doesn't (skip it):** a linear three-step pipeline, anything a single sentence says, or a full class diagram of the codebase.

**Rules:**
1. One diagram, one question it answers; write that question as the caption.
2. At most about 12 boxes or rows; cut anything not needed for the one idea (coherence).
3. Label edges with the condition or payload (signaling); mark the part under discussion (`<== this lesson`).
4. Put the two-to-four-line explanation directly under the diagram, not in a later paragraph (spatial contiguity).
5. Build in steps: show the skeleton, then the new branch in the next message (segmenting, progressive drawing).
6. Reuse the same diagram across lessons and the study guide so it becomes an anchor; change it by adding, not redrawing.

**Three text formats, one example each:**

Box diagram (RAG graph with a grading loop):
```
question -> [retrieve] -> [grade_docs] --relevant--> [generate] -> answer
                ^              |
                |         not relevant
                +--[rewrite]<--+        (max N rewrites, then answer "not found")
```
Caption: "Where does the loop stop?" Under it: the stop condition lives in the edge function, not in the node.

Sequence sketch (HITL interrupt and resume):
```
user     agent        HITL middleware      tool(execute)
 | ask ->  |                 |                  |
 |         |-- call execute ->| interrupt        |
 |<-- action_request {name,args,description} ---|
 | approve -------------------> resume -------->| runs
 |<------------------ result -------------------|
```

State-flow table (per-question scratch fields):
| Step | `question` | `documents` | `rewrites` | Note |
| :--- | :--- | :--- | :--- | :--- |
| Q1 start | "What is X?" | [] | 0 | caller resets scratch |
| after grade | same | 3 docs | 0 | node returns partial update |
| Q2 start without reset | "What is Y?" | 3 old docs | 0 | bug: stale scratch field |

### Gaps
- No study found on ASCII diagrams specifically versus rendered diagrams; the rules transfer Mayer's principles to text by inference.
- Exact effect sizes for Mayer's principles were not verified against a primary table (see the conflict above).

## 4. Spaced review in a project- or stage-based curriculum

### Takeaway
Use short retrieval questions at every session start (including one from weeks earlier), a
cumulative review at every stage or project close, and re-exposure of earlier concepts inside new
work. Classroom evidence for spacing is positive but less uniform than lab evidence, so keep it
cheap and routine rather than elaborate.

### Cited Findings
- Rosenshine's Principles of Instruction open with daily review of previous learning and include weekly and monthly review. Secondary summaries describe daily review as short (about 5-8 minutes); that figure is from commentary, not verified against the original article. — [FutureLearn summary](https://www.futurelearn.com/info/courses/early-career-teachers/0/steps/164331); [CIRL (Eton College)](https://cirl.etoncollege.com/rosenshine-and-sherrington-on-reviewing/)
- Spaced retrieval in nine introductory STEM courses (bi-weekly quizzes, practice massed on one quiz vs spaced across several; Int. J. STEM Ed., Feb 2024): significant spacing benefits in only two courses, small positive effects in two more; the pooled effect was significant with all courses but not when calculus was excluded; authors call it a low-cost method that helps in at least some courses. — [IJ STEM Education 2024](https://link.springer.com/article/10.1186/s40594-024-00468-5); [ERIC EJ1411400](https://eric.ed.gov/?q=source:%22International+Journal+of+STEM+Education%22&ff1=dtySince_2020&id=EJ1411400)
- Practical spacing recommendations: a brief review of concepts from several weeks earlier in each lesson; homework that re-exposes earlier material; cumulative quizzes and exams. — [Indiana University CITL, Spaced Practice](https://citl.indiana.edu/teaching-resources/evidence-based/spaced-practice.html) (from search snippet); see also [AERO spacing and retrieval practice guide](https://www.edresearch.edu.au/guides-resources/practice-guides/spacing-and-retrieval-practice-guide-full-publication) and [retrievalpractice.org spacing guide](https://pdf.retrievalpractice.org/SpacingGuide.pdf)
- A CS1 course re-framed quizzes as low-stakes retrieval practice activities that students take repeatedly, spaced and interleaved, across the semester. — [ICETC 2023 case study](https://dl.acm.org/doi/10.1145/3629296.3629362)

### Inferences

**Schedule (no flashcard app; the mentor keeps a review ledger):**
| When | What | Size |
| :--- | :--- | :--- |
| Every session start | 3 questions: 1 from last session, 1 from 1-3 weeks ago, 1 from an earlier project | 3-5 min, answered before any new material |
| Topic boundary | 1 "connect" question linking the new topic to an earlier one | 1 question |
| Stage or project close | Cumulative review: 8-10 questions across all projects so far, weighted to the ledger's weak items | 20-30 min, before the teach-back |
| Next project kickoff | "Prerequisite recall": the 3-5 earlier concepts the new project builds on | 5-10 min |

Intervals (next session, about 1 week, about 3 weeks, next project close) are a heuristic, not an evidence-backed optimum for this setting.

**Question rules:** ask for retrieval and explanation, not recognition ("Why does the fallback re-raise the primary's error, and what does that break in debugging?", not "Which error is re-raised?"); mix projects (interleave); keep answers closed-book; the mentor gives the correct answer immediately after.

**Review ledger template:**
```
| Concept | Taught (project/session) | Last asked | Result (ok / partial / miss) | Next due |
| RunnableWithFallbacks re-raises primary's error | P1 s3 | P4 s2 | partial | P4 s4 |
| Checkpointer does not rewind the sandbox | P4 s1 | P4 s3 | ok | P5 close |
```
A "miss" or "partial" moves the next due date closer; two "ok" in a row push it out.

**Worked example (session start, mid P5):**
1. (last session) "What does `/undo` in the memory assistant restore, and what can't it restore?"
2. (2 weeks ago) "In the review pipeline, which node owns the one retry layer for the web search, and why only one?"
3. (earlier project) "Why does per-user data travel in `context=UserContext(...)` rather than `configurable`?"

### Gaps
- No study found on spaced review for one-on-one advanced adult engineering learners; the course-level evidence is from undergraduate STEM and is mixed.
- Did not verify an evidence-based optimal gap length for multi-week projects within budget.

## 5. Study guides and end-of-project write-ups the learner will reuse

### Takeaway
A reusable study guide is a question-led explanation plus reference, not a lesson transcript: it
answers "why is it built this way", records decisions and gotchas in tables, shows one annotated
worked example with labeled subgoals, and ends with retrieval questions. Writing or constructing
the summary is where much of the value lies, so the learner should co-produce part of it.

### Cited Findings
- Diátaxis separates documentation into four types with distinct purposes and styles: tutorials (learning by doing, guided), how-to guides (completing a task), reference (looking up facts), explanation (understanding why); built on two axes, action vs knowledge and study vs work; the types should be kept distinct. — [Diátaxis, start here](https://diataxis.fr/start-here/); [diataxis.fr](https://diataxis.fr/)
- Concept maps: retention gains across 55 studies, larger for some uses than others (constructing vs studying). — [Nesbit and Adesope 2006](https://journals.sagepub.com/doi/10.3102/00346543076003413)
- Subgoal-labeled worked examples improve performance and transfer in programming (app development, text-based and block-based programming); given subgoals suit simple transfer, self-generated subgoal labels suit isomorphic transfer; in a CS1 course, subgoal labeling was associated with lower drop/fail rates. — [Margulieux, Catrambone, Guzdial 2016](https://bpb-us-e1.wpmucdn.com/sites.gatech.edu/dist/b/1555/files/2020/09/MargulieuxCatramboneGuzdial2016.pdf); [Morrison, Margulieux, Guzdial ICER 2015](https://dl.acm.org/doi/10.1145/2787622.2787733); [cs1subgoals.org publications](https://www.cs1subgoals.org/publications/)
- Crib sheets: allowed crib cards did not improve exam performance (Dickson and Miller 2005); a follow-up asked whether students learn while constructing them (Dickson and Bauer 2008); one study attributes a small benefit to preparing the card rather than using it (Erbe 2007, as reported in snippets); over-reliance may encourage shallow learning. — [Dickson and Miller 2005](https://journals.sagepub.com/doi/abs/10.1207/s15328023top3204_6); [Dickson and Bauer 2008](https://doi.org/10.1080/00986280801978343); [crib sheets in a data structures course (Virginia Tech)](https://people.cs.vt.edu/shaffer/Papers/Crib_Sheets2016.pdf)
- "Explain in plain English" research: good explanations describe the code's purpose (relational), not a line-by-line walk (multistructural); relational explainers scored notably higher elsewhere on exams (about 50% higher is reported in a snippet, source attribution not verified). — [EiPE questions, SIGCSE 2012](https://dl.acm.org/doi/10.1145/2157136.2157249); [Ability to EiPE linked to proficiency](https://www.researchgate.net/publication/230718837_Ability_to_'Explain_in_Plain_English'_Linked_to_Proficiency_in_Computer-based_Programming)

### Inferences

**What separates a reusable guide from a transcript:**
| Transcript (avoid) | Study guide (use) |
| :--- | :--- |
| Lesson order, conversational | Organized by the questions a future reader will ask |
| Everything said | Only what is needed to re-derive the design |
| Copies code | Links to code, ADRs, and design cards (one fact, one file) |
| "We did X" | "X exists because Y; it would change if Z" |
| No self-test | Ends with retrieval questions, answers folded below |

In Diátaxis terms, the guide is mostly **explanation** (why) plus a small **reference** (commands, gotchas, file map). It is not a tutorial; the demos and labs were the tutorial.

**Study guide template (one per project, 2-4 pages):**
```
# P<n> study guide: <project>
1. The problem in one paragraph (what breaks without this system)
2. Architecture: one diagram (reused from the lessons) + 3-line caption
3. Five questions this project answers (question-led headings, each 1-2 paragraphs, relational)
4. Decision table: | Decision | Options considered | Chosen | Why (named force) | Would flip if |
5. Worked example: one annotated run with subgoal labels (e.g., "1. build state", "2. route", "3. retry", "4. envelope")
6. Gotchas: | Symptom | Cause | Where handled | Test that pins it |
7. Production path: what changes at real load (links to design card)
8. Commands and file map (reference): run, test, eval; core files as links
9. Retrieval questions (8-10, mixed difficulty), answers folded
10. Learner's gaps at close (from the teach-back) and where they will be revisited
```

**Rules:**
1. Write section 3 as questions the learner actually asked or failed in review, not as topic names.
2. Keep the decision table honest: every "why" names a force (production, sequencing, evidence, scope), matching the repo's admissible-argument rule.
3. The learner produces one part: their own concept map or their own subgoal labels for the worked example, which the mentor corrects. (Constructing is where concept maps and crib-sheet preparation appear to help.)
4. Link, don't copy, anything that already has an owning file (ADRs, design cards, `AGENTS.md` gotchas).
5. Revisit the guide's retrieval questions in the next project's session starters (feeds the review ledger).

**Worked example (fragment for a P2 RAG guide):**
- Question heading: "Why does the graph grade documents before generating, instead of trusting the retriever?"
- Decision row: `| Grade step | none / LLM grader / decision model | LLM grader now | production: bad retrievals are silent without it | when a decision model seam lands (R1) |`
- Gotcha row: `| Answers get worse after a folder move, no error | index glob matched nothing | index build | a test asserting a non-empty corpus per source |`
- Subgoal-labeled run: `1. retrieve (k docs)` -> `2. grade (keep/drop)` -> `3. rewrite if none kept (max N)` -> `4. generate with citations`.

### Gaps
- No controlled study found comparing study-guide formats (question-led vs topic-led) for later reuse; the format rules are inferred from Diátaxis, concept-map, subgoal, and EiPE evidence.
- Karpathy's or fast.ai's end-of-lesson note formats were not reviewed within budget.

## 6. Recaps and resume notes after breaks

### Takeaway
Open every resumed session with retrieval, not a re-lecture: a short "where we are" marker, one
sentence on what the last piece does with a link, the next step, and one question the learner
answers before the mentor restates anything. Evidence supports the review-first habit; no study
was found on the exact note format.

### Cited Findings
- Begin with review of previous learning (Rosenshine principle 1; daily review), distinct from weekly and monthly review. — [FutureLearn summary](https://www.futurelearn.com/info/courses/early-career-teachers/0/steps/164331); [Rosenshine's principles, Structural Learning](https://www.structural-learning.com/post/rosenshines-principles-a-teachers-guide) (secondary)
- Segmenting (learner-paced parts) supports learning of complex material. — [Cambridge Handbook ch. 12 and related Mayer work](https://www.cambridge.org/core/books/abs/cambridge-handbook-of-multimedia-learning/principles-for-reducing-extraneous-processing-in-multimedia-learning-coherence-signaling-redundancy-spatial-contiguity-and-temporal-contiguity-principles/CD5B7AE1279A9AB81F8EEBB53DBEC86E) (segmenting value from search snippet)
- Retrieval-first formats: see the spaced-practice sources in section 4. — [IU CITL](https://citl.indiana.edu/teaching-resources/evidence-based/spaced-practice.html)

### Inferences

**Resume note template (5-8 lines, sent at the start of a resumed session):**
```
Position:   P<n> / topic <k> of <m> / step <hook|concept|architecture|components|tests+demo>
Recall Q:   <one question on the last piece; answer before reading on>
Last piece: <one sentence: what it does and why>  -> <file link>
Connects:   <which earlier piece it plugs into>  (diagram anchor: <name>)
Next:       <the next step in one line>
Open item:  <a parked question or gap, if any>
```
Rules: the recall question comes before the restatement; restate only what the answer shows is
shaky; reuse the project's anchor diagram with a `<== we are here` marker; after breaks longer
than about a week, add one question from the project's start (inference, not evidence-backed).

**Worked example (after a one-week break, mid P5):**
```
Position:   P5 / topic 3 of 5 / components
Recall Q:   "When the assistant writes a memory, whose namespace does it land in, and where does that id come from?"
Last piece: the memory backend factory builds a per-user store namespace from the runtime context  -> utils/ memory backend
Connects:   identity seam from P1 (context=UserContext)
Next:       /forget: what deletion must cover (store + checkpoints) and how we test it
Open item:  your question on TTL for memories (parked, answered at topic close)
```

### Gaps
- No research found on resume-note formats for learning after breaks; the template is an inference from review-first principles and engineering handoff practice (the repo's own `STATE.md` pattern).

## 7. Assessment artifacts: teach-back, design defense, portfolio, gap log

### Takeaway
Explaining to someone (even an imagined audience, even recorded) produces durable learning, and
the quality of an explanation can be graded by whether it states purpose and reasons (relational)
rather than walking through lines. Use a short teach-back rubric, a fixed set of design-defense
prompts, a portfolio of dated evidence, and a gap log that feeds the next project's session
starters and labs.

### Cited Findings
- Fiorella and Mayer (2013): students who expected to teach did better only on an immediate test; students who actually taught (a short video lecture) did better on immediate and delayed comprehension tests. — [Fiorella and Mayer 2013, Contemporary Educational Psychology](https://www.researchgate.net/publication/247768656_The_relative_benefits_of_learning_by_teaching_and_teaching_expectancy); [Fiorella, "Learning by Teaching" chapter](https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-learning-by-teaching-fiorella.pdf)
- Explaining to fictitious others on video improved learning, while writing an explanation for them did not (per the article title). — [Gaining from explaining, Contemporary Educational Psychology 2016](https://www.sciencedirect.com/science/article/abs/pii/S0361476X16000102)
- EiPE: grade explanations as relational (purpose) vs multistructural (line-by-line); relational ability is linked to programming proficiency. — [EiPE questions, SIGCSE 2012](https://dl.acm.org/doi/10.1145/2157136.2157249); [EiPE linked to proficiency](https://www.researchgate.net/publication/230718837_Ability_to_'Explain_in_Plain_English'_Linked_to_Proficiency_in_Computer-based_Programming)
- Recorded predictions from demos are a cheap, honest measure of misconceptions (prediction is the active ingredient in Crouch et al.). — [Crouch et al. 2004](https://mazur.harvard.edu/publications/classroom-demonstrations-learning-tools-or-entertainment)

### Inferences

**Teach-back rubric (per project close; learner explains aloud, mentor scores and quotes):**
| Criterion | 1 (gap) | 2 (partial) | 3 (solid) |
| :--- | :--- | :--- | :--- |
| Purpose | Describes code line by line | States what it does | States what problem it solves and what breaks without it (relational) |
| Mechanism | Names parts | Traces one run correctly | Traces a run and a failure run, naming which layer handles what |
| Decisions | "That's how it is" | Names the choice | Names the choice, the rejected alternative, and the force behind it |
| Failure and scale | Not addressed | Names one failure mode | Names failure modes, how each is contained, and the production path |
| Transfer | None | Answers one what-if | Applies the design to a new case unprompted |

**Design-defense prompts (pick 4-5 per project, same shape every time):**
1. "Why is this a graph (or an agent, or a node) and not the other?"
2. "What happens when <dependency> is down for 5 minutes? Walk the retry, fallback, and envelope."
3. "Where does per-user identity enter, and what leaks if it's read from the wrong place?"
4. "What would you remove if you had to cut 30% of the code, and what would you lose?"
5. "Show me the test that proves <property>. What doesn't it prove?"
6. "At production load, what changes first?"
Worked example (P4 interpreter): "The sandbox shell gets `build_sandbox_env()` only. What would a generated script see without it, and which test pins it?"

**Portfolio evidence (dated, linked, no copies of code):** demo predictions with outcomes;
lab diagnoses (symptom -> cause -> mechanism -> fix); teach-back scores with quoted answers;
design-defense answers; the learner-produced part of each study guide.

**Gap log (feeds the next project):**
```
| Gap | Evidence (where seen) | Severity | Re-teach in | Re-check (ledger) | Status |
| Confuses graph state with on-disk side effects | P4 demo 2 prediction | high | P5 topic 2 (memory writes) | P5 s3 start | open |
| Can't say which layer retries a tool error | P3 lab 2 diagnosis | medium | P5 lab (memory backend fault) | P5 close | open |
```
Rules: every "1" or "2" on the rubric becomes a gap row; each gap is scheduled into a named later
topic or lab plus a ledger question; the next project's kickoff reviews open gaps first.

### Gaps
- No empirical study found on design-defense rubrics or engineering portfolios for advanced learners; the rubric and prompts are inferences built on EiPE (relational vs multistructural) and learning-by-teaching evidence.
- The exact attribution of "Gaining from explaining" (authors) was not verified; only its title and journal are cited.
