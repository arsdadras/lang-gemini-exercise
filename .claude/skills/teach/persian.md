# Writing lessons in Persian

Every message to the learner from R0 topic 3 on is in Persian script. The learner asked for it
on 2026-10-04, which overrides the Finglish rule in
[principle 12](../../../library/governance/principles.md#12-communication); the lead records
the exception (MN-017). The learner reads this skill's result, not this file, so the file is
English and its examples are Persian.

Three things went wrong in the first Persian message. Each has a rule below.

| What went wrong | Rule |
| :--- | :--- |
| English words scrambled the Persian sentence order | [1. Mark every Latin run](#1-mark-every-latin-run) |
| "Raise" and "call" were translated, so the text became hard to read | [2. Technical words stay English](#2-technical-words-stay-english) |
| A concept came as prose only, and the learner could not follow it | [3. Every concept comes with an example](#3-every-concept-comes-with-an-example) |

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

**The rule.** Wrap every Latin run in `LRI` (U+2066) and `PDI` (U+2069). These are invisible,
and the paragraph-direction check skips what is inside them.

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
- **Not verified:** how the Claude desktop app draws these paragraphs; I cannot see it. If the
  learner still reports mixed-up order, run the helper with `--rtl`, which wraps each
  paragraph in `RLI`..`PDI`, and record which version worked here.

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

## 3. Every concept comes with an example

The learner learns from examples. An intro and a recap in prose are fine; a concept explained
in prose alone is not understood.

- Order: the example first (a real input and output, a run, a trace, or four lines of code),
  then at most three sentences that name the concept and its rule.
- A paragraph of more than four sentences with no example in the same message is a defect:
  replace the prose with an example.
- The example is code or output in a fenced block (English only), with the Persian around it.

## 4. Sentence style

- Short sentences, one idea each, about fifteen words at most. Avoid long chains of `ی`
  (ezafe): not `معماری لایه‌ی انتزاع تصمیم‌گیری`.
- Plain written Persian: `می‌شود`, not `میشه`, and not literary or ornate.
- Use the half-space (ZWNJ, U+200C) in `می‌`, `نمی‌`, and `‌ها`/`‌ای` endings.
- Persian punctuation: `،` `؛` `؟` and `«»`. Numbers are always written 0-9.

## Before sending a Persian message

1. The helper ran, and printed no warning that I cannot defend.
2. Every term that appears in the code is English, and no Persian suffix touches it.
3. Every concept has its example in this message.
4. Each paragraph starts with a Persian word where that reads naturally.
5. The first line is the position marker, with the English run wrapped:
   `<<R0 · Topic 3/4>> · نام قدم`.

## Sources

[W3C: bidi basics](https://www.w3.org/International/articles/inline-bidi-markup/uba-basics),
[Unicode bidirectional algorithm](https://en.wikipedia.org/wiki/Unicode_bidirectional_algorithm),
and the 2026-10-04 test above. The wording rules (2 and 3) come from the learner's own
feedback on 2026-10-04.
