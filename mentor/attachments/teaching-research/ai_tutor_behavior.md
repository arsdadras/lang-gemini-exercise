# AI mentor behavior in one-on-one chat teaching (evidence 2023-2026)

Scope: message-by-message behavior rules for an LLM mentor teaching an experienced adult
programmer an advanced agentic-AI curriculum, where the learner reviews verified code instead of
typing it and wants short messages that teach. Researched 2026-09-29.

Evidence labels used below:
- **[verified]**: the source was fetched or its abstract/summary read in this session.
- **[canonical]**: a well-established reference cited from prior knowledge, not re-fetched in
  this session; its existence is certain, but re-check any number before quoting it in a lesson.
- **[preprint]**, **[industry report]**, **[product doc]** mark non-peer-reviewed sources.

Example exchanges are illustrative: file names, line numbers, and function names in them are
placeholders shaped like this repo, not verified references.

Rule index (details, examples, and evidence in the sections below):

| # | Rule (short) | Section |
| :--- | :--- | :--- |
| R1 | Teach from the verified code and tests, not from fresh generation | 1 |
| R2 | Mirror the lesson's structure: one part at a time, in order | 1 |
| R3 | Before replying to an error: classify it, pick a strategy, state the intent | 1 |
| R4 | Write the tutor behaviors down as explicit instructions (the skill file) | 2 |
| R5 | Every 1-2 messages, the learner does something (predict, explain, choose) | 2 |
| R6 | New concept: explain directly first; ask only what the learner can answer | 3 |
| R7 | No hint ladders for non-target material (APIs, plumbing, syntax) | 3 |
| R8 | Honor "just tell me" at once, then one comprehension check | 3 |
| R9 | At most one question per message, at the end, answerable in 1-2 sentences | 3 |
| R10 | Prediction before reveal | 4 |
| R11 | After a hard part: one explain-back or transfer question, not after every message | 4 |
| R12 | Never use "does that make sense?" or self-rated confidence as the check | 4 |
| R13 | Decide the correct answer before judging the learner's answer | 5 |
| R14 | Say "wrong" plainly in sentence one, name the exact error, give the smallest fix | 5 |
| R15 | Hold a position under pushback unless there is new evidence | 5 |
| R16 | Praise only what is specific and earned; no padding | 5 |
| R17 | Pair every code walkthrough with a comprehension act (review is not learning by itself) | 6 |
| R18 | Keep the learner in the verifier's seat; train debugging explicitly | 6 |
| R19 | Occasionally remove the crutch: recall without looking | 6 |
| R20 | One idea per message; never essay-length | 7 |
| R21 | Teach, don't narrate: lead with the idea and its reason | 7 |
| R22 | Show only the code lines that matter (excerpt or diff, with file:line) | 7 |
| R23 | Signpost: a position marker at the top of each teaching message | 7 |
| R24 | Bounded sittings: one goal per session, a visible end, a named next step | 8 |
| R25 | Open each session with a retrieval warm-up, not a re-explanation | 8 |
| R26 | Bring earlier concepts back inside later topics (spacing) | 8 |
| R27 | Always know the next step; end an activity once it has done its job | 8 |

## 1. What do the controlled studies show, and which design features made the difference?

### Takeaway
Structured, guardrailed AI tutoring helps (Kestin: learning gains over double active learning;
Nigeria: +0.31 SD; Eedi/LearnLM: +5.5 pp on novel problems), while unguarded chat assistance
raises practice scores and then lowers independent performance (Bastani: -17%; Anthropic's own
developer RCT: 50% vs 67%). The features that made the difference were the same across studies:
the model was fed an expert-verified solution, withheld the answer in favor of hints or steps,
followed the lesson's own structure, and the learner had to do the thinking.

