# Evidence Ledger

Back to the [research office](../../../archive/offices/research/README.md). Every measurement, spike, benchmark, or live-run
result this repo has produced, one record each. The full list is in the
[catalog](../CATALOG.md#evidence).

## Rules

- **Immutable.** A record is written once. If a later run contradicts it, write a new record
  and mark the old one `superseded by EV-...` in the catalog. Never edit the numbers.
- **One ID, one folder:** `EV-<YYYY-MM-DD>-<slug>/README.md`, where the date is when the
  measurement ran, not when it was written up. If the date is unknown, use `undated` and say
  what is known in the record.
- **Raw data travels with the record** under `artifacts/`: scripts, inputs, outputs, exactly as
  run. A record without artifacts is labeled **[R]** (reconstructed from prose an earlier
  session wrote) and says where that prose lives.
- **Test mode for live runs** (Principle 5); the record states the tier and model that answered.

## Record template

Every `README.md` here uses these headings, so agents can read any record the same way:

```markdown
# EV-<date>-<slug>: <one-line title>

| | |
| :--- | :--- |
| Status | current / superseded by EV-... |
| Label | [V] verified here, with artifacts / [R] reconstructed |
| Ran | <date>, <who or which session, if known> |
| Question | <what it set out to learn> |
| Cited by | <files that rely on it> |

## Setup
## Results
## Reading
## Limits
## Re-running        (only when artifacts exist)
```
