# What People Build with Jev

[Decision models](README.md) › ecosystem. As of **2026-09-27**, twelve days after launch.
Labels:

- **[V]** verified here;
- **[S]** primary source;
- **[T]** third-party and builder-reported. Most numbers below are this kind, unaudited;
- **[C]** vendor or partner claim.

The measured map of the public catalog is
[EV-2026-09-27-jev-ecosystem-map](../../evidence/EV-2026-09-27-jev-ecosystem-map/README.md).
What it means for this repo is in [BR-003](../../briefs/BR-003-decision-points/README.md).

## The shape of the ecosystem

Of 551 cataloged builds **[V]**:

- **Harness work dominates.** Of the builds that use Jev, 53.9% put it in the agent's harness:
  - picking the next action;
  - gating a call;
  - choosing what enters the context;
  - checking that work is done;
  - routing to a model or an agent.
- **Coding agents are a leading consumer.** One build in four serves Claude Code, Codex,
  Cursor, or OpenCode.
- **The LLM stays.** One build in four pairs Jev with an LLM, as a planner, a fallback, or the
  escalation.
- **Few measure quality:** only 6.7% report it against labels.

The frameworks moved in about ten days **[S]**. Among them:

- LangChain in Python and JavaScript;
- Pydantic AI, which derives Jev questions from Pydantic output types;
- LiteLLM, with complexity routing and a tool-result guardrail;
- Vercel's agent framework `eve`, with Jev as its default "evaluate" model;
- Composio, which shortlists tools, maps closed-set arguments, and gates destructive actions;
- BAML, TanStack AI, and Effect;
- Langfuse, where Jev is a native evaluator;
- LangSmith, with views for decision models;
- clients in Go, Rust, .NET, Swift, Elixir, R, Ruby, Laravel, and Spring Boot.

## By role, with the builds that show it best

Numbers are the builders' own **[T]** unless marked.

### Agents' harness (the development loop and the product loop)

| Role | Build | What it does | Reported |
| :--- | :--- | :--- | :--- |
| Verify "done" | jev-belay | A Claude Code Stop hook: if files changed and no check passed since, one four-question call asks whether "done, tests pass" is unverified; if so, the turn doesn't end | AUROC 0.976 on 100 labeled stops, against 0.777 on the wording alone; blocks 8 in 100, 7 rightly; 346 ms |
| Verify "done" | Canny | An evidence ledger of what the agent actually did; won't let it finish on a claim | n/a |
| Rule compliance | Abide | Per edit, one question per rule: does it break `AGENTS.md` or `CLAUDE.md`? | Replay of 93 Claude Code sessions (1,256 edits): 39 edits flagged, **10 confirmed**; 15 turns flagged, 11 confirmed; $0.22 |
| Gates | jev-gates | Nine gates for Claude Code: rules, scope, intent, prompt completeness, bash, done, claims, proof, commit honesty. **They escalate but never approve** | n/a |
| Gates | Bouncer, jev-firewall, jev-guard, the shell-command hook | Every tool call or shell command judged against a policy: allow, ask, or deny | about $0.04 a day (Bouncer) |
| Context | jev-rules | Picks which of your rules apply to the current prompt, so Claude sees only those | n/a |
| Context | fast-jev-compaction | Replaces summary compaction with keep, drop, or truncate decisions per tool call; everything kept stays verbatim | n/a |
| Context | jev-gc, jev-harness, FyleContext | Decide what stays in the next prompt; filter every tool result or retrieved passage before the model reads it | n/a |
| Memory | invalidate | Gives each remembered fact a lease; asks whether new evidence ends it | n/a |
| Memory | perfectrecall | Decides what is worth recalling | n/a |
| Skills | TypeSafe's skill-suggestion cookbook; jev-skill-router; skillranker | Rank and re-check a large skill roster before the agent loads one | 182 skills, 488 turns: wrong loads 16.8% → 7.3%, needless loads 9.8% → 4.0% **[C]** |
| Tool choice | jev-gateway, jev-tool-router, Composio | Jev picks the tool; an LLM fills in the arguments or writes the prose | WebMCP benchmark 49/49 at ~112x lower cost |
| Delegation | opencode-jev-orchestrator, agent-dispatcher | Difficulty judgments send harder turns to subagents; tasks go to 27 roles, with "done" evidence defined up front | n/a |
| Model routing | ModelRouterMiddleware; DeepSeek Harness router; pi-jev-router; Jev Router on OpenRouter | Choose model and reasoning effort per request | LiteLLM routing: 95% vs 74% for Haiku, on the authors' labels |
| Code search | Oko | Ranks code snippets for the agent through MCP | 13-44% fewer tokens, 33-61% fewer tool calls; MRR 0.39 vs 0.24 on a public benchmark |
| Waking | wakegate | Decides whether a timer or an event is worth waking a sleeping agent's LLM | n/a |
| Evals | LangSmith experiment; jevals; Langfuse evaluator | The same typed checks run on saved traces and as runtime guardrails | See below |

### Computer and browser use: action selection over a finite menu

- **Browserbase Stagehand.** Code lists the interactive elements; Jev picks the action type and
  the element. Below 0.7 confidence it falls back to an LLM. The median `act()` dropped from
  1.97 s to 0.46 s **[T]**.
- **Others:** Browser Use (a flight search in about 7 s for about $0.004), Jev Desktop, Hunch
  (153 ms per decision), and voice-controlled Macs **[T]**.
- **The pattern:** the next UI action is a choice from a finite list, so a decider can take it.

### Development workflow outside the agent loop

- **Semantic lint in plain English.** JevLint, perch, oxlint-plugin-jev, jev-lint, jev-pref,
  taste-lint, and slopch.
