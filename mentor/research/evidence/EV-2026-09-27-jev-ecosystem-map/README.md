# EV-2026-09-27-jev-ecosystem-map: What 551 cataloged Jev builds use it for

| | |
| :--- | :--- |
| Status | current |
| Label | **[V]** for the classification and its validation. The builds' own claims stay **[T]** |
| Ran | 2026-09-27, research office |
| Question | In the public catalog shipwithjev.com (551 builds, twelve days after launch), what role do Jev's decisions play? How many builds hook into coding agents, cascade to an LLM, or measure quality? |
| Cited by | [ecosystem](../../landscape/decision-models/ecosystem.md), [BR-003](../../briefs/BR-003-decision-points/README.md) |

## Setup

1. **Collect.** Every build page listed in the catalog's sitemap, downloaded on 2026-09-27 (551 of
   551), and parsed into:
   - title, category, type, source, and any reported cost and latency: kept as
     [`builds_meta.json`](artifacts/builds_meta.json);
   - the summary and the opening text: used, but not kept, since they are other people's words.

   Script: [`parse_builds.py`](artifacts/parse_builds.py).
2. **Classify with Jev.** One request per build, 551 in all, through OpenRouter (`typesafe/jev-1.13`). Each request
   asked:
   - one `choice` of twelve roles: action selection, safety gate, context management,
     verification, model or agent routing, triage, search and ranking, content scoring,
     extraction, analysis at scale, about Jev (SDKs, benchmarks, articles), and other;
   - three `noul`s: works with coding agents; combines Jev with an LLM (a cascade or a planner);
     reports a quality measurement against labels or a baseline.

   Script: [`classify_builds.py`](artifacts/classify_builds.py).
3. **Validate.** A seeded random sample of 40 builds, labeled by hand from title and summary
   before looking at Jev's labels ([`manual_labels.json`](artifacts/manual_labels.json)).

## Results

**The classifier:** 551 builds in 33 s, 684,211 input tokens, **$0.029**. On the 40-build
sample:

| Jev's confidence | Items | Agreement with the hand labels |
| :--- | :---: | :---: |
| any | 40 | 32 (80%) |
| ≥ 0.6 | 34 | 30 |
| ≥ 0.8 | 26 | 24 |
| ≥ 0.9 | 19 | **19** |

The median confidence was 0.955 where we agreed and 0.535 where we didn't. Several
disagreements are defensible either way, such as a feed curator as "content scoring" or as
"search and ranking".

**What the builds do**, from [`ecosystem_summary.txt`](artifacts/ecosystem_summary.txt):

| Role | Builds | Share |
| :--- | :---: | :---: |
| Action selection (browser and computer use, tool routing, game and robot moves) | 132 | 24.0% |
| About Jev (SDKs, integrations, benchmarks, articles) | 109 | 19.8% |
| Content scoring and moderation | 83 | 15.1% |
| Search and ranking | 51 | 9.3% |
| Triage | 41 | 7.4% |
| Verification (done checks, lint, PR and commit checks, evals) | 33 | 6.0% |
| Safety gate (tool-call and command gates, guardrails) | 27 | 4.9% |
| Model or agent routing | 25 | 4.5% |
| Other | 17 | 3.1% |
| Analysis at scale | 12 | 2.2% |
| Context management (skills, rules, memory, compaction) | 12 | 2.2% |
| Extraction | 9 | 1.6% |

- **Harness roles** are the five that sit around an agent's model: action selection, safety
  gate, context management, verification, and routing. They cover 229 builds, **41.6% of all
  builds, or 53.9% of the builds that use Jev** (excluding "about Jev" and "other").
- **Coding agents:** 130 builds (23.6%) hook into or serve Claude Code, Codex, Cursor, or
  OpenCode. Among them, most are action selection (24), verification (21), safety gates (20),
  routing (15), and context management (10).
- **Jev plus an LLM** (a cascade, fallback, or planner split): 135 builds (24.5%).
- **Quality measured against labels:** 37 builds (6.7%). The rest report speed, cost, or
  nothing.

## Reading

- **The main use is harness engineering, not document classification.** Half the builds that use
  Jev make the small decisions around an agent's model: the next action, whether a call may run,
  what enters the context, whether the work is really done, and which model or agent takes it.
- **Coding agents are a leading consumer.** One build in four serves them, mostly as hooks that
  gate, verify, or route. That is the development loop this repo's own sessions run in.
- **Evidence is thin.** Only one build in fifteen measures quality. Most claims are speed and
  cost.
- **The method works too.** Jev did this research task itself, for three cents, with its
  confidence marking the items worth a human look.

## Limits

- **One catalog, curated by one community site, twelve days after launch.** It is biased toward
  demos, launch-week enthusiasm, and what gets posted.
- **Roles overlap,** and each build got one. The hand sample shows the boundary cases.
- **Single hand labeler, sample of 40:** the agreement figure is indicative only.
- **The noul properties were not hand-validated.**

## Re-running

- Download the build pages listed in `https://www.shipwithjev.com/sitemap.xml` into `builds/`.
- Run `parse_builds.py`, then `classify_builds.py` (it needs `langchain-typesafe` and the
  OpenRouter key in the repo's `.env`, read by absolute path).
- The catalog grows daily, so a re-run measures a different population.