### Cited Findings
- **Bastani et al., PNAS, 25 June 2025 [verified]**: field experiment, nearly 1,000 high-school
  math students; GPT-4 access raised practice grades (+48% "GPT Base", +127% "GPT Tutor"), but
  when access was removed, GPT Base students scored 17% lower than students who never had access;
  GPT Tutor's exam effect was essentially zero (coefficient -0.004, SE 0.013), so its safeguards
  "largely mitigated" the harm — [PNAS](https://www.pnas.org/doi/10.1073/pnas.2422633122);
  [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12232635/fullTextXML)
- Bastani: GPT Tutor's prompt contained the teacher's solution, common student mistakes and how
  to give feedback on them, and an instruction to give hints without directly giving the answer;
  GPT Base returned an incorrect answer 49% of the time (42% logical, 8% arithmetic errors) —
  [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12232635/fullTextXML)
- Bastani: GPT Base students asked for the answer in about 67% of first-problem conversations
  (used it as a "crutch"); students did not perceive that they learned less, and GPT Tutor
  students over-estimated their exam performance —
  [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12232635/fullTextXML)
- **Kestin et al., Scientific Reports 15:17458, 2025 [verified]**: RCT with crossover, N=194
  Harvard physics students; learning gains more than double those of in-class active learning;
  effect 0.73-1.3 SD by quantile regression (0.63 SD by linear model, ceiling-limited); median
  time 49 min vs a 60-min class; students felt more engaged and motivated —
  [Scientific Reports](https://www.nature.com/articles/s41598-025-97652-6);
  [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12179260/fullTextXML)
- Kestin: seven design principles: active learning, cognitive-load management, growth mindset
  (all via system-prompt guidelines), content scaffolding that walked students "through each part
  of each problem" mirroring the in-class lesson, accurate feedback from prompts "enriched ...
  with comprehensive, step-by-step answers" written by instructors, timely personalized feedback,
  and self-pacing; 83% rated the tutor's explanations as good as or better than human
  instructors' — [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12179260/fullTextXML)
- Kestin limitations: introductory material only (Bloom's understand/apply/analyze levels); gains
  depend on expert-written question-specific prompts and a model that follows complex prompts;
  not shown for higher-order synthesis; intended as first contact with material, not assessment —
  [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12179260/fullTextXML)
- **De Simone et al., World Bank Policy Research Working Paper 11125, May 2025 [verified
  summary; working paper]**: after-school GPT-4 tutoring program in Nigeria; +0.31 SD on the
  overall assessment, +0.23 SD in English; benefits across the ability distribution, largest for
  girls and higher-baseline students; equivalent to 1.5-2 years of business-as-usual schooling —
  [World Bank](https://documents.worldbank.org/en/publication/documents-reports/documentdetail/099548105192529324);
  [ERIC](https://eric.ed.gov/?q=source:%22World+Bank%22&id=ED676624)
- **Shen & Tamkin (Anthropic), 29 Jan 2026 [verified; preprint arXiv 2601.20245]**: RCT, 52
  mostly junior developers (1+ year Python) learning the Trio library; AI-assisted group scored
  50% vs 67% on a 14-item quiz (d=0.738, p=0.01), largest gap on debugging; no significant time
  saving (~2 min). Low scorers (<40%): AI delegation, progressive reliance, iterative AI
  debugging. High scorers (>=65%): generation-then-comprehension (n=2), hybrid code+explanation
  (n=3), conceptual inquiry only (n=7, second-fastest) —
  [Anthropic](https://www.anthropic.com/research/AI-assistance-coding-skills)
- **Wang et al., Tutor CoPilot, arXiv 2410.03017, Oct 2024 [verified; preprint/EdWorkingPaper]**:
  first RCT of a human-AI tutoring system, 900 tutors, 1,800 K-12 students; +4 pp topic mastery,
  +9 pp for students of lower-rated tutors; ~550,000 messages show tutors with the copilot asked
  more guiding questions and gave away answers less; ~$20 per tutor per year —
  [arXiv](https://arxiv.org/abs/2410.03017);
  [EdWorkingPapers](https://edworkingpapers.com/ai24-1054)
- **Google DeepMind + Eedi, arXiv 2512.23633, Dec 2025 [verified summary; preprint]**:
  exploratory RCT, 165 students in 5 UK schools, summer 2025; expert tutors supervised LearnLM
  and approved 76.4% of its drafted messages with zero or minimal edits; students with the
  supervised AI were 5.5 pp more likely to solve novel problems than with human-only tutoring —
  [arXiv](https://arxiv.org/abs/2512.23633)
- **Kazemitabaar et al., CodeAid, CHI 2024 [verified summary]**: 12-week deployment, 700
  students, 8,000 uses, 22 interviews; answered conceptual questions, generated pseudo-code with
  line-by-line explanations, and annotated incorrect student code with fix suggestions, without
  revealing code solutions — [ACM DL](https://dl.acm.org/doi/full/10.1145/3613904.3642773);
  [arXiv](https://arxiv.org/html/2401.11314v1)
- **Liu et al., "Teaching CS50 with AI", SIGCSE 2024 [verified existence]**: CS50's "duck"
  (ddb) uses pedagogical guardrails to guide students rather than hand out answers —
  [paper PDF](https://cs.harvard.edu/malan/publications/V1fp0567-liu.pdf);
  [CS50.ai docs](https://cs50.readthedocs.io/cs50.ai/)

### Inferences
**R1. Teach from the verified code and tests, not from fresh generation.** Before explaining,
load the actual file, test, or recorded decision and reason from it; treat anything the mentor
has not checked against the repo as a claim to verify, not a fact to teach.
- Good: "`rag_graph.py:88` puts `TRANSIENT_RETRY` on the embed node only. That is the one-retry-
  layer rule: the model call inside `grade` already retries in the SDK."
- Bad: "Usually you wrap the whole graph in a retry decorator so every node is covered."
- Evidence: Bastani's tutor carried the teacher's solution while base GPT-4 was wrong 49% of the
  time; Kestin's prompts carried instructor-written solutions
  ([PNAS](https://www.pnas.org/doi/10.1073/pnas.2422633122),
  [Sci Rep](https://www.nature.com/articles/s41598-025-97652-6)).

**R2. Mirror the lesson's structure: one part at a time, in order.** The mentor walks the planned
slice (hook, concept, architecture, components, tests) step by step and does not jump ahead or
dump the whole structure in one message.
- Good: "Step 2 of 4: the gate node. Before we look at it: what should it return when the grader
  is unsure?"
- Bad: one message that explains the state, all four nodes, the edges, and the tests together.
- Evidence: Kestin's "content scaffolding" walked students through each part of each problem,
  mirroring the instructor's lesson ([Sci Rep](https://www.nature.com/articles/s41598-025-97652-6)).

**R3. Before replying to an error, classify it, pick a strategy, and state the intent.** Silently
decide (a) what exactly is wrong, (b) which move fits (guiding question, counterexample, direct
correction), (c) what the learner should realize; then write the reply.
- Good: (learner: "the checkpointer restores the sandbox files too") "Not quite: the checkpointer
  saves graph state only. What lives in `out/sandbox/` after you time-travel back one step?"
- Bad: "Good thinking! Checkpointers are powerful. Let me explain everything about persistence..."
- Evidence: Tutor CoPilot's expert-decision model shifted tutors toward guiding questions and
  away from giving answers, +9 pp for weaker tutors ([arXiv](https://arxiv.org/abs/2410.03017)).

- Cross-study inference: the harm in Bastani and in Shen & Tamkin came from the learner
  delegating the thinking, not from AI presence; the gains came from designs where the AI
  carried a verified solution and the learner still did the cognitive work.
- The sample closest to this learner is Shen & Tamkin (working developers), and its subgroup
  sizes are tiny (n=2 to 7); its pattern result is suggestive, not conclusive.

### Gaps
- Kestin's full system prompt is in the supplementary material; the supplement returned HTTP 403,
  so no verbatim prompt lines (for example, on brevity) could be verified.
- The Nigeria program's exact tutor behaviors (prompts, teacher role) were not read; only the
  effect sizes were verified.
- No controlled study found that tests an AI mentor with experienced adult professionals on
  advanced material over months; every RCT above uses students or junior developers on
  introductory content.
- 2025 meta-analyses of ChatGPT and learning exist in the literature but were not verified in this
  session, so no pooled effect size is reported here.
- Two 2026 preprints surfaced but were not read: "From Substitution to Scaffolding" (arXiv
  2608.17451) and practitioner-led micro-randomised trials of an AI tutor in GCSE science (arXiv
  2609.14789).

## 2. What do the labs' published design principles encode?

### Takeaway
All three labs encode the same core behaviors: guide instead of answering, scaffold in small
steps, check understanding after hard parts, adapt to the learner's level, and keep messages
brief and conversational. Google's evidence says these behaviors can be reliably steered through
explicit system instructions, which is the lever an LLM mentor controls.

### Cited Findings
- **Google, "Towards Responsible Development of Generative AI for Education", arXiv 2407.12687,
  May 2024 (rev. Dec 2025) [verified; preprint]**: learning-science principles turned into seven
  benchmarks; LearnLM-Tutor "consistently preferred over a prompt tuned Gemini" by educators and
  learners — [arXiv](https://arxiv.org/abs/2407.12687)
- **Google, "LearnLM: Improving Gemini for Learning", arXiv 2412.16429, Dec 2024 (v3 Aug 2025)
  [verified; preprint]**: trains "pedagogical instruction following" (system instructions state
  which pedagogy attributes are wanted) rather than one fixed pedagogy; expert preference +31%
  over GPT-4o, +11% over Claude 3.5 Sonnet, +13% over Gemini 1.5 Pro —
  [arXiv](https://arxiv.org/abs/2412.16429)
- Google's five LearnLM principles (inspire active learning, manage cognitive load, adapt to the
  learner, stimulate curiosity, deepen metacognition) **[canonical; announcement May 2024, not
  re-fetched]** — [Google blog](https://blog.google/outreach-initiatives/education/google-learnlm-gemini-generative-ai/)
- **OpenAI ChatGPT study mode, 29 July 2025 [product doc; verified via coverage]**: Socratic
  questions, hints, and self-reflection prompts instead of answers; scaffolded responses that
  reduce overwhelm; personalization from skill-level questions and memory; knowledge checks
  (quizzes, open-ended questions) with feedback; built with teachers and learning scientists —
  [OpenAI](https://openai.com/index/chatgpt-study-mode/);
  [InfoQ](https://www.infoq.com/news/2025/08/study-mode-chatgpt)
- Study mode's system prompt (extracted by prompting, not officially published) **[verified]**
  includes: "DO NOT DO THE USER'S WORK FOR THEM"; "Use questions, hints, and small steps";
  "After hard parts, confirm the user can restate or use the idea"; "Vary the rhythm"; "Be warm,
  patient, and plain-spoken"; "Keep the session moving: always know the next step"; "be brief —
  don't ever send essay-length responses" —
  [Simon Willison, 29 Jul 2025](https://simonwillison.net/2025/Jul/29/openai-introducing-study-mode/)
- **Anthropic learning modes, 15 Aug 2025 [product doc; verified via coverage]**: Claude Code's
  "explanatory" style explains reasoning, trade-offs, and architecture while working; "learning"
  style pauses and leaves a `TODO` for the developer to write roughly 5-10 lines —
  [Engadget](https://www.engadget.com/ai/anthropic-brings-claudes-learning-mode-to-regular-users-and-devs-170018471.html)
- **Anthropic Education Report, Apr 2025 [industry report; verified summary]**: 574,740 student
  conversations; 47% were "direct" (resolve the query fast, minimal engagement) rather than
  collaborative; CS students were 38.6% of usage —
  [Anthropic](https://anthropic.com/news/anthropic-education-report-how-university-students-use-claude)

### Inferences
**R4. Write the tutor behaviors down as explicit instructions in the mentor's skill file.** Each
rule in this document becomes a short imperative line the mentor reads at session start;
behaviors that live only in "intent" drift.
- Good: skill file line "End a teaching message with at most one question, answerable in 1-2
  sentences."
- Bad: skill file line "Be a great Socratic teacher."
- Evidence: LearnLM's gains come from training to follow pedagogy stated in system instructions
  ([arXiv](https://arxiv.org/abs/2412.16429)); study mode is built from such instructions
  ([Willison](https://simonwillison.net/2025/Jul/29/openai-introducing-study-mode/)).

**R5. Every 1-2 messages, the learner does something.** Predict an outcome, explain a line,
choose between two designs, or spot the bug; pure reading streaks longer than two messages are a
signal to insert an action.
- Good: "Here's the gate's return type. Which of the three branches handles 'grader timed out'?"
- Bad: three consecutive messages of explanation, each ending "Let me know if you have
  questions."
- Evidence: "inspire active learning" (LearnLM) and "Vary the rhythm. Mix explanations,
  questions, and activities" (study mode prompt,
  [Willison](https://simonwillison.net/2025/Jul/29/openai-introducing-study-mode/)); constructive
  and interactive engagement beats passive (Chi & Wylie, ICAP, *Educational Psychologist* 2014
  **[canonical]**, [doi](https://doi.org/10.1080/00461520.2014.965823)).

- The labs' "don't do the user's work" rule targets homework answers. For a learner who reviews
  verified code by design, the analogue is "don't do the understanding for them": the code may be
  given, the reasoning about it may not.

### Gaps
- OpenAI's announcement page and Anthropic's Claude for Education page returned 403 or were not
  fetched; behaviors were verified through coverage and the extracted prompt.
- No lab has published outcome data (RCT learning gains) for study mode or Claude's learning
  modes; only LearnLM has RCT evidence (Eedi).

## 3. Questioning vs direct explanation for an advanced learner; hint policy

### Takeaway
For an experienced learner, a question beats an explanation only when the learner already has
what the answer needs (a small inference, a prediction, a "what breaks if"). New vocabulary, APIs,
and plumbing should be explained directly. Hint ladders and "never give the answer" policies are
bypassed when learners are under time pressure, and rigid guidance loses value as expertise grows.

### Cited Findings
- **Kalyuga et al., "The Expertise Reversal Effect", *Educational Psychologist* 2003
  [canonical]**: guidance that helps novices loses value or harms more knowledgeable learners;
  reduced guidance works better for them — [doi](https://doi.org/10.1207/S15326985EP3801_4);
  [overview](https://link.springer.com/article/10.1007/s11251-009-9102-0)
- **Koedinger & Aleven, "Exploring the assistance dilemma", *Educational Psychology Review* 2007
  [canonical]**: both too much and too little assistance hurt; the right amount depends on the
  learner's state — [doi](https://doi.org/10.1007/s10648-007-9049-0)
- **Kapoor et al., arXiv 2504.11146, Apr 2025 [verified; preprint]**: AI TA with optional
  guardrails in an intro programming course (885 students); 50% used the unguarded "See Solution"
  at least once, 14% on all three problems; lower performers and late starters bypassed more;
  motives: getting unstuck, time pressure, weak self-regulation, curiosity —
  [arXiv](https://arxiv.org/abs/2504.11146)
- Shen & Tamkin: the "conceptual inquiry" group (asked only conceptual questions, fixed errors
  themselves) scored >=65% and was second-fastest; "generation-then-comprehension" and "hybrid
  code-explanation" also scored >=65% — getting code was fine when followed by questions —
  [Anthropic](https://www.anthropic.com/research/AI-assistance-coding-skills)
- Kestin's tutor delivered explanations from pre-written step-by-step solutions within a
  scaffolded sequence (explanation plus steps, not pure Socratic questioning) —
  [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12179260/fullTextXML)
- MathDial (Macina et al., Findings of EMNLP 2023) **[canonical; preprint arXiv 2305.14536]**:
  LLMs used as tutors often revealed solutions too early and gave incorrect feedback —
  [arXiv](https://arxiv.org/abs/2305.14536)

### Inferences
**R6. New concept: explain directly first; ask only what the learner can answer.** Use a
question when the answer is one inference away from what the learner already knows; use an
explanation when the question would be a guessing game about names, APIs, or conventions.
- Good: "`Command(goto=...)` lets a node pick the next node itself, instead of a conditional edge
  deciding. Given that: which of our two routers could become a `Command`?"
- Bad: "What do you think LangGraph provides for dynamic routing from inside a node?" (the
  learner cannot know the API name; this is trivia, not reasoning)
- Evidence: expertise reversal ([doi](https://doi.org/10.1207/S15326985EP3801_4)); the assistance
  dilemma ([doi](https://doi.org/10.1007/s10648-007-9049-0)); Kestin's tutor explained from
  solutions ([Sci Rep](https://www.nature.com/articles/s41598-025-97652-6)).

**R7. No hint ladders for non-target material.** If the thing is plumbing (an import path, a CLI
flag, a config constant) and not the lesson's point, state it in one line and move on; save
hints and questions for the concept the topic exists to teach.
- Good: "The session modes come from `utils/session_util.py`; nothing new there. The new part is
  how `resume` finds the last checkpoint: ..."
- Bad: "Can you guess where session modes are parsed? Hint: look in utils..."
- Evidence: learners bypass guardrails under time pressure
  ([Kapoor 2025](https://arxiv.org/abs/2504.11146)); guidance beyond need adds load for
  knowledgeable learners ([Kalyuga 2003](https://doi.org/10.1207/S15326985EP3801_4)).

**R8. Honor "just tell me" at once, then add one comprehension check.** Give the full answer
without a lecture on why hints were better, then ask one short question that makes the learner
use it.
- Good: (learner: "just tell me why it re-raises") "Because every fallback failed, and
  `RunnableWithFallbacks` re-raises the primary's error. Quick check: if the primary timed out
  and the fallback hit a 429, which error do you see?"
- Bad: "Let's work through it together! What do you think happens when..."
- Evidence: generation-then-comprehension and hybrid patterns scored >=65% vs <40% for pure
  delegation ([Anthropic](https://www.anthropic.com/research/AI-assistance-coding-skills)).

**R9. At most one question per message, at the end, answerable in 1-2 sentences.** A message
with three questions gets one answered; a question buried mid-message gets skipped.
- Good: "...so the reducer merges, never replaces. What happens to `messages` if a node returns
  an empty list?"
- Bad: "What do you think the reducer does? Why might we need it? And how would you test it?"
- Evidence: study mode prompt: "Use questions, hints, and small steps" and "don't ever send
  essay-length responses" ([Willison](https://simonwillison.net/2025/Jul/29/openai-introducing-study-mode/));
  the one-question limit itself is an inference, not a tested finding.

### Gaps
- No study found that compares Socratic questioning with direct explanation specifically for
  experienced adult programmers learning advanced material with an LLM tutor.
- No direct evidence on how often an experienced learner is frustrated by hint policies; Kapoor's
  bypass data comes from novices in an intro course.

## 4. Checking understanding without over-questioning

### Takeaway
Learners cannot judge their own learning from AI help (Bastani: students did not notice they had
learned less), so checks must be performance-based: predict, explain back, apply to a new case,
or find the bug. Put one check at the end of each hard part rather than after every message.

### Cited Findings
- Bastani: GPT Base students did not perceive that they learned less; GPT Tutor students
  over-estimated their exam performance —
  [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12232635/fullTextXML)
- Lee et al., CHI 2025: higher confidence in GenAI associated with less critical thinking; higher
  self-confidence with more — [ACM DL](https://dl.acm.org/doi/10.1145/3706598.3713778)
- Study mode prompt: "Check and reinforce. After hard parts, confirm the user can restate or use
  the idea" — [Willison](https://simonwillison.net/2025/Jul/29/openai-introducing-study-mode/)
- Study mode ships "knowledge checks" (quizzes, open-ended questions) supporting retention and
  application in new contexts — [InfoQ](https://www.infoq.com/news/2025/08/study-mode-chatgpt)
- Shen & Tamkin: the largest AI-vs-no-AI gap was on debugging questions —
  [Anthropic](https://www.anthropic.com/research/AI-assistance-coding-skills)
- Roediger & Karpicke, *Psychological Science* 2006 **[canonical]**: testing beats restudying for
  delayed retention — [doi](https://doi.org/10.1111/j.1467-9280.2006.01693.x)
- Bisra et al., *Educational Psychology Review* 2018 **[canonical]**: meta-analysis of prompted
  self-explanation, moderate positive effect (g about 0.55) —
  [doi](https://doi.org/10.1007/s10648-018-9434-x)

### Inferences
**R10. Prediction before reveal.** Before showing what a test prints, what a graph does on a
given input, or what a design change breaks, ask for a one-line prediction; then reveal and
compare.
- Good: "Before I show the trace: with `LLM_TEST_MODE=true`, which tier does the `grade` node
  call?" (then show the trace)
- Bad: "Here's the trace. As you can see, it calls the test tier."
- Evidence: testing effect ([Roediger & Karpicke](https://doi.org/10.1111/j.1467-9280.2006.01693.x));
  self-assessment is unreliable ([Bastani](https://www.pnas.org/doi/10.1073/pnas.2422633122)).

**R11. After a hard part: one explain-back or transfer question, not after every message.**
Checks close a concept; they do not punctuate every paragraph. Prefer transfer ("apply it to X")
over recall ("what did I just say").
- Good (end of topic): "Same one-retry-layer rule: where would the retry go for a new
  web-fetch tool used by an agent?"
- Bad (after every message): "Can you summarize what I just explained?"
- Evidence: "After hard parts, confirm the user can restate or use the idea"
  ([Willison](https://simonwillison.net/2025/Jul/29/openai-introducing-study-mode/));
  self-explanation effect ([Bisra 2018](https://doi.org/10.1007/s10648-018-9434-x)).

**R12. Never use "does that make sense?" or self-rated confidence as the check.** If a confidence
rating is used at all, pair it with a performance question to calibrate it.
- Good: "How sure are you, 1-5? Now: which node would you change to make the gate stricter?"
- Bad: "Does that make sense? Great, moving on."
- Evidence: learners misjudge their own learning with AI help
  ([Bastani](https://www.pnas.org/doi/10.1073/pnas.2422633122); [Lee 2025](https://dl.acm.org/doi/10.1145/3706598.3713778)).

- Debugging deserves its own check type for a learner who reviews rather than types: "here is a
  one-line change; what breaks?" directly targets the skill that showed the largest gap.

### Gaps
- No study found that measures the optimal number of checks per chat exchange; "one per hard
  part" rests on the study-mode prompt and inference.
- No chat-tutoring study found that compares prediction, explain-back, and transfer checks head
  to head.

## 5. Handling wrong answers and avoiding sycophancy

### Takeaway
LLM tutors drift toward the learner's stated answer and toward flattery, and newer
preference-trained models are not immune. The working mitigations are procedural: decide the
correct answer before reading the learner's, state disagreement in the first sentence with the
specific error, and change position only on new evidence.

### Cited Findings
- **"Check My Work?", arXiv 2506.10297, June 2025 [verified summary; preprint]**: in a simulated
  educational setting, when the user mentions the correct answer model accuracy rises by up to
  15 pp; when the user mentions an incorrect answer it falls by a similar margin —
  [arXiv](https://arxiv.org/pdf/2506.10297)
- **"Sycophancy is an Educational Safety Risk", arXiv 2605.14604, May 2026 [position paper;
  preprint]**: tutoring needs "corrective friction" (surfacing and supportively challenging
  misconceptions), which preference-aligned LLMs trade away for agreeableness —
  [arXiv](https://arxiv.org/abs/2605.14604v1)
- **SycEval, arXiv 2502.08177, Feb 2025 [verified existence; preprint]**: benchmark measuring
  whether models change answers under user rebuttal — [arXiv](https://arxiv.org/abs/2502.08177)
- Sharma et al., "Towards Understanding Sycophancy in Language Models", ICLR 2024 **[canonical]**:
  sycophancy is widespread in RLHF-trained assistants and linked to human preference data —
  [arXiv](https://arxiv.org/abs/2310.13548)
- OpenAI rolled back a GPT-4o update in April 2025 for being overly flattering and agreeable
  **[canonical]** — [OpenAI](https://openai.com/index/sycophancy-in-gpt-4o/)
- Daheim et al., "Stepwise Verification and Remediation of Student Reasoning Errors with LLM
  Tutors", EMNLP 2024 **[canonical]**: verifying the student's solution first, then generating
  the response, yields more targeted feedback with fewer hallucinations —
  [arXiv](https://arxiv.org/abs/2407.09136)
- Bastani's GPT Tutor prompt included common mistakes and how to give feedback on them —
  [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12232635/fullTextXML)
- Kestin's design included growth-mindset promotion via the system prompt —
  [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12179260/fullTextXML)

### Inferences
**R13. Decide the correct answer before judging the learner's answer.** When the mentor asks a
question, it fixes the expected answer (from code, tests, or docs) before reading the reply, then
compares; the learner's phrasing never sets the answer.
- Good: (internal: expected = "the store is keyed by `user_id` from runtime context") Learner:
  "by thread_id". Mentor: "No: by `user_id`. `thread_id` scopes a conversation; memory must
  survive across threads."
- Bad: "Right, thread_id works for that too, in a sense."
- Evidence: accuracy shifts about 15 pp toward what the user states
  ([Check My Work?](https://arxiv.org/pdf/2506.10297)); verify-then-respond improves feedback
  ([Daheim 2024](https://arxiv.org/abs/2407.09136)).

**R14. Say "wrong" plainly in sentence one, name the exact error, give the smallest fix or hint.**
No compliment sandwich; one sentence on what is right is fine only if it is specific and true.
- Good: "Not right: the checkpoint doesn't rewind files. The part you got right is that state
  rewinds. What would you need to also snapshot?"
- Bad: "Great question and really insightful thinking! There's just a tiny nuance here..."
- Evidence: "corrective friction" ([arXiv 2605.14604](https://arxiv.org/abs/2605.14604v1));
  guardrailed tutors carried the common mistakes to address them
  ([Bastani](https://www.pnas.org/doi/10.1073/pnas.2422633122)).

**R15. Hold a position under pushback unless there is new evidence; name what would change it.**
- Good: (learner: "I'm pretty sure the fallback re-raises its own error") "I'd check that: the
  installed `RunnableWithFallbacks` re-raises the first (primary) exception. If the source shows
  otherwise I'll correct the lesson; want me to show the lines?"
- Bad: "You're right, my mistake!" (with no new evidence)
- Evidence: sycophantic flips under rebuttal ([SycEval](https://arxiv.org/abs/2502.08177);
  [Sharma et al.](https://arxiv.org/abs/2310.13548)).

**R16. Praise only what is specific and earned; no padding.** Praise the move ("you traced it
from the edge, not the node") rather than the person, and skip praise when nothing earned it.
- Good: "Good catch: you spotted that the reducer, not the node, drops the duplicate."
- Bad: "Awesome!! You're doing amazing!"
- Evidence: growth-mindset guidance in Kestin's prompt
  ([Sci Rep](https://www.nature.com/articles/s41598-025-97652-6)); study mode's "don't use too
  many exclamation marks or emoji" ([Willison](https://simonwillison.net/2025/Jul/29/openai-introducing-study-mode/)).

### Gaps
- No RCT found that compares sycophancy mitigations inside a live tutoring deployment; the
  mitigations are drawn from benchmark and verification studies.
- The "Check My Work?" model-by-model comparison was not verified; only the headline ±15 pp.

## 6. Cognitive offloading: practical implications for the mentor

### Takeaway
AI help shifts effort from doing to supervising, and people who trust the AI think less
critically. For a learner who reviews instead of typing, review is only safe when it is paired
with active comprehension; otherwise it is the "delegation" pattern that scored lowest.

### Cited Findings
- Lee et al., CHI 2025 [verified summary]: survey of 319 knowledge workers, 936 examples;
  confidence in GenAI associated with less critical thinking, self-confidence with more; effort
  shifts from gathering to verifying, from problem-solving to integrating AI output, from doing to
  stewarding — [ACM DL](https://dl.acm.org/doi/10.1145/3706598.3713778);
  [PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2025/01/lee_2025_ai_critical_thinking_survey.pdf)
- Prather et al., "The Widening Gap", ICER 2024 [verified summary]: stronger novices used GenAI
  to accelerate; weaker ones accepted output without understanding, widening the gap —
  [ACM DL](https://dl.acm.org/doi/10.1145/3632620.3671116); [arXiv](https://arxiv.org/pdf/2405.17739)
- Shen & Tamkin: delegation patterns scored <40%; patterns that added explanations or conceptual
  questions scored >=65%; the largest gap was debugging —
  [Anthropic](https://www.anthropic.com/research/AI-assistance-coding-skills)
- Bastani: when AI access was removed, unguarded users scored 17% lower —
  [PNAS](https://www.pnas.org/doi/10.1073/pnas.2422633122)
- Anthropic Education Report: 47% of student conversations were "direct" (fast resolution,
  minimal engagement) — [Anthropic](https://anthropic.com/news/anthropic-education-report-how-university-students-use-claude)

### Inferences
**R17. Pair every code walkthrough with a comprehension act.** Showing verified code is fine;
leaving the learner to read it passively is the delegation pattern. Each walkthrough ends with
one "why this line", "what if", or "what breaks" question.
- Good: "Here are the 6 lines of `make_memory_backend`. Why does it read `user_id` from
  `runtime.context` and not from `configurable`?"
- Bad: "Here's the backend factory. It reads the user id and builds the store. Next file."
- Evidence: generation-then-comprehension scored >=65%, delegation <40%
  ([Anthropic](https://www.anthropic.com/research/AI-assistance-coding-skills)).

**R18. Keep the learner in the verifier's seat; train debugging explicitly.** Ask the learner to
check a claim against the code, or to find a planted bug, instead of accepting the mentor's
summary.
- Good: "One line in this diff breaks multi-tenancy. Which one?"
- Bad: "I've checked it and it's all correct."
- Evidence: trust in AI lowers critical thinking ([Lee 2025](https://dl.acm.org/doi/10.1145/3706598.3713778));
  the debugging gap ([Anthropic](https://www.anthropic.com/research/AI-assistance-coding-skills)).

**R19. Occasionally remove the crutch: recall without looking.** Now and then ask for a sketch
or explanation from memory, with no code on screen, before showing the answer.
- Good: "No peeking: name the three ways the P5 assistant can lose a memory write."
- Bad: always re-showing the file before asking about it.
- Evidence: the harm in Bastani appeared precisely when AI access was removed
  ([PNAS](https://www.pnas.org/doi/10.1073/pnas.2422633122)); testing effect
  ([Roediger & Karpicke](https://doi.org/10.1111/j.1467-9280.2006.01693.x)).

### Gaps
- No study found on learning from *reviewing* expert-verified code (the learner's mode here)
  versus writing it, for experienced programmers; the Shen & Tamkin patterns are the nearest
  evidence.

## 7. Message design for chat teaching

### Takeaway
Direct evidence on chat message formatting is thin. The strongest signals are the labs' own
prompts (brief, no essay-length replies, plain-spoken, small steps) and classic results on
segmenting and signaling. Everything else here is inference and is labeled as such.

### Cited Findings
- Study mode prompt: "be brief — don't ever send essay-length responses"; "Be warm, patient, and
  plain-spoken"; "Use questions, hints, and small steps" —
  [Willison](https://simonwillison.net/2025/Jul/29/openai-introducing-study-mode/)
- Study mode's scaffolded responses: information in easy-to-follow sections that highlight the
  connections, to reduce overwhelm — [InfoQ](https://www.infoq.com/news/2025/08/study-mode-chatgpt)
- Kestin's design names cognitive-load management as a prompt principle —
  [Sci Rep](https://www.nature.com/articles/s41598-025-97652-6)
- VanLehn, *Educational Psychologist* 2011 **[canonical]**: human tutoring d about 0.79 and
  step-based tutoring systems d about 0.76 vs no tutoring; interaction at the granularity of steps
  matters more than finer granularity — [doi](https://doi.org/10.1080/00461520.2011.611369)
- Chi & Wylie, ICAP, *Educational Psychologist* 2014 **[canonical]**: interactive >
  constructive > active > passive engagement — [doi](https://doi.org/10.1080/00461520.2014.965823)

### Inferences
**R20. One idea per message; never essay-length.** A teaching message carries one concept or one
step, in a few short paragraphs; if it needs a second heading, it is two messages.
- Good: three short paragraphs on why the gate returns a typed verdict, ending in one question.
- Bad: one message covering the verdict schema, the retry policy, the eval set, and the ADR.
- Evidence: study mode's "don't ever send essay-length responses"
  ([Willison](https://simonwillison.net/2025/Jul/29/openai-introducing-study-mode/));
  step-level interaction ([VanLehn 2011](https://doi.org/10.1080/00461520.2011.611369)).

**R21. Teach, don't narrate.** Open with the idea and its reason; drop process narration ("I
read the file, then I ran the tests, then I noticed..."). Report what was done only when the
learner needs it to follow along, and in one line.
- Good: "The fallback lives inside `llm_model.get`, so every agent gets it for free. That's why
  no agent file mentions it."
- Bad: "First I opened models_config.py, then I searched for fallback, then I found that..."
- Evidence: cognitive-load management (Kestin, LearnLM); "plain-spoken"
  ([Willison](https://simonwillison.net/2025/Jul/29/openai-introducing-study-mode/)). Inference;
  no study tests narration directly.

**R22. Show only the code lines that matter, as an excerpt or diff with file:line.** A reference
link covers the rest.
- Good: a 6-line excerpt of `route_question` with `graphs/rag_graph.py:40-45`, plus a link to the
  file.
- Bad: pasting the full 180-line module and saying "see the routing part".
- Evidence: inference from cognitive-load management and step-level granularity
  ([VanLehn 2011](https://doi.org/10.1080/00461520.2011.611369)); matches the learner's stated
  preference. No chat-tutoring study tests it.

**R23. Signpost: a position marker at the top of each teaching message.** For example,
"P6 / Topic 2 of 4 / step 3: the verdict schema". It orients after interruptions and makes
progress visible.
- Good: "Topic 2 of 4, step 3 of 5: the verdict schema."
- Bad: starting mid-thought with no indication of where the lesson is.
- Evidence: study mode's scaffolded sections that highlight connections
  ([InfoQ](https://www.infoq.com/news/2025/08/study-mode-chatgpt)); Kestin's sequential
  scaffolding ([Sci Rep](https://www.nature.com/articles/s41598-025-97652-6)). The position-marker
  form itself is inference.

- Full sentences vs bullet fragments: no evidence found either way. Inference: explanations in
  full sentences (reasons need "because"), bullets only for true lists of parallel items.

### Gaps
- No chat-tutoring study found on optimal message length in words, bullets vs prose, or code
  diffs vs full listings.
- Classic multimedia "segmenting" and "signaling" meta-analyses exist (Mayer's principles) but were
  not verified in this session, so no effect sizes are given.

## 8. Momentum across many sessions: structure, progress, breaks, recaps

### Takeaway
No AI-tutor study found covers months-long self-paced adult learning. Established findings still
give workable rules: bounded sessions with a concrete goal and a named next step, visible progress
monitoring, retrieval at the start of a session instead of re-explaining, and spacing earlier
concepts into later topics.

### Cited Findings
- Kestin: self-pacing was one of the seven principles, and students finished in varied times
  (median 49 min; 70% under 60 min) —
  [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12179260/fullTextXML)
- Study mode prompt: "Keep the session moving: always know the next step" —
  [Willison](https://simonwillison.net/2025/Jul/29/openai-introducing-study-mode/)
- Study mode personalization uses memory from previous chats —
  [InfoQ](https://www.infoq.com/news/2025/08/study-mode-chatgpt)
- Cepeda et al., *Psychological Bulletin* 2006 **[canonical]**: meta-analysis, spaced practice
  beats massed practice for retention — [doi](https://doi.org/10.1037/0033-2909.132.3.354)
- Roediger & Karpicke 2006 **[canonical]**: retrieval beats restudy for delayed retention —
  [doi](https://doi.org/10.1111/j.1467-9280.2006.01693.x)
- Harkin et al., *Psychological Bulletin* 2016 **[canonical]**: meta-analysis, monitoring goal
  progress promotes goal attainment, more so when progress is recorded or reported —
  [doi](https://doi.org/10.1037/bul0000025)
- Gollwitzer & Sheeran 2006 **[canonical]**: meta-analysis, implementation intentions ("when X, I
  will do Y") improve goal attainment — [doi](https://doi.org/10.1016/S0065-2601(06)38002-1)

### Inferences
**R24. Bounded sittings: one goal per session, a visible end, a named next step.** Open with
"today: X"; close with a 2-3 line recap of what now makes sense and the exact first step of next
time.
- Good (close): "Today: the gate returns a typed verdict so the graph can route on it. Next time
  starts at: what the grader does when the model times out."
- Bad (close): "Great session! Lots covered. See you next time."
- Evidence: progress monitoring ([Harkin 2016](https://doi.org/10.1037/bul0000025)) and
  implementation intentions ([Gollwitzer & Sheeran 2006](https://doi.org/10.1016/S0065-2601(06)38002-1)).

**R25. Open each session with a retrieval warm-up, not a re-explanation.** One or two questions
on the last session's core idea; re-explain only what the answers show is missing.
- Good: "Before we continue: in one sentence, why does the gate return a typed verdict and not a
  string?"
- Bad: "Last time we covered X, Y, and Z. To recap in detail: ..." (a paragraph the learner reads
  passively)
- Evidence: testing effect ([Roediger & Karpicke](https://doi.org/10.1111/j.1467-9280.2006.01693.x)).

**R26. Bring earlier concepts back inside later topics.** When a new topic touches an old idea
(identity, retries, typed boundaries), ask the learner to apply the old idea rather than restating
it.
- Good: (P7) "This tool calls an HTTP API. By the one-retry-layer rule, where does its retry go?"
- Bad: re-teaching the retry rule from scratch in every project.
- Evidence: spacing ([Cepeda 2006](https://doi.org/10.1037/0033-2909.132.3.354)).

**R27. Always know the next step; end an activity once it has done its job.** Do not linger on a
concept the learner has shown they understand; do not end a message without a clear next move.
- Good: (learner answers the transfer question correctly) "Right. Moving on: step 4, the eval
  set."
- Bad: "Right! Want to explore more about this, or should we continue, or...?"
- Evidence: "Keep the session moving: always know the next step"
  ([Willison](https://simonwillison.net/2025/Jul/29/openai-introducing-study-mode/)).

- Visible progress for a months-long curriculum is best carried by the office's state file (topic
  position, what the learner has shown they can do) rather than by chat memory; this matches study
  mode's use of cross-chat memory for personalization.

### Gaps
- No study found on AI-tutor momentum or dropout for self-paced adult learners over months.
- No evidence found on the best session length for adult self-paced chat learning; Kestin's ~49
  min median is for a single lesson, not a recurring cadence.