- **Commit and PR honesty.** jev-commit, JevPR, jev-auto-approve, and lorenzini.
- **Specs and APIs.** jev-spec checks generated code against its specification; jev-oas-sentinel
  checks OpenAPI changes.
- **Logs and alerts.** jev-logtriage; Tocsin (22.8M log lines for $0.64); triagedy.

### Business decisions at volume

- **Content and moderation:** 83 builds, the largest non-harness role.
- **Triage:** email, tickets, leads, and alerts.
- **Search, ranking, and semantic SQL:** JevQL for Postgres, duckdb-jev.
- **Examples [T]:** "500 emails for 3.5 cents", and "26,000 verdicts for 13 cents".

### Real-time control

Games and robots, 66 and 7 builds, show the latency. Doom at about 10 decisions a second,
Tetris, drones, and a robot arm in MuJoCo. The robot and drone builds share one rule: code owns
kinematics and physics, and Jev decides only at the branches.

### Teaching and learning

- **Confidence trivia.** The player answers with a probability, and the opponent is a model
  trained to be honest about uncertainty. It teaches calibration.
- **A Rubik's cube coach.** Code solves; the decider watches, stays quiet during progress, and
  steps in on mistakes or when the player is stuck. "Real-time Clippy", which wakes only when
  the user seems stuck, is the same idea.
- **The catalog site's grading essay.** Rubric verdict batteries for formative feedback, with
  misconception routing and item analysis. Summative marks stay human, with safeguards against
  fluency bias, nondeterminism, and gaming **[T]**.

## Evaluation uses (LLM-as-judge, replaced or supplemented)

- **LangSmith experiment** (LangChain, 2026-09-20) **[C]**. Five fixed agent traces, each judged
  100 times:
  - Jev agreed with the human labels 100% of the time, with the lowest variance: 92-913x lower
    than three LLM judges;
  - $0.34 for all 500 judgments, against $28.17 for Claude.

  The authors say the sample is too small to generalize.
- **Langfuse** **[T]**: Jev is a native evaluator. Good Start Labs graded 6,003 rubric checks,
  and Jev matched Claude Fable 5.1's verdict 91.5% of the time. Per million verdicts that is $160
  against $33,000.
- **TypeSafe's consistency cookbooks** **[C]**: the per-question probability's standard
  deviation was 0.0102 over 15 repeats, against visible run-to-run movement for LLM judges, even
  at temperature 0.

## Independent studies

Every one publishes its data, and most were pre-registered **[T]**.

| Study | Scope | Finding |
| :--- | :--- | :--- |
| jev-decision-benchmarks | MetaTool (995 + 995), When2Call (3,652), BFCL V4 | Tool selection 77.8% vs ChatGPT 69.1%; **abstention 87.0% vs 50.4%**; When2Call 74.8%; BFCL relevance 87.5%, irrelevance 86.7% |
| jev-eval (4esv) | 300 items per task | CLINC, 151-way: 0.897 (ECE 0.039). Banking77: 0.780, against GPT-5.6 Terra 0.847 and open-jev 0.873. SST-5: 0.570 vs 0.593. IMDB: 0.970, tied. Latency flat from 2 to 151 options |
| jev-evaluation (Will Kelly) | 123,805 requests; 28 pre-registered predictions, 12 held | Batching 200 questions matched single questions at nearly flat latency. Calibration held on ticket routing (ECE 0.075) and **failed off-distribution** (3-SAT). Position bias: named subjects 1.000, unnamed 0.420, decaying to 0.150. **Direct injection failed on 199/200 tickets; authority-claiming text succeeded on 147/200** |
| jev-acento | Spanish, 19,200 calls, pre-registered | −3.0 to −6.4 points against English state; ECE about doubled on harder tasks; coverage at 0.9 fell from 72.2% to 63.4%; keep instructions in English; 17-38% more tokens |
| Decomposition study (beri.net) | PhishNChips, 1,000 + 1,000 | One broad question: Jev 62.6%, against Haiku 81.3%. **Five atomic questions combined by logistic regression: Jev 95.0%, Haiku 93.2%, regex baseline 91.8%**; 12-27x cheaper. Out-of-distribution ECE 0.107; on unknowable questions, 44.7% right at a mean probability of 0.74 |
| jev-rerank-bench | 14 datasets | Jev as a reranker 0.692, against Cohere Rerank 4 Pro 0.691: no winner. Better than rerankers on negation; Open-Jev 9B better still (77% vs 71%) |
| jev-orderby-bench | 360 human-labeled rows, 6 pre-registered gates | Passes all six. Boolean inversion 0.036; score ordinal inversion 0.143, the weak link; underconfident in 8 of 10 bins |
| Jev vs. ML | 8 datasets, 11 classical pipelines | IMDb 96.3% vs 88.4%; classical pipelines lead on four tasks |
| jev-behavior-study | 11,621 requests, synthetic | Performance depends on exact framing; a right answer to a prerequisite doesn't guarantee a right decision |
| nibzard; AbdelStark; Context Studios | See [jev.md](jev.md#measurements) | Mid-pack on Banking77 (76.3%); worst ECE (0.246); about 25x faster like for like |

**What the evidence says, taken together:**

- **It is strong on bounded choices:**
  - tools;
  - actions over a finite menu;
  - abstaining when nothing fits;
  - routing;
  - ranking with a rubric.
- **It is decent on binary checks when they are well phrased.**
- **It is weaker on:**
  - many-class intent it wasn't asked to decompose;
  - implied conditions;
  - out-of-distribution reasoning;
  - languages other than English;
  - authority-claiming injection.
- **Decomposition is the lever.** The same model went from 62.6% to 95.0% on one task.
