# Teaching Through Code Reading and Review: A Technique Catalog for an Experienced Learner

Scope: what the mentor does, step by step, when walking an experienced adult programmer through a
senior engineer's verified code in chat (text, snippets, live demo runs). The learner doesn't type
lesson code. Each section gives the technique's steps, a worked example on real agentlab code
(`src/agentlab/graphs/rag_graph.py`, `src/agentlab/nodes/rag_node.py`,
`src/agentlab/schemas/state/rag_state.py`, `MAX_RETRIES = 2` in `configs/rag_config.py`), when it
helps or backfires for an experienced learner, and a one-line evidence note.

**Caveat that applies to every section:** almost all the CS-education evidence below comes from
novices (school pupils or CS1/CS2 students). Transfer to an experienced adult is an inference,
marked as such. The code-review evidence (Microsoft, Google) is the only strand drawn from
professionals.

The worked examples use this real code (quoted exactly):

```python
def route_after_grading(state: RAGState) -> Literal["generate", "query_rewrite", "web_search"]:
    if state.get("documents"):
        return "generate"
    if state.get("retries", 0) < MAX_RETRIES:
        return "query_rewrite"
    return "web_search"

# in build_rag_graph():
graph.add_node("retrieve", retrieve_node, retry_policy=TRANSIENT_RETRY)
graph.add_node("grade_documents", grade_documents_node)
graph.add_node("query_rewrite", query_rewrite_node)
...
graph.add_node("web_search", web_search_node, retry_policy=TRANSIENT_RETRY)
graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "grade_documents")
graph.add_conditional_edges("grade_documents", route_after_grading)
graph.add_edge("query_rewrite", "retrieve")
```

Relevant facts from the nodes and state: `grade_documents_node` returns `{"documents": relevant}`
(an overwrite; `RAGState.documents` has no reducer); `query_rewrite_node` returns
`{"search_query": <rewritten>, "retries": state.get("retries", 0) + 1}`; `RAGState`'s docstring says `search_query`
and `retries` are per-question scratch fields that a caller reusing a thread must reset.

---

## 1. PRIMM in practice: Predict, Run, Investigate on existing code, without Modify

### Takeaway
PRIMM's front half (Predict, then Run to check the prediction, then Investigate with targeted
comprehension tasks) maps directly onto a no-typing walkthrough. For this learner, "Modify"
becomes "predict the effect of a proposed change, then the mentor runs the variant". The
evidence is a school-age quasi-experiment, so the structure transfers but the effect size doesn't.

