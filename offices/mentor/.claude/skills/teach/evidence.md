# Evidence

Why each technique in this skill is here. **Strength:** **MA** meta-analysis or systematic
review, **RCT** randomized trial, **QE** quasi-experimental, lab, or field study, **Q**
qualitative study (interviews, surveys, logs), **Review** narrative review, **Framework** a
design framework with no trial, **P** practitioner consensus, vendor guidance, or a benchmark;
"preprint" marks work not yet peer reviewed. **Population** is who was measured; "—" means the
notes don't record it. Nearly every row measured students or novices and none an experienced
developer learning by reviewing verified code, so every row is indirect for this learner, and
guidance that helps novices can reverse with expertise.

Rows compiled 2026-09-28: every DOI checked against Crossref. Rows marked † were added or
changed on 2026-09-29 from the mentor's
[teaching-research notes](../../../artifacts/teaching-research/synthesis.md): only their DOI
links were matched to Crossref titles; their claims, labels, and other links are not yet
checked and join research's audit, [MN-012](../../../OUTBOX.md).

## Learning

| Technique in the skill | Finding | Population | Strength | Source |
| :--- | :--- | :--- | :--- | :--- |
| Prediction before a demo or the code | Students who predicted a demo's outcome learned more from it than those who only watched | Physics undergraduates | QE | [Crouch et al. 2004](https://mazur.harvard.edu/publications/classroom-demonstrations-learning-tools-or-entertainment) |
| Demo, not typing † | Live coding taught about as well as static code examples; no large effect either way | Intro-course students, four lecture sections | QE, novices | [Rubin 2013](https://www.semanticscholar.org/paper/The-effectiveness-of-live-coding-to-teach-Rubin/8994b3dbf011725aa9a8b8e31a0d2565a9b33920) |
| Failure first (hook before theory) | Problem-solving before instruction beats instruction first on conceptual knowledge (g = 0.36, 53 studies) | 53 studies, over 12,000 participants | MA | [Sinha & Kapur 2021](https://journals.sagepub.com/doi/10.3102/00346543211019105) |
| Depth follows judgment, not routine; the probe † | Guidance that helps novices becomes redundant, even harmful, for more knowledgeable learners; a rapid first-step test tracked knowledge tests, and instruction adapted by it beat unadapted instruction. A 2025 meta-analysis exists and was not read | Reviews across domains; the rapid test outside programming | Review; QE | [Kalyuga et al. 2003](https://doi.org/10.1207/S15326985EP3801_4); [Kalyuga 2007](https://link.springer.com/article/10.1007/s10648-007-9054-3); [Kalyuga & Sweller 2005](https://link.springer.com/article/10.1007/BF02504800); [2025 meta-analysis](https://www.sciencedirect.com/science/article/pii/S0959475225000660) |
| "Why" and "what if" questions | Prompted self-explanation improves learning (g of about 0.55) | 64 reports, 69 effect sizes, about 6,000 participants | MA | [Bisra et al. 2018](https://doi.org/10.1007/s10648-018-9434-x) |
| Retrieval question at topic start | Practice testing and spaced practice rated highest utility among ten study techniques | — | Review | [Dunlosky et al. 2013](https://doi.org/10.1177/1529100612453266) |
| Spacing kept cheap (one or two questions) † | Spaced retrieval helped significantly in 2 of 9 courses, with small positive effects in 2 more | Nine introductory STEM courses | QE, mixed | [Bego et al. 2024](https://link.springer.com/article/10.1186/s40594-024-00468-5) |
| Questions after every component | Interactive and constructive engagement beats active and passive (ICAP) | — | Review | [Chi & Wylie 2014](https://doi.org/10.1080/00461520.2014.965823) |
| "Is the understanding real?" checks | People believe they understand mechanisms far better than they can explain them | — | QE | [Rozenblit & Keil 2002](https://doi.org/10.1207/s15516709cog2605_1) |
| Teach-back, announced early † | Preparing to teach g = 0.35, teaching after preparing g = 0.56; expecting to teach directly 0.50 vs 0.27 indirectly; explaining to others beats studying | 28 studies, students | MA | [Kobayashi 2019](https://onlinelibrary.wiley.com/doi/10.1111/jpr.12221); [Fiorella & Mayer 2014](https://doi.org/10.1016/j.cedpsych.2014.01.001) |
| Teach-back: the tutee probes † | Tutors default to telling knowledge; tutee questions move them to building it, where the deepest gains are | Peer tutors | Review | [Roscoe & Chi 2007](https://journals.sagepub.com/doi/abs/10.3102/0034654307309920) |
| Modeling, coaching, articulation, fading | Cognitive apprenticeship: make the expert's thinking visible, then fade support | — | Framework | [Collins, Brown & Newman 1989](https://www.researchgate.net/publication/232588395) |
| One idea per message, signposts | Segmenting, signaling, and coherence reduce extraneous load in explanations | — | Review | [Mayer, Multimedia Learning, 3rd ed. 2021](https://doi.org/10.1017/9781316941355) |
| Targeted feedback on answers † | Feedback helps most when it addresses the task and the process, not praise: high-information feedback d = 0.99, corrective only 0.46 | 435 studies, 994 effect sizes, over 61,000 participants | MA | [Wisniewski, Zierer & Hattie 2020](https://doi.org/10.3389/fpsyg.2019.03087) |
| Refutation † | Naming and refuting a misconception beats presenting the correct view, g = 0.41 over 44 comparisons | 3,869 participants, school and college | MA | [Schroeder & Kucera 2022](https://pubmed.ncbi.nlm.nih.gov/35095236/) |
| No self-level feedback † | 38% of feedback interventions lowered performance; effects fell as feedback moved from the task toward the self | 607 effect sizes, 23,663 observations | MA | [Kluger & DeNisi 1996](https://cris.huji.ac.il/en/publications/the-effects-of-feedback-interventions-on-performance-a-historical/) |
| One question at a time, wait for answers | Step-based tutoring comes close to human tutoring in effect | — | MA | [VanLehn 2011](https://doi.org/10.1080/00461520.2011.611369) |

## Code reading and design judgment

| Technique in the skill | Finding | Population | Strength | Source |
| :--- | :--- | :--- | :--- | :--- |
| Predict, run, investigate | PRIMM (reading and predicting before modifying and writing) improved programming attainment | 493 pupils aged 11-14, 13 schools | QE, novices | [Sentance, Waite & Kallia 2019](https://doi.org/10.1080/08993408.2019.1608781) |
| Chunks labeled by purpose † | Subgoal labels in worked examples improve problem solving and transfer; whether given or learner-made labels work better (Morrison et al. 2015) is unverified | Novice programmers | QE, novices | [Margulieux, Guzdial & Catrambone 2012](https://doi.org/10.1145/2361276.2361291) |
| Purpose check † | Explaining code's purpose in plain English correlates with writing code, r = 0.555 | Intro and data-structures students (10,024 answers) | QE, novices | [Chen et al. 2020](https://zilles.cs.illinois.edu/papers/EiPE_rubric_sigcse_2020.pdf) |
| Trace table † | A 5-10 minute tracing strategy with an external memory table scored about 15% higher | 24 intro-course students | RCT, small | [Xie, Nelson & Ko 2018](https://www.benjixie.com/publication/sigcse-2018/) |
| Contrasting options in architecture steps | Comparing contrasting cases prepares learners to understand the explanation that follows | College students, three classroom studies | QE | [Schwartz & Bransford 1998](https://doi.org/10.1207/s1532690xci1604_4) |
| Design contrast † | Comparing and contrasting solutions increased learning, replicating the result from mathematics | 241 second-year CS students | QE | [Patitsas, Craig & Easterbrook 2013](https://dl.acm.org/doi/10.1145/2493394.2493409) |
| Rank and reveal † | Matches with expert rankings improved 28% over a no-feedback group, and 21% in a second evaluation; the measure is agreement with experts, not field performance | Marines (59), soldiers (30) | QE, other domain | [Klein & Borders 2016](https://journals.sagepub.com/doi/abs/10.1177/1555343416636515) |
| Surfacing expert rationale † | Training built on cognitive task analysis of experts: g = 0.871 | Few studies, mostly medical | MA, other domain | [Tofel-Grehl & Feldon 2013](https://journals.sagepub.com/doi/abs/10.1177/1555343412474821) |
| PR review † | Review yields knowledge transfer, team awareness, and alternative solutions more than found defects | Microsoft: 873 programmers and 165 managers surveyed, 570 comments classified | Q, professionals | [Bacchelli & Bird 2013](https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/) |
| PR review † | Education, teaching or learning through review, is one of four core expectations of review | Google: 12 interviews, 44 surveyed, logs of 9 million changes | Q, professionals | [Sadowski et al. 2018](https://sback.it/publications/icse2018seip.pdf) |
| First-read opener † | A fixed sequence of short reading exercises (first glance, important lines, the why); no outcome study found | Practitioner reading groups | P | [Code Reading Club](https://codereading.club/) |

## AI tutoring

| Technique in the skill | Finding | Population | Strength | Source |
| :--- | :--- | :--- | :--- | :--- |
| Teach from the verified answer; hints only on the target idea † | Unguided GPT-4 raised practice scores, then left students 17% lower once access ended, and answered wrongly 49% of the time; a tutor whose prompt carried the teacher's solution and common mistakes, and gave hints rather than answers, largely removed the harm | About 1,000 high-school math students | RCT | [Bastani et al. 2025, PNAS](https://doi.org/10.1073/pnas.2422633122) |
| Plumbing told; "just tell me" answered at once † | Half the students bypassed optional hint guardrails at least once; lower performers and late starters bypassed more | 885 intro-programming students | QE, preprint | [Kapoor et al. 2025](https://arxiv.org/abs/2504.11146) |
| Structured, pedagogically prompted tutor | An AI tutor built on active-learning principles produced larger gains than an in-class active-learning session, in less time | 194 Harvard physics students | RCT | [Kestin et al. 2025, Scientific Reports](https://doi.org/10.1038/s41598-025-97652-6) |
| Fix the expected answer first † | When the user states an answer, model accuracy moves up to about 15 points toward it, right or wrong | Models in a simulated tutoring setting | P, preprint | ["Check My Work?" 2025](https://arxiv.org/pdf/2506.10297) |
| Never agree to be agreeable | Assistant models tend to tell users what they want to hear, even when wrong | Assistant models, not learners | QE | [Sharma et al. 2023](https://arxiv.org/abs/2310.13548) |
| The learner does the thinking † | With AI help, developers learning a new library scored 50% vs 67%; those who used it to understand (conceptual questions, explanations after code) scored 65% or more | 52 mostly junior developers | RCT, preprint | [Shen & Tamkin 2026](https://www.anthropic.com/research/AI-assistance-coding-skills) |

## LLM systems

From the mentor's research notes of 2026-09-28 (sandbox), not yet re-checked against the
sources.

| Idea in the skill | Finding | Population | Strength | Source |
| :--- | :--- | :--- | :--- | :--- |
| Outputs vary at temperature 0 | 1,000 samples at temperature 0 gave 80 distinct outputs; the cause is batch-dependent numerics | One model, 1,000 samples | QE | [Thinking Machines Lab, 2025-09](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/) |
| pass^k vs pass@k | Agents succeeding on ~61% of single trials succeeded on all 8 trials only ~25% of the time | LLM agents, retail domain | QE | [Yao et al. 2024, tau-bench](https://arxiv.org/abs/2406.12045) |
| Read outputs before writing criteria | Criteria drift: grading outputs is what defines the criteria | — | Q | [Shankar et al. 2024, UIST](https://arxiv.org/abs/2404.12272) |
| Mini error analysis | Open coding, then axial coding, then counts, then binary checks aligned to a human | — | P | [Husain & Shankar, evals FAQ](https://hamel.dev/blog/posts/evals-faq/) |
| Prompts are programs | Developers struggle to form reliable mental models of how a model responds to a prompt | 20 developers, interviews | Q | [Liang et al. 2025, FSE](https://arxiv.org/abs/2409.12447) |
| Transcripts and outcomes, trials and graders | Read transcripts; judge the outcome state, not the agent's claim; start from 20 to 50 real failures | — | P | [Anthropic, Demystifying evals for AI agents, 2026-01](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) |
| Traces as documentation | When decisions move into the model, the trace becomes the record of behavior | — | P | [LangChain blog, 2026-01](https://blog.langchain.com/in-software-the-code-documents-the-app-in-ai-the-traces-do/) |
