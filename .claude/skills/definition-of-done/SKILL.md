---
name: definition-of-done
description: Verify work is really complete before calling it done or opening a PR - run all checks and tests, prove every acceptance criterion, scan the diff for secrets and debug code, and update docs. Use before saying a task is finished, before write-pr, or when asked "is this done?".
---

# Definition of done

Goal: an evidence-based pass/fail report. Never say "done" while any item fails.

## Steps

1. **Run the checks** from the repo root and read the output:
   - `pre-commit run --all-files` (format, lint, typecheck, secret scan)
   - `pre-commit run --all-files --hook-stage manual` (tests)
   If something fails, fix it and run again. Don't skip hooks, weaken tests, or add ignores
   just to get green; if you think a check is wrong, stop and ask.
2. **Prove each acceptance criterion.** Get them from the issue (`gh issue view <N>`; N is in
   the branch name). For each one, point to evidence: a test name, or `file:line` plus how you
   verified it. If a criterion has no test, add one or explain why it can't be tested.
3. **Review the diff**: `git diff main...HEAD` plus `git status` for uncommitted or untracked files.
   Look for:
   - debug output: `print(`, `console.log`, `debugger`, `breakpoint()`, `pdb`
   - commented-out code, stray files, temporary scripts
   - `TODO`/`FIXME` without an issue link
   - secrets, tokens, internal URLs, personal data (gitleaks ran in step 1; still eyeball it)
   - changes unrelated to the ticket (move them to a separate branch)
4. **Docs.** Update anything this change made wrong:
   - README (setup, usage), AGENTS.md (commands, conventions), code comments
   - an ADR in `docs/adr/` if you made an architectural choice (use the write-adr skill)
5. **Report** in this format:

```
Definition of done - <branch>
[PASS|FAIL] Checks (pre-commit)
[PASS|FAIL] Tests
[PASS|FAIL] AC1: <criterion> - <evidence>
[PASS|FAIL] AC2: ...
[PASS|FAIL] Diff clean (no debug code, secrets, unrelated changes)
[PASS|FAIL] Docs updated (or "not needed: <reason>")
Verdict: DONE | NOT DONE - <what's left>
```
