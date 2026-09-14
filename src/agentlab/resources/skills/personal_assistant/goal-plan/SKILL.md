---
name: goal-plan
description: Build and track a personal plan toward a goal that takes weeks - learning a skill, building or breaking a habit (such as quitting smoking), or a fitness routine - fitted to the user's stored constraints, with current guidance from the web and progress kept in memory across sessions.
---

# Goal Plan

## When to Use

The user wants a plan for a goal that takes weeks: learning a topic, starting or quitting a
habit, getting fitter, or a combination of these. Also when they report progress or a setback
on such a goal, or ask what to do next.

## Steps

1. **Recall.** Read `/memories/user_profile.md`, then `ls /memories/goals/` and read the
   goal's file if it exists. Continue an existing plan instead of starting over.
2. **Fill gaps.** Ask at most two short questions, and only for what memory does not
   already answer: the starting point, the target (what, and by when), and the weekly time
   or limits.
3. **Research.** Run 1-3 `web_search` calls for current, reputable guidance: official
   documentation and well-known courses for learning; health authorities for habits and
   fitness.
4. **Plan.** Split the target into 3-5 milestones sized to the user's constraints. Each
   milestone has an outcome, 2-4 concrete tasks, and a checkpoint that proves it. The first
   milestone must fit in one week. Combined goals (e.g. quit smoking while starting the gym)
   get one plan whose milestones cover both.
5. **Save.** Write `/memories/goals/<goal-slug>.md` (lowercase, hyphens), following the
   `memory-curation` skill. Asking for a tracked plan counts as asking you to remember the
   goal, health goals included. Memory holds only the skeleton: target, starting point,
   limits, one line per milestone, and the progress log. Tasks, resources, and explanations
   belong in your reply, not in memory; keep the file under about 20 lines.

   ```markdown
   # Goal: Quit smoking with a gym routine

   - Target: Smoke-free in 4 weeks, gym 3 days per week
   - Starting point: Smokes daily, no gym routine
   - Limits: Evenings only

   ## Milestones
   1. Log cigarettes and triggers, set a quit date - checkpoint: 7-day log
   2. ...

   ## Progress Log
   - Started the plan
   ```

   Add a one-line pointer under `## Goals` in the profile if it is not there yet.
6. **Reply.** Give the target, the milestones, and exactly what to do this week.

## Tracking Progress

The file is append-only on purpose, so everyday progress never needs approval:

- When the user reports progress or a setback, add a bullet to the end of `## Progress Log`
  (e.g. `- 3 days smoke-free, 2 gym sessions this week` or `- Smoked 2 cigarettes on day 5`).
  Do not edit milestone lines to mark them done; the log is the record.
- Recommend the next step from the first milestone the log does not show as finished. After
  a setback, adjust this week's steps in your reply; don't rewrite the plan.
- Changing the target or restructuring milestones edits existing lines, so it pauses for
  approval. Do it only when the user asks for a different plan.
