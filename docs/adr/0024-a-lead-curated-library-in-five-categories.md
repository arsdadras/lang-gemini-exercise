# ADR-0024: A library the lead alone writes and curates, in five categories

- Status: Accepted
- Date: 2026-09-28
- Origin: user direction (2026-09-28): the library is the lead's to manage, nobody else may write
  in it, and the lead brings into it whatever is worthy, important, or needed at hand, whoever
  wrote it and whichever office holds it, and categorizes it. Amends
  [ADR-0018](0018-three-offices-library-and-archive.md) (the library's maintainers).
- Revisit when: a category outgrows one screen of index, or an office keeps knowledge the other
  roles look for.

## Context

- **Writing was already the lead's:** the ownership map lists `library/` for the lead only, and
  the guard enforces it. The library's own rules still allowed any role as an entry's
  maintainer.
- **Important knowledge sat outside the library:** the pedagogy, the technology radar, and the
  architecture standards lived in the lead's office, and the model facts were spread across
  ADRs, `AGENTS.md`, and research's briefs.
- **Two categories** (governance, engineering) didn't fit design rules, technology facts, or the
  learning method.

## Decision

- **The lead alone writes the library.** Every entry's maintainer is the lead; other roles read
  it and propose changes by message.
- **The lead curates it** at every phase and project boundary, and whenever a record becomes
  knowledge other roles rely on. It works from any office.
- **Move, never copy** (principle 9):
  - Stable knowledge (rules, guides, policies, lessons learned) moves into the library, and its
    old home links to it. For another role's file, the lead asks the owner by message.
  - Research's living facts (vendors, numbers, measurements) stay in research's landscape and
    evidence. A library entry carries the practical takeaway and the key numbers, with the record
    ID and its date.
- **Five categories:**

  | Category | Holds |
  | :--- | :--- |
  | Governance | How the roles work together: principles, protocol, ownership, terms |
  | Engineering | How we build and ship: git, dependencies, the environment |
  | Architecture | How we design: the standards every component meets, decision points |
  | Technology | Facts about the stack at hand: the radar, the model tiers and deciders |
  | Teaching | How the learner learns: the pedagogy |

- **The first pass,** 2026-09-28:
  - the pedagogy moved into Teaching;
  - the radar moved into Technology, with a new entry on the models;
  - the architecture principles, scale seams, and composition patterns moved into Architecture as
    its standards, and the decision-model rules moved there from Engineering.

  The lead's office keeps its plans and its registers (roadmap, backlog, decisions, risks, and the
  system map). Redirects stay at the old paths until the offices that link to them have updated.
- **`alireza/` stays outside:** it is private, and nothing enters the library from it unless the
  learner sends it.

## Consequences

- Every role finds shared knowledge in one place, by category, and the lead is accountable for
  keeping it current.
- Links into the moved files change; the mentor and research update theirs by message, and the
  redirects then go.
- The docs lint could require the lead as every entry's maintainer; the engineer tightens it.

## Alternatives considered

- **Index the lead's files in place:** rejected. The library would point into an office instead
  of holding the knowledge, and "shared" would mean two places.
- **Copy the key facts into the library:** rejected. Two copies of a fact drift (principle 9).
- **Keep two categories:** rejected. Design rules and teaching don't belong under engineering.
