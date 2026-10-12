# Writing lessons and messages in Persian

Every message to the learner in Persian script follows this file ([principle 12](../../../library/governance/principles.md#12-communication), DEC-034). The learner reads this skill's result, not this file, so the file is English and its examples are Persian.

This file is only about writing Persian. How to teach (examples first, one idea per message)
is in [SKILL.md](SKILL.md).

| What went wrong | Rule |
| :--- | :--- |
| English words or markdown bullets scrambled the Persian sentence order | [1. Mark every Latin run and start every paragraph with RLM + Persian](#1-mark-every-latin-run) |
| "Raise" and "call" were translated, so the text became hard to read | [2. Technical words stay English](#2-technical-words-stay-english) |

## 1. Mark every Latin run

**Why it scrambles.** Unicode (UAX #9) takes a paragraph's direction from its first strong
letter, and the Antigravity / Claude desktop chat containers render `<p>`, `<li>`, and `<h3>`
in an LTR CSS layout. A space or punctuation mark between a Persian and an English run takes
the paragraph's direction. So a line that starts with English, or starts with a markdown bullet
(`- `, `* `) or numbered prefix (`1. `), or contains multiple unwrapped English words/code
spans, scrambles the visual word order.

**Checked on 2026-10-04 and 2026-10-11:**

| Logical text | Without marks | With every Latin run wrapped and RLM paragraph start |
| :--- | :--- | :--- |
| `EvalCase یک مدل است و Decision خروجی آن.` (starts with English) | Left-to-right paragraph: the Persian words and both English terms are in the wrong order | Rephrased to start with `RLM` + Persian (`مدل <<EvalCase>> ...`): reads in logical right-to-left order |
| `اجزا: eval_util، EvalCase و run_eval.` | The display shows `run_eval` before `EvalCase`, so the order is reversed | `eval_util`, `EvalCase`, `run_eval`, in logical order |

**The rule.** Four mandatory measures:

- **Every paragraph and heading starts with `RLM` (`U+200F`, `‏`) followed immediately by a Persian word, and ends with `RLM` (`‏`).** This includes the position marker:
  `‏مرحله: <<R2 · Topic 1/4>> · نام قدم‏`. Rephrase instead of opening with an English term:
  `‏در این کد <<EvalCase>> ...‏`, `‏فیلد <<path>> ...‏`.
- **Never use markdown bullet lists (`- `, `* `) or numbered lists (`1. `) in Persian prose.** Instead, write normal paragraphs that open with Persian ordinal phrases (`‏گام اول، ...‏`, `‏مورد اول، ...‏`).
- **Wrap every Latin run, code span, or markdown link in `RLM + LRI` (`U+200F` + `U+2066`, `‏⁦`) and `PDI + RLM` (`U+2069` + `U+200F`, `⁩‏`).** These invisible bidi isolates keep neighbouring English terms, inline code `` `...` ``, and links `[...](...)` from merging into an LTR block that reverses the sentence.
- A run is a phrase, not a word: `Topic 3/4` is one run. Identifiers, code spans, markdown links, English terms, abbreviations, and numbers that touch English text (`P1`, `R2`) are all runs.
- Use the helper script (`uv run python .agents/skills/teach/fa_isolate.py draft.txt`) or emit the exact `‏⁦...⁩‏` markers directly:

  ```
  تابع <<run_eval>> هر <<case>> را به <<decider>> می‌دهد.
  ```

- A code span or markdown link goes inside the isolate markers: ``<<`run_eval`>>`` or `<<[rag_workflow.py](file:///...)>>`.
- A fenced code block holds English only. Persian goes outside it, never in its comments.
- No Persian suffix touches an English run (`decider‌ها`, `decider‌ی`): rephrase (`چند decider`,
  `برای decider`) or insert a space after the closing isolate (`‏⁦Agent⁩‏های`).
- On Windows, Python prints Persian only with `PYTHONIOENCODING=utf-8`; without it the
  console raises `UnicodeEncodeError` (cp1252).

## 2. Technical words stay English

A Persian reader who works with this code meets the English word in the code, the traceback,
and the docs. A translation (`بالا می‌آید` for "raises") sends the reader to guess what
English word hides behind it.

**Stays English:** names from the code; and the vocabulary the learner meets in code and
output: error, exception, raise, call, return, import, bug, test, case, label, probability,
dataset, report, timeout, retry, fallback, prompt, token, state, node, graph, agent, workflow,
specialist, coordinator, tool, middleware, decider, harness, shadow, and so on. When the lesson
points at something the learner saw in code or output, it uses the English name seen there.

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
`decider` (مدلی که تصمیم می‌گیرد). After that it is English only.

## 3. Sentence style

- Short sentences, one idea each, about fifteen words at most. Avoid long chains of `ی`
  (ezafe): not `معماری لایه‌ی انتزاع تصمیم‌گیری`.
- Plain written Persian: `می‌شود`, not `میشه`, and not literary or ornate.
- Use the half-space (ZWNJ, U+200C) in `می‌`, `نمی‌`, and `‌ها`/`‌ای` endings.
- Persian punctuation: `،` `؛` `؟` and `«»`. Numbers are always written 0-9.

## Before sending a Persian message

1. Every paragraph and heading starts with `RLM` (`‏`) + a Persian word and ends with `RLM` (`‏`).
2. No markdown bullets (`- `, `* `) or numbered lists (`1. `) are used in Persian text.
3. Every English term, code span, or markdown link is wrapped in `‏⁦...⁩‏`, and no Persian suffix is glued directly without isolation.
4. The first line of a lesson message is the position marker, led by a Persian word:
   `‏مرحله: ⁦R2 · Topic 1/4⁩ · نام قدم‏`.

## Sources

[W3C: bidi basics](https://www.w3.org/International/articles/inline-bidi-markup/uba-basics),
[Unicode bidirectional algorithm](https://en.wikipedia.org/wiki/Unicode_bidirectional_algorithm),
and the 2026-10-04 and 2026-10-11 UI tests above.
