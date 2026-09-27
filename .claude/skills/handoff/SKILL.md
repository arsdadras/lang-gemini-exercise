---
name: handoff
description: End a role session cleanly - update the office's STATE.md, commit (a wip commit if the work is unfinished), push the role branch, and print a three-line summary. Use at the end of every lead, mentor, or research session, and before switching between machines or between local and cloud.
---

End this session so the next one (here, on another machine, or in the cloud) can start from
files alone (ADR-0019, `library/engineering/git-policy.md`).

1. **State.** Rewrite `offices/<role>/STATE.md`: where the work stands, what is unfinished, and
   the next agenda. Append to the office's log if its charter keeps one, and reply in your
   `OUTBOX.md` to every message you acted on.
2. **Check the changes.** Run `git status --short`. Every path must be your role's
   (`library/governance/ownership.md`); a link repair that your own move required is the only
   exception. If anything else is there, stop and tell the user instead of committing it.
3. **Commit and push.** Run
   `python scripts/handoff.py -m "<conventional subject>" --trailer "Co-Authored-By: <your model attribution>"`
   (`python3` where `python` is missing). Add `--wip` when the work is unfinished: the commit
   becomes `wip(<role>): <subject>`, and a wip branch may be red. Add `--pr` when the work is
   verified and ready for `main`; the lead merges it when CI is green.
4. **Report** the script's three lines to the user, as they are.
