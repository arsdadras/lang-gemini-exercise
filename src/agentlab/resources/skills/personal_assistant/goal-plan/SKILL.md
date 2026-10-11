---
name: goal-plan
description: Build and track a personal plan toward a goal that takes weeks - learning a skill, building or breaking a habit (such as quitting smoking), or a fitness routine - fitted to the user's stored constraints, with current guidance from the web; the plan and its progress are kept in memory across sessions.
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
5. **Reply.** Give the target, the milestones, and exactly what to do this week. Don't write
   any file: memory is read-only for you. When the conversation ends, the app stores the
   plan's skeleton (target, starting point, limits, one line per milestone, and a progress
   log) in `/memories/goals/<goal-slug>.md` after the user approves it.

## Tracking Progress

- When the user reports progress or a setback, acknowledge it; the app adds it to the goal's
  `## Progress Log` after the conversation.
- Recommend the next step from the first milestone the log does not show as finished. After
  a setback, adjust this week's steps in your reply; don't restart the plan.
- If the user wants a different plan, give it in your reply; the app proposes the change to
  the goal file when the conversation ends.
