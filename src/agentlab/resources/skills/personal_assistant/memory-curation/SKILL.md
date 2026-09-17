---
name: memory-curation
description: How to save, update, or remove long-term memories about the user under /memories/ - what is worth storing, how memory files are laid out, and how to change them so ordinary saves need no approval.
---

# Memory Curation

## When to Use

Read this before any `write_file`, `edit_file`, or `delete` under `/memories/`: the user
shared a durable fact, preference, constraint, or goal, or asked you to remember, correct,
or forget something.

## What Is Worth Storing

Store facts that will still matter in a future session:

- identity and background: name, occupation, languages;
- stable preferences: tools, formats, tone, schedules;
- recurring constraints: available time, budget, things to avoid;
- goals and ongoing projects, including learning progress;
- sensitive facts (health, finances, relationships) when they will shape future help, such as
  a condition that affects a training plan. Save them like any other fact and don't ask the
  user first: when a change needs approval, the app asks.

Facts about other people are worth storing only when they matter for the user's own goals.

Do not store:

- one-off requests, temporary states ("tired today"), or small talk;
- secrets of any kind: passwords, API keys, tokens, account numbers. Tell the user you don't
  keep them.

## Layout

The profile, `/memories/user_profile.md`, is loaded into every conversation. Keep it short:

```markdown
# User Profile

## Identity
- Name: Sam

## Preferences
- Prefers short answers with code examples

## Constraints
- About 3 hours per week for learning

## Goals
- Become a backend developer
```

- One fact per bullet, written in English. Proper names keep their original form.
- Write only facts you know. Leave a section empty rather than filling it with a placeholder
  such as "Name: the user".
- Larger topics get their own file, e.g. `/memories/goals/<goal>.md` (see the `goal-plan`
  skill). Only a one-line pointer goes in the profile.

## How to Change Memory

Every change has one of three outcomes: it is stored, it waits for the user's approval, or it
is refused. The app decides which. Shape your edits so ordinary saves are stored directly:

1. **Read first.** `read_file` the target file before editing. Never edit from what you
   remember it contains.
2. **Add by appending.** New file: `write_file`, only if it does not exist yet. Existing file:
   `edit_file` whose `new_string` keeps the `old_string` and adds after it, e.g. anchor on a
   heading:
   - `old_string`: `"## Goals\n"`
   - `new_string`: `"## Goals\n- Become a backend developer\n"`
3. **Change only when the user corrected or retracted a fact.** Make one precise `edit_file`
   on that bullet. Never rewrite an existing file with `write_file`.
4. **Batch.** Put everything worth saving from one turn into a single edit.
5. **Accept a rejection or refusal.** Never try to reach the same result another way: no
   rewording, splitting the fact, or using a different tool. A rejected fact stays out of
   memory for the rest of the conversation, so leave it out of later saves too, unless the
   user brings it up again. Follow the user's reason if they gave one; otherwise leave the
   memory as it is and continue the conversation.

## After Writing

Say something was saved only after the tool result confirms it. If a change was rejected or
refused, say plainly that it was not saved.
