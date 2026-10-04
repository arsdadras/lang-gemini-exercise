# Writing lessons in Persian

Every message to the learner from R0 topic 3 on is in Persian script. The learner asked for it
on 2026-10-04, which overrides the Finglish rule in
[principle 12](../../../library/governance/principles.md#12-communication); the lead records
the exception (MN-017). The learner reads this skill's result, not this file, so the file is
English and its examples are Persian.

This file is only about writing Persian. How to teach (examples first, one idea per message)
is in [SKILL.md](SKILL.md). Two things went wrong in the first Persian message, and each has a
rule below.

| What went wrong | Rule |
| :--- | :--- |
| English words scrambled the Persian sentence order | [1. Mark every Latin run](#1-mark-every-latin-run) |
| "Raise" and "call" were translated, so the text became hard to read | [2. Technical words stay English](#2-technical-words-stay-english) |

## 1. Mark every Latin run

**Why it scrambles.** Unicode (UAX #9) takes a paragraph's direction from its first strong
letter. A space or punctuation mark between a Persian and an English run takes the paragraph's
direction. So a line that starts with English becomes left-to-right, and the Persian words
inside it come out in the wrong order. Several English words in a row, separated only by
commas, also join into one left-to-right block that reads backwards.

**Checked on 2026-10-04** with a UAX #9 implementation (`python-bidi`), reading the displayed
order from the right:

| Logical text | Without marks | With every Latin run wrapped |
| :--- | :--- | :--- |
| `EvalCase یک مدل است و Decision خروجی آن.` (starts with English) | Left-to-right paragraph: the Persian words and both English terms are in the wrong order | Right-to-left paragraph; reads in logical order |
| `اجزا: eval_util، EvalCase و run_eval.` | The display shows `run_eval` before `EvalCase`, so the order is reversed | `eval_util`, `EvalCase`, `run_eval`, in logical order |

A line that already starts with a Persian word and has one English term in the middle was
fine either way. The wrap matters at the start of a line, and between two English terms.

**Seen in the Claude desktop app (learner's screenshots, 2026-10-04):** two paragraphs that
began with an English run (`EvalCase هیچ چیز...`, `path هم ساده است...`) were drawn scrambled,
although the run was wrapped. So the app does not skip the isolates when it picks a
paragraph's direction, and the wrap alone is not enough. Paragraphs that began with a Persian
word were fine.

**The rule.** Two measures, both needed:

- **Every paragraph starts with a Persian word.** This includes the position marker:
  `مرحله: <<R0 · Topic 3/4>> · نام قدم`. Rephrase instead of opening with a term:
  `در این کد <<EvalCase>> ...`, `فیلد <<path>> ...`. The helper also puts an invisible
  right-to-left mark (RLM, U+200F) at the start of each paragraph, and warns about a
  paragraph that starts with a Latin run.
- **Wrap every Latin run in `LRI` (U+2066) and `PDI` (U+2069).** These are invisible, and
  keep neighbouring English terms from merging into one block that reads backwards.

- A run is a phrase, not a word: `Topic 3/4` is one run. Identifiers, code spans, English
  terms, abbreviations, and numbers that touch English text are all runs.
- Do it with the helper, never by hand. Write the draft with `<<` and `>>` around each run:

  ```
  تابع <<run_eval>> هر <<case>> را به <<decider>> می‌دهد.
  ```

  then run `python .claude/skills/teach/fa_isolate.py draft.txt` and send its output. It
  checks the markers and warns about the problems in rules 1 and 2.
- A code span goes inside the markers: `<<`run_eval`>>`.
- A fenced code block holds English only. Persian goes outside it, never in its comments.
- Prefer paragraphs. A bullet or a table cell is fine only if it starts with a Persian word.
- No Persian suffix touches an English run (`decider‌ها`, `decider‌ی`): rephrase (`چند decider`,
  `برای decider`). A separate word such as `را` is fine.
- On Windows, Python prints Persian only with `PYTHONIOENCODING=utf-8`; without it the
  console raises `UnicodeEncodeError` (cp1252).
- **Not verified:** whether the RLM fixes a paragraph in the app; I cannot see it, only the
  learner's screenshots. If a paragraph is still drawn wrong, run the helper with `--rtl`,
  which wraps each paragraph in `RLI`..`PDI`, and record which version worked here.

## 2. Technical words stay English

A Persian reader who works with this code meets the English word in the code, the traceback,
and the docs. A translation (`بالا می‌آید` for "raises") sends the reader to guess what
English word hides behind it.

**Stays English:** names from the code; and the vocabulary the learner meets in code and
output: error, exception, raise, call, return, import, bug, test, case, label, probability,
dataset, report, timeout, retry, fallback, prompt, token, state, node, graph, agent, tool,
decider, harness, shadow, and so on. When the lesson points at something the learner saw in
code or output, it uses the English name seen there.

**Persian is the glue:** grammar, everyday words, and sentences that connect the terms.

**The pattern** is English verb plus a Persian light verb: `raise می‌شود`, `call می‌کنیم`,
`return می‌کند`, `retry می‌شود`, `import می‌کنیم`.

| Instead of | Write (draft markers) |
| :--- | :--- |
| اگر باگ باشد، خطا بالا می‌آید. | اگر <<bug>> باشد، <<exception>> <<raise>> می‌شود. |
| تابع را صدا می‌زنیم. | تابع را <<call>> می‌کنیم. |
| تصمیم‌گیرنده، برچسب، مجموعه‌داده | <<decider>>، <<label>>، <<dataset>> |
| خطای بیرونی مثل timeout | <<external error>> مثل <<timeout>> |

**A new term** appears once as the English word with a short Persian gloss, like
`decider` (چیزی که تصمیم می‌گیرد). After that it is English only.

## 3. Sentence style

- Short sentences, one idea each, about fifteen words at most. Avoid long chains of `ی`
  (ezafe): not `معماری لایه‌ی انتزاع تصمیم‌گیری`.
- Plain written Persian: `می‌شود`, not `میشه`, and not literary or ornate.
- Use the half-space (ZWNJ, U+200C) in `می‌`, `نمی‌`, and `‌ها`/`‌ای` endings.
- Persian punctuation: `،` `؛` `؟` and `«»`. Numbers are always written 0-9.

## Before sending a Persian message

1. The helper ran, and printed no warning that I cannot defend.
2. Every term that appears in the code is English, and no Persian suffix touches it.
3. Every paragraph starts with a Persian word; the helper warns when one does not.
4. The first line is the position marker, led by a Persian word:
   `مرحله: <<R0 · Topic 3/4>> · نام قدم`.

## Sources

[W3C: bidi basics](https://www.w3.org/International/articles/inline-bidi-markup/uba-basics),
[Unicode bidirectional algorithm](https://en.wikipedia.org/wiki/Unicode_bidirectional_algorithm),
and the 2026-10-04 test above. Rule 2 comes from the learner's own feedback on 2026-10-04.