### Cited Findings
- PRIMM = Predict, Run, Investigate, Modify, Make. Its five principles: read code before you write
  code; work collaboratively and talk about programs; focus on comprehension, with tasks aligned
  to the Block Model; use existing starter programs (the learner "does not have responsibility for
  the code and does not suffer emotionally if the code has errors"); and gradually take ownership
  (built on Use-Modify-Create). — [Sentance 2021, RPF seminar proceedings](https://www.raspberrypi.org/app/uploads/2022/08/Teaching_Programming_with_PRIMM-1.pdf)
- A PRIMM lesson "starts with an activity whereby learners examine some existing code and predict
  what it might do"; learners then test their predictions by running the code. — [Sentance 2021](https://www.raspberrypi.org/app/uploads/2022/08/Teaching_Programming_with_PRIMM-1.pdf)
- Investigate tasks named in teacher guidance: trace programs to find end states or the inputs
  needed to reach a state; investigate the effect of swapping two lines; find lines that can never
  run; Parsons problems; explain the purpose of a line, snippet, or program; give meaningful names;
  compare programs for functional equivalence. The guidance notes that "many of these activities
  are also good examples of the 'Investigate' phase". — [NCCE Pedagogy Quick Read: Block Model](https://media.teachcomputing.org/QR_12_Block_model_8956b6555c.pdf), citing Sentance (2020) "The I in PRIMM", *Hello World* 14
- In teacher interviews (n=20), teachers reported less whole-class talk and more "probing"
  questions in PRIMM lessons, plus more student-to-student dialogue and more confident use of
  programming vocabulary. This is early, qualitative, interview-based evidence. — [Sentance 2021](https://www.raspberrypi.org/app/uploads/2022/08/Teaching_Programming_with_PRIMM-1.pdf)
- The dialogue model PRIMM draws on: *uptake* (build the next question on the learner's answer),
  *authentic questions* (explore views, not test known answers), and *high-level evaluation*
  (elaborate on the response). Initiation-Response-Feedback quizzing has been criticized for
  inhibiting the development of ideas. — [Sentance 2021](https://www.raspberrypi.org/app/uploads/2022/08/Teaching_Programming_with_PRIMM-1.pdf)
- **Evidence:** a quasi-experiment with a non-equivalent control group and post-test, 13 schools,
  493 students aged 11-14, 8-12 weeks of lessons. The PRIMM group scored significantly higher on
  the post-test. The effect size is not stated in the sources I read. — [Sentance, Waite & Kallia 2019, *Computer Science Education* 29(2-3)](https://www.tandfonline.com/doi/abs/10.1080/08993408.2019.1608781); [RPF CERC project page](https://computingeducationresearch.org/projects/primm/)

### Inferences
**Mentor steps (applied design):**
1. *Frame.* Name the component and the one scenario to predict. Show only the code needed.
2. *Predict (committed).* The learner writes the prediction plus one line of reasoning before
   anything runs. Ask for a concrete, checkable output: a path, a count, a final state value.
3. *Run.* Run the demo live (test mode) and show the evidence: output, streamed node updates, or
   checkpoint history (`uv run lab-rag`, then `history` / `replay <i>`).
4. *Reconcile.* If the prediction was wrong, ask "which line made the difference?" before
   explaining anything. Use uptake: build the next question on the learner's wording.
5. *Investigate.* Give two to four targeted tasks drawn from the Block Model grid (section 2):
   one execution task, one relations task, one purpose or design task.
6. *Modify-in-mind (replaces Modify).* Propose a one-line change and have the learner predict the
   new behavior. The mentor applies it in a scratch copy and runs it. The learner still types
   nothing.
7. *Make → defend.* For the experienced learner, "Make" becomes "defend or attack the design
   choice", or "name the production risk".

**Worked example (RAG retry loop):**
- *Predict:* "A question the corpus can't answer (grading keeps nothing each time), and web search
  returns results. List the node sequence. How many times does `retrieve` run, ignoring transient
  retries?"
- *Expected:* `retrieve → grade_documents → query_rewrite (retries=1) → retrieve → grade_documents →
  query_rewrite (retries=2) → retrieve → grade_documents → web_search → generate_from_web → END`.
  `retrieve` runs 3 times, because `retries` is read *before* `query_rewrite` increments it and
  `2 < 2` is false.
- *Run:* `LLM_TEST_MODE=true uv run lab-rag` with an off-corpus question. Then `history` to show
  the checkpoints next to the prediction.
- *Investigate:* (a) "Which node writes `retries`, and which function reads it?" (relations);
  (b) "`grade_documents_node` returns `{"documents": relevant}`. What happens to the documents from
  the previous retrieve?" (they're overwritten, with no reducer); (c) "Why does `retry_policy`
  appear only on `retrieve` and `web_search`?" (AGENTS.md convention 11: model calls are never
  wrapped in another retry, and each node has one external dependency).
- *Modify-in-mind:* "Change `<` to `<=`. How many retrieves now?" (4). Or: "The caller reuses the
  thread for a second off-corpus question and forgets to reset `retries`. What path runs?"
  (`retrieve → grade → web_search`: no rewrite at all, a silent quality regression). The mentor
  runs the variant.

**Helps / backfires for an experienced learner:**
- Helps: committed prediction exposes wrong framework assumptions (reducers, routing timing,
  retry scope) that an expert would otherwise read past. Run-to-check gives immediate, objective
  feedback.
- Backfires: predicting trivial code (plain wiring, obvious guards) is redundant and irritating.
  Predict only where framework semantics or cross-node state make the outcome non-obvious. The
  school-age "talk with peers" element has no direct counterpart one-on-one; the mentor has to
  play the questioning partner.

### Gaps
- I found no PRIMM study with adult or professional learners, and no published effect size in
  the sources I read (the full CSE paper is paywalled).
- I didn't access "The I in PRIMM" (*Hello World* 14) directly; its Investigate task list is
  known only through the NCCE summary.

---

## 2. The Block Model as a question generator

### Takeaway
The Block Model is a 4x3 grid: *scope* (Atoms, Blocks, Relations, Macro) crossed with *dimension*
(Text surface, Program execution, Function/purpose). It generates a balanced question set for any
component. It is a design framework, not an intervention with an efficacy trial. For an
experienced learner, spend most questions in the Relations and Macro rows and in the
Function/purpose column.

### Cited Findings
- The grid and its example tasks, cell by cell:
  - Atoms: identify statement types (T); trace values (P); explain the purpose of a single line (F).
  - Blocks: identify block types (T); reorder lines, Parsons problems (P); explain the purpose of
    a block (F).
  - Relations: identify variable scope, highlight function calls (T); draw the flow of control,
    find redundant conditional branches (P); choose a name for a variable or function, decide
    whether two segments are functionally equivalent (F).
  - Macro: annotate or diagram the overall structure, restructure an untidy program (T); identify
    the inputs needed to test all branches, "Will line X ever be executed?" (P); choose a name for
    the program, write a sentence that describes its purpose (F).

  — [NCCE Pedagogy Quick Read: Block Model](https://media.teachcomputing.org/QR_12_Block_model_8956b6555c.pdf)
- The educator's use: "categorise tasks and identify gaps where students need support". Learners
  should be able to move between all 12 zones. The linked "holey quilt" idea says knowledge in
  each zone ranges from fragile to deep. — [NCCE Quick Read](https://media.teachcomputing.org/QR_12_Block_model_8956b6555c.pdf); [Schulte 2008, ICER](https://www.researchgate.net/publication/247927531_Block_Model_an_educational_model_of_program_comprehension_as_a_tool_for_a_scholarly_approach_to_teaching)
- The model's developmental claim: novices first learn atoms, then block patterns, then relations
  between blocks, and finally the macro view. — [KSU "Teaching and Learning CS": The Block Model](https://textbooks.cs.ksu.edu/tlcs/4-designing-cs-lessons/06-the-block-model/)
- A teacher-focused ITiCSE 2019 study identified more than 60 comprehension activities and found
  that many were used to *assess* comprehension rather than to develop it. — [NCCE Quick Read](https://media.teachcomputing.org/QR_12_Block_model_8956b6555c.pdf) citing Izu et al. 2019
- Block-Model-typed questions have been generated automatically about learners' *own* code to
  detect "fragile knowledge". — [arXiv 2306.16267, "Automated Questions About Learners' Own Code Help to Detect Fragile Knowledge"](https://arxiv.org/pdf/2306.16267) (not read in full)
- **Evidence:** a conceptual framework (Schulte 2008 ICER; Schulte et al. 2010 ITiCSE working
  group). I found no controlled trial of "Block-Model-balanced questioning" versus alternatives.

### Inferences
**Mentor steps (applied design):**
1. Pick the component. Draft one question per cell (12), then keep the 4-6 that hit
   non-obvious framework or design semantics.
2. Order the questions from the learner's likely strong zone toward the weak one. For an expert:
   Blocks/Execution → Relations/Execution → Relations/Function → Macro/Function.
3. After each answer, ask one uptake question that moves up a row ("so what does that mean for
   the node that reads it?") or across a column ("and why was it built that way?").
4. Log which zones were fragile. They set the next component's question mix.

**Worked example (a grid for `route_after_grading` and `build_rag_graph`):**
- Atom/Text: "Why `state.get("retries", 0)` and not `state["retries"]`?" (`retries` is
  `NotRequired`)
- Atom/Execution: "`documents == []`, `retries == 2`. What does it return?" (`"web_search"`)
- Block/Function: "Name the loop pattern in three or four words." ("bounded retry with fallback")
- Relations/Text: "Which node writes `retries`? Who reads it?" (`query_rewrite_node` writes it;
  `route_after_grading` reads it)
- Relations/Execution: "`grade_documents` returns `{"documents": relevant}`. What does
  `generate` see after two rounds?" (only the last round's relevant documents: an overwrite)
- Relations/Function: "Why are the retry policies on `retrieve` and `web_search` only?"
- Macro/Execution: "Give the minimum set of inputs that exercises every edge." (answerable in the
  corpus; off-corpus with web hits; off-corpus with no web hits; plus hallucination-check pass
  and fail)
- Macro/Function: "One sentence: what is this graph's contract to its caller?"

**Helps / backfires:**
- Helps: it prevents a walkthrough stuck at the level where an expert is already fluent (atoms,
  syntax), and makes gaps visible.
- Backfires: covering all 12 cells mechanically. Atoms/Text questions ("what is a dict?") insult
  an experienced learner; keep Atom questions only for framework-specific atoms (`retry_policy`,
  `NotRequired`, `END`).

### Gaps
- No efficacy trial found for Block-Model-guided questioning. Its value rests on framework
  coherence and teacher adoption.
- I didn't fetch the Izu et al. 2019 ITiCSE working-group report on learning trajectories, which
  would give ordered activity sequences.

---

## 3. "Explain in plain English" (EiPE): asking, and judging relational vs multistructural answers

### Takeaway
Ask the learner for a short, purpose-level description of a code fragment. A good answer is
*relational* (what it's for). A *multistructural* answer walks through the code line by line.
Judge on three axes: correctness, level of abstraction, and ambiguity. Set a word limit and show
one good and one bad example answer first, or answers drift into long line-by-line narration.

### Cited Findings
- SOLO categories for EiPE (Whalley et al.): *Relational* = "a summary of what the code does in
  terms of the code's purpose"; *Multistructural* = "a line by line description ... of all the
  code"; *Unistructural* = a description of one portion only; *Prestructural* = lacking
  knowledge or unrelated. — [Chen et al. 2020, SIGCSE, Table 1](https://zilles.cs.illinois.edu/papers/EiPE_rubric_sigcse_2020.pdf)
- The 4-level SOLO rubric was hard to apply reliably because answers vary on three dimensions:
  level of abstraction, correctness, and ambiguity. The replacement is a 7-point scale (0-6).
  6 = all key ideas, correct, at a high level of abstraction. 4 = key ideas present, but an
  incorrect reading is possible through imprecise language (for example, "stores X in a local
  variable" without saying it is returned). 2 = mostly correct and high-level, but at least one
  thing clearly wrong. 1 = very low-level or multiple errors. 0 = an English transliteration of
  the statements. When an answer fits several categories, assign the lowest. — [Chen et al. 2020](https://zilles.cs.illinois.edu/papers/EiPE_rubric_sigcse_2020.pdf)
- Question design: code fragments are "straightforward implementations of common ... tasks"
  describable in "a short (12 or less words) sentence", with no tricks or unusual syntax. After
  early trials, students were shown desirable and undesirable sample answers, because "students
  were otherwise prone to give long, low-level, and over-complete answers". — [Chen et al. 2020](https://zilles.cs.illinois.edu/papers/EiPE_rubric_sigcse_2020.pdf)
- The skill sits between tracing and writing: explaining requires "consider[ing] how the code
  behaves over all possible inputs". Tracing and code-reading performance accounted for 46% of
  the variance in code writing (Lopez et al.). Students who can't explain relationally early in a
  course struggle to write code later. — [Chen et al. 2020](https://zilles.cs.illinois.edu/papers/EiPE_rubric_sigcse_2020.pdf) summarizing Lopez et al. 2008 and a longitudinal study
- Corney et al. suggest EiPE's value "may therefore be more as formative assessment rather than
  summative assessment". — quoted in [Chen et al. 2020](https://zilles.cs.illinois.edu/papers/EiPE_rubric_sigcse_2020.pdf)
- Recent variant: asking for a *function name* as a compact test of comprehension. — [arXiv 2503.12207, "ReDefining Code Comprehension: Function Naming..."](https://arxiv.org/pdf/2503.12207) (not read in full)
- **Evidence:** a rubric validation. 10,024 responses to 52 questions (CS1 and data structures);
  inter-rater Krippendorff's alpha 0.775 (median); a 12-question survey with Cronbach's alpha
  0.954; EiPE scores correlated with code writing at r = 0.555 (N = 452). — [Chen, Azad, Haldar, West, Zilles 2020](https://zilles.cs.illinois.edu/papers/EiPE_rubric_sigcse_2020.pdf)

### Inferences
**Mentor steps (applied design):**
1. Choose a fragment with one clear purpose (a router, a node, a reducer). Hide or strip the
   docstring, which gives the answer away.
2. Ask: "In one sentence, at most 15 words, what is this *for*?" For the first EiPE only, show
   one bad answer (a line-by-line one) and one good answer on a *different* fragment.
3. Score silently on three checks. Is it correct? Is it at the purpose level, or narrating
   lines? Is anything ambiguous? Give feedback on the weakest axis only.
4. Follow up with "for all inputs?" Ask for the edge case the sentence glosses over. This tests
   the "over all possible inputs" part.
5. Reveal the docstring and compare. Discuss differences in abstraction, not in wording.

**Worked example (`route_after_grading`, docstring hidden):**
- Multistructural (score about 1-2): "If there are documents it returns generate, else if retries
  is less than MAX_RETRIES it returns query_rewrite, else web_search."
- Relational, ambiguous (about 4): "Decides whether to retry." Correct in spirit but misses the
  fallback and the success path.
- Relational (6): "Answer from the corpus if grading kept anything; else retry rewritten, then
  fall back to the web." Or, at the design level: "a bounded self-correction loop with a web
  fallback."
- Follow-up: "Is 'retry up to MAX_RETRIES times' exact?" (Yes: 2 rewrites, 3 retrievals. Check
  the learner's arithmetic against `<`.)

**Helps / backfires:**
- Helps: this is a fast, high-signal check of whether an expert grasped the *purpose* and the
  design intent, not just the mechanics. It fits in one chat turn.
- Backfires: on trivial fragments (an expert answers relationally at once, which wastes a turn),
  and on fragments whose purpose is only clear across files; then it becomes a Macro question and
  needs the cross-file context first.

### Gaps
- The original Lister/Whalley/Murphy/Corney papers weren't opened directly; their claims are
  taken from Chen et al.'s literature summary.
- No EiPE study with professional developers found.

---

## 4. Code reading clubs (Hermans; codereading.club): the activities and a one-on-one adaptation

### Takeaway
Code Reading Club is a practitioner protocol: a fixed sequence of short, timed reading activities
(first glance → structure → names → important lines → summary → "why"). It adapts well to
one-on-one chat as a 10-20 minute opening for any new component, with the mentor as the second
reader who compares selections. I found no controlled efficacy study.

### Cited Findings
- Format: "a bit like a book club, and a bit like an escape room". A small group meets about
  1 hour every other week to read short code samples, "inspired by research and teaching
  exercises designed by Felienne Hermans". — [codereading.club](https://codereading.club/); [CodeReadingClubs/Resources](https://github.com/CodeReadingClubs/Resources)
- The basic exercise sequence (each is individual work, then group discussion):
  1. *First glance* (1 min scan): note what catches the eye first and second, and whether they
     relate.
  2. *Code structure* (10 min): circle variables, methods, and instances in different colors and
     link each to its uses; ask which sections deserve deeper attention.
  3. *Names* (5 min): list all identifiers; discuss what they reveal and any ambiguous ones.
  4. *Random line* (5 min): pick a line and establish its purpose and connections.
  5. *Most important lines* (10 min): agree on what "important" means, then each picks 5 lines;
     compare consensus and outliers.
  6. *Save the last word*: rotating 30-second contributions, adding only new information.
  7. *Individual summary* (10 min, at most 10 sentences): compare coverage and strategy.
  8. *Collaborative summary*: compare with existing documentation.

  Advanced exercises: data-flow density; the 5 central domain concepts; the 5 central programming
  concepts; *The "why" of the code* ("document creator decisions and underlying assumptions";
  discuss advantages, drawbacks, alternatives). — [neontribe/code-reading-club exercises.md](https://github.com/neontribe/code-reading-club/blob/trunk/exercises.md)
- In first glance, "different people notice different things", such as familiar constructs,
  naming, comments, or imports. — [Hermans, "Code Reading Club"](https://www.felienne.com/archives/6472) via search summary; [codereading.club](https://codereading.club/)
- An annotation tool imports GitHub files, highlights spans, and links them with arrows. — [annotate.codereading.club](https://annotate.codereading.club/)
- Hermans' *The Programmer's Brain* (Manning 2021) gives memory aids for overloaded reading:
  dependency graphs, state tables, and the combination of the two; and Sajaniemi's 11 "roles of
  variables" (for example "fixed value", or "stepper" for a loop index), with a flowchart for
  assigning roles. — [O'Reilly TOC](https://www.oreilly.com/library/view/the-programmers-brain/9781617298677/Text/HermansTOC.htm); [reading notes (M. Salmon, 2026)](https://masalmon.eu/2026/08/21/the-programmer-s-brain-reading-notes/)
- **Evidence:** a practitioner protocol grounded in Hermans' research program. I found no
  controlled evaluation of the club format itself.

### Inferences
**One-on-one adaptation (applied design, about 15 min per new component):**
1. *First glance* (learner, 60 s): "What caught your eye first and second? Do they relate?" The
   mentor shares its own pick. The divergence is the discussion.
2. *Structure in text* (dependency list): the learner lists "node → state keys it writes/reads".
   The mentor fills gaps. This is the text form of Hermans' dependency graph.
3. *Names*: "Which identifier is least clear out of context?" (for example `TRANSIENT_RETRY`,
   `answer_source`). This feeds a conventions discussion.
4. *Five most important lines*: learner and mentor each pick independently; then compare. This
   is the densest single signal of whether the learner found the design center.
5. *Summary in 3 sentences at most*, then compare with the module docstring (the
   "collaborative summary vs documentation" step).
6. *The "why"*: pick 2 decisions; for each, ask for the assumption behind it and one alternative.
   This bridges into the mentor's "why this design? / what if X changed?" questions.

**Worked example (`rag_graph.py`):**
- First glance: an expert often notices `retry_policy=TRANSIENT_RETRY` on only two nodes, or the
  `query_rewrite → retrieve` back-edge.
- Five lines, the mentor's pick: `add_conditional_edges("grade_documents", route_after_grading)`;
  `add_edge("query_rewrite", "retrieve")`; `if state.get("retries", 0) < MAX_RETRIES`;
  `retry_policy=TRANSIENT_RETRY` on `retrieve`; the `checkpointer ... InMemorySaver()` default.
  If the learner's five are all `add_node` lines, the design center was missed.
- Roles of variables: `MAX_RETRIES` is a fixed value; `retries` behaves as a stepper (a counter
  across loop iterations, persisted in graph state rather than in a local variable).
- "Why": "Why is the retry counter in graph state, not a Python loop inside one node?" (It makes
  each attempt observable in checkpoints and replayable, and each node keeps one external
  dependency.)

**Helps / backfires:**
- Helps: it gives a consistent opening ritual; exposes where the learner's attention goes; costs
  little.
- Backfires: timed "phonetic" exercises (reading aloud, listing all names) are low-value for an
  expert on short files. Keep first glance, important lines, and "why", and drop the rest unless
  the file is large or unfamiliar. The group-discussion value (divergent perspectives) shrinks to
  two perspectives one-on-one.

### Gaps
- No outcome data found for code reading clubs. The book's specific exercises were confirmed
  only via the table of contents and secondary notes, not the book text.
- Only two of Sajaniemi's 11 variable roles are confirmed here; take the full list from the book.

---

## 5. Subgoal labels and annotated worked examples, with fading

### Takeaway
Subgoal labeling means placing short functional labels over chunks of a worked example so the
structure, not just the steps, is visible. The CS evidence is mostly CS1-level. For an
experienced learner, label only unfamiliar framework structure, and fade quickly: mentor labels,
then learner labels mentor-given chunks, then learner chunks and labels.

### Cited Findings
- Subgoal labels are claimed to work by emphasizing the worked example's structure, helping
  learners organize information, and improving self-explanation. The claimed mechanism is that
  "labels make the functional organisation of examples easier to notice". — [Frontiers in Education 2022, review section](https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2022.832901/full); [eduKate summary (secondary)](https://edukatesg.com/2026/09/11/how-subgoal-labeling-works-name-structural-step-procedure-easier-to-learn/)
- Morrison, Margulieux & Guzdial (ICER 2015, ICER Paper Award) asked whether *giving* learners
  subgoal labels is more or less effective than asking them to *generate* labels in an
  introductory programming task. — [ACM DL](https://dl.acm.org/doi/10.1145/2787622.2787733); [Nebraska research portal](https://experts.nebraska.edu/en/publications/subgoals-context-and-worked-examples-in-learning-computing-proble)
- Subgoal learning had been tested mostly in one-to-two-hour sessions, before Margulieux et al.
  implemented subgoal-labeled worked examples across an entire introductory course. — [Margulieux et al. 2020, *IJ STEM Education*](https://link.springer.com/article/10.1186/s40594-020-00222-7)
- Morrison, Margulieux & Decker aggregated three studies of subgoal-labeled worked examples across
  populations and designs. — [search summary of Morrison et al., "The Curious Case of Loops" (CSE 2020)](https://eric.ed.gov/?id=EJ1261187)
- Subgoals have also been tested with Parsons problems. — [Morrison et al. 2016, SIGCSE, "Subgoals Help Students Solve Parsons Problems"](https://dl.acm.org/doi/10.1145/2839509.2844617)
- Worked examples lose effectiveness, and can hamper learning, as prior knowledge grows (the
  expertise reversal effect; see section 10). In a programming-adjacent study (programmable logic
  controllers), the worked-example advantage disappeared as trainees gained experience. — [Kalyuga 2007, *Educational Psychology Review*](https://link.springer.com/article/10.1007/s10648-007-9054-3); [search summary of Kalyuga et al. 2001](https://www.researchgate.net/publication/225767816_Expertise_Reversal_Effect_and_Its_Implications_for_Learner-Tailored_Instruction)
- **Evidence:** multiple CS1-level experiments and a course-wide deployment (Morrison, Margulieux
  et al. 2015-2020). The exact effect sizes and the direction of the given-vs-generated result
  weren't verified here (the PDFs were blocked).

### Inferences
**Mentor steps (applied design):**
1. Split the component into 3-6 chunks by *function*, not by syntax.
2. **Stage A (first component of a new framework idiom):** the mentor shows the code with labels
   as comments above each chunk, and asks the learner to explain why each chunk earns its label.
3. **Stage B (next component):** the mentor marks chunk boundaries only; the learner writes the
   labels. The mentor compares with its own labels and discusses the differences (Morrison 2015's
   "generate" condition, adapted).
4. **Stage C:** the learner chunks and labels unaided. The mentor critiques only mislabeled or
   missing chunks.
5. Move back one stage when a new framework mechanism appears (subgraphs, interrupts,
   middleware). Skip labeling entirely for idioms the learner already reads fluently.

**Worked example (Stage A labels on `build_rag_graph`):**
```text
# [1] Register nodes; attach a retry policy only where a non-model external call lives
#     (retrieve = embeddings, web_search = search API)
# [2] Wire the fixed spine: START -> retrieve -> grade_documents
# [3] Branch on the grader's verdict (route_after_grading): answer / rewrite / web
# [4] Close the self-correction loop: query_rewrite -> retrieve
# [5] Terminal paths: generate -> check_hallucination -> END; web -> generate_from_web -> END
# [6] Compile with persistence (default InMemorySaver) so every step is checkpointed
```
Stage B on the next graph (for example `code_review_parentgraph.py`): give only
`# [1] ... # [2] ...` markers and ask for the labels.

**Helps / backfires:**
- Helps: on new framework structure (the first StateGraph, the first subgraph composition),
  labels speed up seeing the architecture. Learner-generated labels double as an EiPE check.
- Backfires: fully labeled examples of familiar patterns are redundant for an expert (expertise
  reversal). They add reading load and signal distrust. Fade fast. A learner who produces
  purpose-level labels at Stage B skips to C.

### Gaps
- The direction and size of the Morrison 2015 given-vs-generated result is unverified here; it
  needs the full text.
- No subgoal-labeling study with professional developers or framework code found.

---

## 6. Tracing and notional-machine sketches for runtime behavior in text

### Takeaway
An explicit, lightweight tracing strategy (go line by line and update an external memory table)
measurably helps novices. Notional machines are simplified models of execution that teachers
choose deliberately, sometimes several in sequence. For graph code, the useful text formats are
a state-trace table, a one-line path ladder, and a per-step state diff, each checked against a
live run's checkpoints.

### Cited Findings
- Xie, Nelson & Ko's tracing strategy: line-by-line tracing plus "an external representation of
  memory for them to update". Taught in 5-10 minutes; block-randomized with 24 CS1 novices;
  strategy users scored about 15% higher on the study's tracing problems (p < 0.05). — [Xie, Nelson & Ko 2018, SIGCSE](https://www.benjixie.com/publication/sigcse-2018/); [Bits and Behavior post](https://medium.com/bits-and-behavior/teaching-a-strategy-for-reading-code-fbc9f4044cab)
- Hermans recommends state tables (tracking variable values through execution) and dependency
  graphs as memory aids when code overloads working memory, and combining the two. — [O'Reilly TOC](https://www.oreilly.com/library/view/the-programmers-brain/9781617298677/Text/HermansTOC.htm); [R-bloggers notes](https://www.r-bloggers.com/2026/08/reading-notes-on-the-programmers-brain-by-felienne-hermans/)
- A notional machine is "a pedagogic device to assist the understanding of some aspect of
  programs or programming". The ITiCSE 2020 working group defined its characteristics and
  documented instructors using multiple notional machines in sequence. A curated catalog exists.
  — [Fincher et al. 2020, ITiCSE-WGR](https://dl.acm.org/doi/10.1145/3437800.3439202); [notionalmachines.github.io](https://notionalmachines.github.io/)
- Code tracing itself is hard for many learners. The known difficulties include single-value
  tracing, confusing function with structure, external representations, and levels of
  abstraction. — [Sentance 2021](https://www.raspberrypi.org/app/uploads/2022/08/Teaching_Programming_with_PRIMM-1.pdf) citing Vainio & Sajaniemi 2007
- In a 941-student, 7-country study, many students were weak at predicting the outcome of short
  code. Researchers collected students' "doodles" (scratch tracing) alongside MCQ answers. — [Lister et al. 2004, ITiCSE WG](https://dl.acm.org/doi/10.1145/1041624.1041673)
- A 2026 multi-institutional study evaluated AI-generated traces for novices. — [arXiv 2606.03288](https://arxiv.org/pdf/2606.03288) (not read)
- **Evidence:** a small randomized experiment (Xie et al., N = 24 novices) plus a
  definitional/catalog working group. No tracing-format study for graph or async runtimes found.

### Inferences
**Mentor steps (applied design):**
1. Name the notional machine first, in one sentence. For LangGraph: "Each node reads the whole
   state and returns a partial update. Updates are merged (overwrite unless a reducer says
   otherwise). The router reads the merged state and picks the next node. Every step is
   checkpointed."
2. Give the learner an empty trace table with fixed columns, and have them fill the first 2-3
   rows (committed prediction).
3. Run the demo and show the real sequence (streamed updates or checkpoint `history`). The
   learner marks where the table diverged.
4. Add overlays one at a time, never all at once: failure (where can `TRANSIENT_RETRY` re-run a
   node?), then persistence (what survives on the thread?), then concurrency or async (only when
   the component has it).

**Text formats that work in chat:**
- *State-trace table* (the main one):
```text
step | node             | writes                         | retries | #docs | router -> next
1    | retrieve         | documents=[d1..d4]             | 0       | 4     | -> grade_documents
2    | grade_documents  | documents=[]  (overwrite)      | 0       | 0     | 0<2 -> query_rewrite
3    | query_rewrite    | search_query=..., retries=1    | 1       | 0     | -> retrieve
4    | retrieve         | documents=[d5..d8]             | 1       | 4     | -> grade_documents
5    | grade_documents  | documents=[]                   | 1       | 0     | 1<2 -> query_rewrite
6    | query_rewrite    | retries=2                      | 2       | 0     | -> retrieve
7    | retrieve         | documents=[...]                | 2       | 4     | -> grade_documents
8    | grade_documents  | documents=[]                   | 2       | 0     | 2<2 false -> web_search
9    | web_search       | documents=[w1..w3]             | 2       | 3     | -> generate_from_web
```
  (Row 3 matches `query_rewrite_node`, which returns `{"search_query": ..., "retries": ... + 1}`.
  Document ids are illustrative.)
- *Path ladder* (for quick predictions): `retrieve → grade(0) → rewrite(r=1) → retrieve →
  grade(0) → rewrite(r=2) → retrieve → grade(0) → web → gen_web → END`
- *Per-step diff* (for reducer questions): `step 2: documents: [4 docs] → []  (replace; no reducer)`
- *Failure overlay*: `retrieve [TRANSIENT_RETRY: re-runs only the embedding call] ... grade
  [no node retry: model SDK retries + fallback]`
- *Thread-persistence overlay*: `thread T, question 2: retries starts at 2 unless the caller
  resets it → step 2 routes straight to web_search`

**Helps / backfires:**
- Helps: runtime behavior spread across nodes, routers, reducers, retries, and checkpoints is
  exactly where an expert's general intuition (a sequential call stack) misleads. The table
  externalizes the framework's model.
- Backfires: full line-by-line tracing inside a node body the expert can read at a glance. Trace
  at node granularity, and drop to line level only inside the router or reducer. Too many
  overlays at once overload even an expert.

### Gaps
- No study found on tracing formats for dataflow, graph, or async runtimes, or with experienced
  developers.
- The Lister 2004 finding on whether doodling correlates with success was not verified in my
  reading.

---

## 7. Comparing two versions: before/after, contrasting cases, alternative designs

### Takeaway
Side-by-side comparison of two solutions to the same problem has replicated evidence in CS2
(Patitsas et al. 2013, replicating Rittle-Johnson & Star's math results). For an experienced
learner, contrasting *design alternatives* is likely the highest-value reading format, because
it forces the "why this design?" reasoning the curriculum targets.

### Cited Findings
- Patitsas, Craig & Easterbrook tested whether comparing and contrasting different solution
  approaches increases learning in CS, replicating Rittle-Johnson & Star. Design:
  pretest-intervention-posttest-follow-up, 241 participants, an in-class CS2 workbook. The results
  agreed with Rittle-Johnson & Star, suggesting the effect generalizes to CS. — [Patitsas, Craig & Easterbrook 2013, ICER](https://dl.acm.org/doi/10.1145/2493394.2493409); [author PDF](http://www.cs.toronto.edu/~patitsas/icer_2013_mscthesis.pdf)
- Block Model Function-column tasks include "are two programs/segments functionally equivalent?"
  and matching a program to a purpose description, which are comparison tasks. — [NCCE Quick Read](https://media.teachcomputing.org/QR_12_Block_model_8956b6555c.pdf)
- Code review surfaces "creation of alternative solutions to problems" as an actual outcome. — [Bacchelli & Bird 2013](https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/)
- Code Reading Club's "why" exercise asks for decisions, assumptions, drawbacks, and "viable
  alternatives". — [neontribe exercises.md](https://github.com/neontribe/code-reading-club/blob/trunk/exercises.md)
- A 2025 FSE paper studies students' comparative-comprehension barriers during code review of
  simplified versions. — [ACM DL 10.1145/3696630.3727249](https://dl.acm.org/doi/10.1145/3696630.3727249) (not read)
- **Evidence:** a CS2 quasi-experiment, N = 241 (Patitsas et al. 2013). The effect-size numbers
  were not retrieved.

### Inferences
**Mentor steps (applied design):**
1. Hold the problem constant and show A (the repo's verified version) and B (a plausible
   alternative) side by side, with the diff kept minimal.
2. Ask for a *behavioral* prediction on a named scenario: "Where do A and B diverge on input X?"
3. Ask for the *forces*: "Which production concern favors A? Which would favor B?" Require
   admissible arguments (the repo's Principle 2), not "it's simpler".
4. Run both if the difference is observable (the mentor keeps B in a scratch copy).
5. The learner states the principle in one sentence. Then link the ADR or convention that
   records it.

**Worked contrasts on the RAG graph:**
- *Retry scope.* A: `retry_policy=TRANSIENT_RETRY` on `retrieve` and `web_search` only.
  B: the same policy on every node. Scenario: a transient failure during `generate`. B stacks a
  node retry on top of the model SDK's retries and the model fallback, multiplying calls. A
  follows AGENTS.md convention 11 ("one retry layer per call").
- *Where the loop lives.* A: `retries` in graph state with a `query_rewrite → retrieve` edge.
  B: a `for` loop inside one `retrieve_and_grade` node. Scenario: the process crashes on
  attempt 2, or you want to replay attempt 2. A's attempts are separate checkpoints. B hides
  them in one step and puts two external dependencies in one node, so a node retry would re-run
  the model call.
- *Reducer choice.* A: `documents` overwritten per round. B: an accumulating reducer. Scenario:
  round 2 retrieves different documents. B lets irrelevant round-1 documents leak into
  `generate`'s context, or requires dedup logic.
- *Before/after from real history:* when an engineer's commit changed a component, show the
  diff and ask "what failure or review comment motivated this?" before revealing the commit
  message.

**Helps / backfires:**
- Helps: this is the most expert-appropriate format. It exercises design judgment, uses the
  learner's prior experience as an asset, and the "what if X changed?" question falls out
  naturally.
- Backfires: straw-man alternatives (an obviously bad B) teach nothing. B must be something a
  competent engineer might write. Too many simultaneous differences blur which change causes
  which behavior: keep to one variable per contrast.

### Gaps
- Effect sizes and the exact contrast design (simultaneous vs sequential) in Patitsas et al. were
  not retrieved.
- No study found on design-alternative contrasts with professionals.

---

## 8. Designing multiple-choice and one-line prediction questions (distractors from real misconceptions)

### Takeaway
Good code-behavior questions are fixed-code prediction items whose wrong options each encode a
specific, real misconception (off-by-one boundaries, overwrite vs accumulate, where state lives).
Aim for items that a meaningful share of learners get wrong. Require a committed answer and a
one-line reason, then run the code to settle it.

### Cited Findings
- "One of the most challenging aspects of writing a multiple-choice test is writing the
  distracters." A good distracter should be "plausible enough to appeal to some students" yet
  "clearly incorrect" for those who know the material. — [Lister et al. 2004, ITiCSE WG](https://dl.acm.org/doi/10.1145/1041624.1041673)
- In Lister et al., the most popular distracter on a harder item contained an incorrect loop
  termination (`j < x.length-1`): an off-by-one boundary misconception. "Fixed-code" questions
  (hand-execute and select the outcome) were generally easier than "skeleton-code" questions
  (select the correct completion). The study covered 941 students from 7 countries, 12 MCQs,
  and 556 students given all 12. — [Lister et al. 2004](https://dl.acm.org/doi/10.1145/1041624.1041673)
- Peer Instruction questions use "carefully chosen distractors to elicit misconceptions". An
  effective item has roughly half the class choosing correctly, with the rest drawn to one or
  two wrong answers. — [Pitt DBSERC: Clickers and Peer Instruction](https://www.dbserc.pitt.edu/resources/discipline-based-educational-strategies/clickers-and-peer-instruction); [Zingaro, PI in CS](https://www.danielzingaro.com/pics.php)
- Zingaro & Porter (2014) observed larger learning gains when an instructor explanation followed
  the discussion. Porter et al. (2011) used isomorphic follow-up questions to show learning from
  peer discussion. — [Frontiers in Education 2018 review](https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2018.00033/full); [Zingaro & Porter, *Computers & Education*](https://www.sciencedirect.com/science/article/abs/pii/S0360131513002777)
- **Evidence:** a multinational descriptive study (Lister 2004). The PI effects come from CS1
  classroom studies (Porter, Zingaro, Simon), cited via secondary sources.

### Inferences
**Mentor steps (applied design):**
1. Pick one behavior with a single checkable answer (a count, a path, a final value).
2. Write one distractor per real misconception you expect *for this framework*, not generic
   ones. Common graph-code misconceptions to mine: `<` vs `<=` budgets; reading a counter before
   vs after its increment; returned partial updates overwrite vs append; state persists across
   questions on a thread; node retries re-run model calls; a router runs as a node.
3. The learner answers with a letter, a confidence of 1-3, and a one-line reason. The reason
   shows *which* misconception drove a wrong pick.
4. Run the code. If wrong, explain against the specific distractor chosen, then ask an
   *isomorphic* follow-up (same idea, different surface) to confirm the fix.
5. Prefer fixed-code (predict the outcome) for runtime semantics. Use skeleton-code (choose the
   completion) for design intent ("which line makes this retry bounded?").

**Worked example (MCQ on the RAG loop):**
> An off-corpus question; grading keeps nothing each round; `MAX_RETRIES = 2`. Ignoring
> transient retries, how many times does `retrieve_node` run before `web_search`?
> A) 2 (*misconception: MAX_RETRIES = total attempts*)
> B) 3 ✔
> C) 4 (*misconception: the budget is inclusive, `<=`, or retries is read after the increment*)
> D) It loops until documents are found (*misconception: `retries` is local or isn't persisted in state*)

Isomorphic follow-up: "Same thread, second off-corpus question, the caller does not reset
`retries`. How many retrieves?" (1: the router sees `retries == 2` and goes straight to web.)

One-line prediction variant (no options, when distractors would leak the answer): "What does
`generate` receive as `documents` after two grading rounds?"

**Helps / backfires:**
- Helps: it's fast, and it diagnoses *which* wrong model the learner holds. For an expert, the
  distractors should target framework semantics where general experience actively misleads.
- Backfires: gotcha items (trick syntax, trivia) erode trust and test attention, not
  understanding. Items an expert answers instantly waste turns. Too many MCQs make a walkthrough
  feel like an exam, so use one or two per component.

### Gaps
- No verified catalog of LangGraph/agent-framework misconceptions exists in the literature I
  found. The mentor would need to build one from observed learner errors.
- The primary PI papers (Porter et al. 2011; Zingaro & Porter 2014) were cited via secondary
  sources, not read.

---

## 9. Code review as a teaching format

### Takeaway
In industry, code review's actual outcomes lean toward understanding and knowledge transfer
rather than defect finding (Microsoft), and "education" is one of four core expectations at
Google. For an experienced learner, reviewing a verified diff as if it were a PR, with
understanding-focused prompts, is a natural and authentic reading format. Peer-review studies in
education flag reviewer inexperience as the main challenge, so give structure.

### Cited Findings
- Microsoft study: finding defects is the main stated motivation, but reviews are "less about
  defects than expected" and yield knowledge transfer, team awareness, and alternative solutions.
  "Code and change understanding" is the key aspect of reviewing, and developers use many
  mechanisms to meet their understanding needs, mostly unmet by tools. — [Bacchelli & Bird 2013, ICSE](https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/)
- **Evidence (Microsoft):** surveys of 165 managers and 873 programmers, 17 interviews across 16
  teams, and 570 review comments manually classified. — [Bacchelli & Bird 2013 PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/ICSE202013-codereview.pdf)
- Google study: code review was originally introduced for understandability and maintainability,
  with an "initial educational motivation". Four expectation themes: **education** ("either
  teaching or learning from a code review"), maintaining norms, gatekeeping, and accident
  prevention. The paper corroborates "the importance of code review as an educational tool". —
  [Sadowski et al. 2018, ICSE-SEIP](https://sback.it/publications/icse2018seip.pdf)
- **Evidence (Google):** 12 interviews, a survey of 44, and logs of 9 million reviewed changes. —
  [Sadowski et al. 2018](https://research.google/pubs/modern-code-review-a-case-study-at-google/)
- In higher education, peer code review "offers potential benefits to both code reviewers and
  code authors", but participants are "typically less experienced, which presents a number of
  challenges". — [Indriasari, Luxton-Reilly & Denny 2020, *TOCE* 20(3)](https://dl.acm.org/doi/abs/10.1145/3403935)
- A follow-up applied gamification to improve student peer code review. — [Indriasari et al. 2021, ACE](https://dl.acm.org/doi/10.1145/3441636.3442308)
- Work on the "upper bound of information diffusion in code review" and on "knowledge transfer in
  modern code review" (ICPC 2020) exists. — [arXiv 2306.08980](https://arxiv.org/pdf/2306.08980); [Caulo et al., ResearchGate](https://www.researchgate.net/publication/342833663_Knowledge_Transfer_in_Modern_Code_Review) (neither read)

### Inferences
**Mentor steps (applied design, "review the verified PR"):**
1. *Intent first.* Show the change's purpose (a directive, issue, or ADR line) *before* the diff.
   The learner states what a correct change must do, in 2-3 bullets. These become the review
   criteria.
2. *Read the tests first* (or alongside). "Which behavior do these tests pin? What's untested?"
3. *Review with prompts, not a free-form hunt.* Give three lenses:
   - Correctness under failure: what happens on timeout, empty results, or a retry?
   - Design and conventions: which AGENTS.md convention does each choice follow?
   - Production path: what breaks at multi-tenant scale or on thread reuse?
4. The learner writes 2-4 review comments in the reviewer's voice (question, suggestion, or
   approval with reason). The learner writes review prose, not code.
5. *Reconcile with the engineer's rationale* (commit message, design card, the engineer's notice
   to the mentor). Each learner comment is classified as confirmed concern, answered by the
   design, or a real finding. Real findings go to the engineer as a request (per the repo
   protocol).
6. Optionally, a *seeded variant*: a copy with one realistic defect (for example `<=` in the
   router, or a missing `retries` reset), clearly labeled as an exercise and never presented as
   the verified code.

**Worked example (reviewing the RAG graph as a PR):**
- Intent: "Bounded self-correction: rewrite at most `MAX_RETRIES` times, then fall back to the
  web; retry only transient external calls."
- Expected learner comments: "`retries` is scratch state with no reducer. Who resets it when a
  thread is reused?" (answered by the design: the `RAGState` docstring puts that duty on the
  caller; follow-up: is it enforced or tested?). "Is there a test that the router goes to
  `web_search` at exactly `retries == MAX_RETRIES`?" "Should `check_hallucination`'s model call
  have a node retry?" (No: convention 11.)

**Helps / backfires:**
- Helps: this is the most authentic format for an experienced developer. It's the professional
  setting where learning from others' code already happens (Bacchelli & Bird; Sadowski et al.),
  it makes "why this design?" the natural question, and it trains a production skill.
- Backfires: unstructured review drifts into style nitpicks, the low-value mode. Reviewing
  verified code with no expected findings can feel like a staged exercise, so frame the goal as
  *understanding and challenging*, not bug-hunting. Seeded defects must be clearly separated
  from real code.

### Gaps
- I found no controlled study of learning outcomes from *reviewing* code (vs writing it) with
  experienced developers. The industry studies report perceived and observed knowledge transfer,
  not measured learning.
- The Indriasari 2020 review's detailed findings (which review designs worked) weren't read in
  full.

---

## 10. Expertise reversal: adapting all of the above to an experienced learner

### Takeaway
Guidance that helps novices (full worked examples, detailed explanations, line-by-line tracing)
can become redundant or harmful as expertise grows. The practical move is to diagnose quickly,
then fade. Use a rapid "first step" probe per component to decide how much scaffolding to give.

### Cited Findings
- Expertise reversal is "a reversal in the relative effectiveness of instructional methods as
  levels of learner knowledge in a domain change". It can be full (helps novices, hurts experts)
  or partial (helps novices, no effect for experts). — [Kalyuga 2007, *Educational Psychology Review*](https://link.springer.com/article/10.1007/s10648-007-9054-3); [Kalyuga & Renkl 2010, *Instructional Science* special issue](https://link.springer.com/article/10.1007/s11251-009-9102-0)
- For experienced learners, detailed guidance becomes redundant and must be reconciled with what
  they already know, which adds load. — [search summary of Kalyuga's work](https://www.researchgate.net/publication/225767816_Expertise_Reversal_Effect_and_Its_Implications_for_Learner-Tailored_Instruction)
- In training on programmable logic controllers, the worked-example advantage over problem
  solving disappeared as trainees gained experience. — [Kalyuga 2007 review](https://link.springer.com/article/10.1007/s10648-007-9054-3) (via search summary)
- The *rapid first-step diagnostic*: learners see a task briefly and indicate their first step
  toward a solution. Scores correlated significantly with traditional knowledge tests, and
  instruction adapted dynamically with such probes improved outcomes over non-adapted
  instruction. — [Kalyuga & Sweller, "Rapid dynamic assessment of expertise..." *ETR&D*](https://link.springer.com/article/10.1007/BF02504800); [Kalyuga 2006, *Applied Cognitive Psychology*](https://onlinelibrary.wiley.com/doi/abs/10.1002/acp.1249)
- A 2025 meta-analysis, "A cornerstone of adaptivity – A meta-analysis of the expertise reversal
  effect", exists (*Learning and Instruction*). — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0959475225000660) (paywalled; figures not retrieved)

### Inferences
**Mentor steps (applied design):**
1. *Probe first* (one turn): show the component for 30-60 seconds of reading, then ask a
   first-step question: "What's the first thing this graph does with an off-corpus question, and
   what decides the next step?" A fluent, purpose-level answer means the learner reads at the
   Relations/Macro level.
2. *Choose the scaffolding level from the probe:*
   - Fluent: skip labels and tracing. Go straight to the contrast (section 7), review (section 9),
     and "what if" questions.
   - Partial: one prediction plus a node-level trace table, then EiPE.
   - Weak on a new framework mechanism: subgoal labels (Stage A), a notional-machine sentence,
     and a full trace.
3. *Re-probe at each new mechanism.* Expertise is per mechanism, not per person: an expert in
   Python may be a novice in reducers or checkpoint semantics.
4. *Watch for redundancy signals:* instant correct answers, "yes, obviously". Then drop a level
   of guidance at once, without finishing the planned sequence.

**Suggested per-component sequence, combining the catalog (applied design):**
1. Rapid probe (section 10).
2. First glance and 5 important lines (section 4).
3. Predict, Run, Reconcile on one non-obvious scenario (sections 1, 6, and 8 for the question form).
4. 3-5 Block-Model questions weighted to Relations and Macro (section 2).
5. EiPE one-sentence purpose (section 3).
6. One design contrast (section 7), or a PR-style review (section 9).
7. A "what if" run by the mentor (Modify-in-mind, section 1).

Labels (section 5) and full traces (section 6) are inserted only when the probe shows a new
mechanism.

**Helps / backfires:**
- Helps: it keeps sessions at the learner's actual frontier, which respects experience and
  prevents boredom.
- Backfires: over-trusting general expertise. Experienced developers carry strong priors (a
  sequential call stack, mutation, "a retry is harmless") that the framework violates.
  Prediction items that target those priors are where scaffolding must *not* be dropped.

### Gaps
- No expertise-reversal study specific to code *reading* by professional developers found. The
  programming-adjacent evidence (PLC training) is dated.
- The 2025 meta-analysis's pooled effects and moderators were not accessible.
