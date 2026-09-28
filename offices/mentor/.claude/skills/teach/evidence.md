# Evidence

Why each technique in this skill is here. Strength: **MA** meta-analysis or systematic
review, **RCT** randomized trial, **QE** quasi-experimental or lab study, **Q** qualitative
study, **P** practitioner consensus or vendor guidance. "Novices" marks findings measured
mainly on beginners; for an advanced learner they are weaker, or reversed (expertise
reversal). Compiled 2026-09-28; every DOI checked against Crossref; research is asked to
audit the claims (see the mentor's outbox).

## Learning

| Technique in the skill | Finding | Strength | Source |
| :--- | :--- | :--- | :--- |
| Prediction before a demo or the code | Students who predicted a demo's outcome learned more from it than those who only watched | QE | [Crouch et al. 2004](https://mazur.harvard.edu/publications/classroom-demonstrations-learning-tools-or-entertainment) |
| Failure first (hook before theory) | Problem-solving before instruction beats instruction first on conceptual knowledge (g = 0.36, 53 studies) | MA | [Sinha & Kapur 2021](https://journals.sagepub.com/doi/10.3102/00346543211019105) |
| Predict, run, investigate | PRIMM (reading and predicting before modifying and writing) improved programming attainment | QE, novices | [Sentance, Waite & Kallia 2019](https://doi.org/10.1080/08993408.2019.1608781) |
| Chunks labeled by purpose | Subgoal labels in worked examples improve problem solving and transfer | QE, novices | [Margulieux, Guzdial & Catrambone 2012](https://doi.org/10.1145/2361276.2361291) |
| Depth follows judgment, not routine | Guidance that helps novices becomes redundant, even harmful, for experienced learners | MA-level review | [Kalyuga et al. 2003](https://doi.org/10.1207/S15326985EP3801_4) |
| "Why" and "what if" questions | Prompted self-explanation improves learning (g of about 0.55) | MA | [Bisra et al. 2018](https://doi.org/10.1007/s10648-018-9434-x) |
| Contrasting options in architecture steps | Comparing contrasting cases prepares learners to understand the explanation that follows | QE | [Schwartz & Bransford 1998](https://doi.org/10.1207/s1532690xci1604_4) |
| Retrieval question at topic start | Practice testing and spaced practice rated highest utility among ten study techniques | MA-level review | [Dunlosky et al. 2013](https://doi.org/10.1177/1529100612453266) |
| Questions after every component | Interactive and constructive engagement beats active and passive (ICAP) | Review | [Chi & Wylie 2014](https://doi.org/10.1080/00461520.2014.965823) |
| "Is the understanding real?" checks | People believe they understand mechanisms far better than they can explain them | QE | [Rozenblit & Keil 2002](https://doi.org/10.1207/s15516709cog2605_1) |
| Teach-back | Explaining to others (preparing to teach and teaching) improves learning beyond studying | QE | [Fiorella & Mayer 2014](https://doi.org/10.1016/j.cedpsych.2014.01.001) |
| Modeling, coaching, articulation, fading | Cognitive apprenticeship: make the expert's thinking visible, then fade support | Framework | [Collins, Brown & Newman 1989](https://www.researchgate.net/publication/232588395) |
| One idea per message, signposts | Segmenting, signaling, and coherence reduce extraneous load in explanations | MA-level review | [Mayer, Multimedia Learning, 3rd ed. 2021](https://doi.org/10.1017/9781316941355) |
| Targeted feedback on answers | Feedback helps most when it addresses the task and the process, not praise | MA | [Wisniewski, Zierer & Hattie 2020](https://doi.org/10.3389/fpsyg.2019.03087) |
| One question at a time, wait for answers | Step-based tutoring comes close to human tutoring in effect | MA | [VanLehn 2011](https://doi.org/10.1080/00461520.2011.611369) |

## AI tutoring

| Technique in the skill | Finding | Strength | Source |
| :--- | :--- | :--- | :--- |
| Hints before answers | Unrestricted GPT-4 raised practice scores but lowered later exam scores; a tutor version that gave hints, not answers, largely removed the harm | RCT | [Bastani et al. 2025, PNAS](https://doi.org/10.1073/pnas.2422633122) |
| Structured, pedagogically prompted tutor | An AI tutor built on active-learning principles produced larger gains than an in-class active-learning session, in less time | RCT | [Kestin et al. 2025, Scientific Reports](https://doi.org/10.1038/s41598-025-97652-6) |
| Never agree to be agreeable | Assistant models tend to tell users what they want to hear, even when wrong | QE | [Sharma et al. 2023](https://arxiv.org/abs/2310.13548) |

## LLM systems

From research's notes of 2026-09-28 (sandbox copy), not yet re-checked by the mentor.

| Idea in the skill | Finding | Strength | Source |
| :--- | :--- | :--- | :--- |
| Outputs vary at temperature 0 | 1,000 samples at temperature 0 gave 80 distinct outputs; the cause is batch-dependent numerics | QE | [Thinking Machines Lab, 2025-09](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/) |
| pass^k vs pass@k | Agents succeeding on ~61% of single trials succeeded on all 8 trials only ~25% of the time | QE | [Yao et al. 2024, tau-bench](https://arxiv.org/abs/2406.12045) |
| Read outputs before writing criteria | Criteria drift: grading outputs is what defines the criteria | Q | [Shankar et al. 2024, UIST](https://arxiv.org/abs/2404.12272) |
| Mini error analysis | Open coding, then axial coding, then counts, then binary checks aligned to a human | P | [Husain & Shankar, evals FAQ](https://hamel.dev/blog/posts/evals-faq/) |
| Prompts are programs | Developers struggle to form reliable mental models of how a model responds to a prompt | Q | [Liang et al. 2025, FSE](https://arxiv.org/abs/2409.12447) |
| Transcripts and outcomes, trials and graders | Read transcripts; judge the outcome state, not the agent's claim; start from 20 to 50 real failures | P | [Anthropic, Demystifying evals for AI agents, 2026-01](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) |
| Traces as documentation | When decisions move into the model, the trace becomes the record of behavior | P | [LangChain blog, 2026-01](https://blog.langchain.com/in-software-the-code-documents-the-app-in-ai-the-traces-do/) |
