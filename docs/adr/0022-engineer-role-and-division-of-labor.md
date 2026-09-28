# ADR-0022: An engineer role: building apart from teaching, research, and review

- Status: Accepted; step 4 of the flow amended by [ADR-0023](0023-active-review-instead-of-typing.md)
  (the learner reviews the verified code instead of typing it)
- Date: 2026-09-28
- Origin: user direction (2026-09-28); design by the lead. Amends
  [ADR-0018](0018-three-offices-library-and-archive.md) (three offices become four) and
  [ADR-0019](0019-role-worktrees-hooks-and-handoff.md) (a fourth worktree).
- Revisit when: the handoff between the engineer and the mentor delays a stage by more than one
  topic, or the mentor can't teach code it didn't build.

## Context

- **The mentor taught and built.** It verified each component, integrated code and tests, and
  paid down debt, so building time competed with teaching time. Several times the learner
  skipped typing or a demo and the mentor integrated instead.
- **The Jev program adds infrastructure** (the decision seam and log, the eval harness, the field
  compiler, the workbench) that must be built to production standard ahead of the lessons.
- **Research wrote spike code and harness-level measurements.** The user wants it on
  investigation, analysis, and strategy, delivering the big picture.
- **The lead decided and also built repo tooling.** The user wants it on management,
  coordination, reviews, and judgments.

## Decision

- **Four roles:**

  | Role | Job |
  | :--- | :--- |
  | Lead | Decides, coordinates, reviews, and runs git and GitHub |
  | Engineer | Implements, tests, debugs, and verifies: the product and the repo tooling |
  | Mentor | Teaches; reviews the code it teaches and asks the engineer for changes |
  | Research | Investigates, analyzes, and advises; brings the user the big picture |

- **The engineer** owns `src/`, `tests/`, `evals/`, `examples/`, `scripts/`, `.github/`,
  `.claude/settings.json`, `pyproject.toml`, and `uv.lock` (dependency changes follow the lead's
  radar). It works in `../lce-engineer` on branch `engineer`, and its messages are `EN-###`.
- **The flow of a change:**
  1. The lead decides (an ADR, a design card, a directive) and makes the stage ready.
  2. The engineer builds and verifies it in lesson-sized commits, and opens a pull request.
  3. The lead reviews and merges; the engineer tells the mentor what is ready to teach.
  4. The mentor reviews it and teaches it: the learner types the core code in the mentor's
     worktree, and the verified version is restored with git, never committed from there.
- **Definition of Ready gains one line:** the stage's verified reference implementation is
  merged, or the engineer is at least one topic ahead of the lesson.
- **Research's measurements that need repo code** or harness changes go to the engineer as
  requests. Research keeps its evidence and its analysis.
- **Reports to the user open with the bottom line** (DEC-027, principles 12).

## Consequences

- The ownership guard enforces the split: the mentor and the lead can no longer edit code or
  tooling. Each directs changes by message and reviews them in pull requests.
- The live code issues move from the mentor's state to the engineer's.
- There are four sessions to run and more messages; the lead's directives pair each build with
  its lesson.
- R0's remaining implementation (LD-006, LD-008, LD-016) is reissued to the engineer; the mentor
  teaches it once it is merged.

## Alternatives considered

- **The mentor keeps building:** rejected by the user; it takes time from teaching.
- **The lead builds:** rejected. The reviewer should not review its own code, and the lead's
  time goes to coordination and review.
- **Code shared by the engineer and the mentor:** rejected, since every path has one writer. The
  mentor prepares exercise states with git and never commits them.
