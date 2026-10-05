# ADR-0025: Two roles, the lead and the mentor

- Status: Superseded by [ADR-0028](0028-one-mentor-one-branch.md)
- Date: 2026-10-03
- Origin: user direction (2026-10-03: "only two roles, the mentor and the lead; the lead does
  everything else and has the authority to coordinate"); design by the lead. Supersedes
  [ADR-0022](0022-engineer-role-and-division-of-labor.md) (the engineer role) and amends
  [ADR-0018](0018-three-offices-library-and-archive.md) (offices) and
  [ADR-0019](0019-role-worktrees-hooks-and-handoff.md) (worktrees per role): four become two.
- Revisit when: the lead's building time delays a stage's readiness by more than one topic, or an
  escaped defect shows that the lead's self-review missed what an independent reviewer would
  have caught.

## Context

- **Four roles cost coordination.** Every change crossed three message hops (lead directive,
  engineer reply, lead review, mentor notice), each a file to write, a lint to pass, and a
  session to open. The first engineer session already hit a routing problem
  (`claude/jolly-satoshi-297451` couldn't move into `../lce-engineer`) and a CI failure that
  the lead's review then raced.
- **The user wants one planner and one teacher.** The mentor teaches; the lead prepares what is
  needed to teach and carries everything else.

## Decision

- **Two roles:**

  | Role | Job |
  | :--- | :--- |
  | Lead | Decides, plans, builds, tests, debugs, researches, reviews, runs git and GitHub; owns everything except the mentor's paths |
  | Mentor | Teaches the learner; reviews the code it teaches; writes study guides |

- **The engineer and research roles are retired.** Their offices move into `archive/offices/`.
  The research record (landscape, evidence, briefs, catalog) is live knowledge other records cite
  by ID; it moves into the lead's office as `mentor/research/`.
- **Ownership:** every path is the lead's except `offices/mentor/`, `docs/study_guides/`, and
  `.claude/skills/teach/` (the mentor's). The guard keeps reading the ownership map's Roles
  column; `ROLES` is `("lead", "mentor")`.
- **Messages:** two outboxes (`LD-###`, `MN-###`). Messages naming a retired role stay valid
  history; new ones can't address it.
- **Worktrees:** `../lce-lead` and `../lce-mentor`. The engineer and research worktrees and
  branches are removed; they held nothing `main` lacked.
- **The loss and its replacement:** the engineer's independent review of the lead's design, and
  the lead's of the engineer's code, no longer exist. Replacements: CI green before any merge;
  the lead reads its own diff once as a stranger; a `/code-review` pass for security-relevant or
  cross-cutting changes; and the mentor, who reads the core code with the learner, reports bugs
  it finds as requests.

## Consequences

- **Fewer hops and files.** A change is one body of work: plan, build, verify, merge, notice to
  the mentor.
- **The lead's sessions are longer and wider.** Hand off more often; keep one body of work per
  session.
- **Principle 1 still applies to the lead itself.** With no second role to object, the lead
  states objections to the user before implementing, and the user's override is recorded as
  always.
- **Closed or absorbed work:** open messages to the engineer and research are withdrawn; their
  content became lead work in [STATE.md](../../mentor/STATE.md) and
  [BACKLOG.md](../../mentor/BACKLOG.md).

## Alternatives considered

- **Keep the engineer, drop research only.** Rejected by the user's direction; it would also
  keep the biggest coordination cost (the build handoff).
- **Fold the lead into the mentor.** Rejected: teaching time and planning time would compete
  again, the reason for ADR-0016.
