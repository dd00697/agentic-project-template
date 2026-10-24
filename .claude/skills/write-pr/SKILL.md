---
name: write-pr
description: Open a pull request using the repo's PR template - summarise the change, link the issue with "Closes #N", and describe exactly how it was tested. Use when the user asks to open, create, or write a PR.
---

# Write a pull request

## Steps

1. **Check it's ready.** If definition-of-done hasn't passed in this session, run that skill
   first. Don't open a PR with failing checks.
2. **Find the issue number** from the branch name (`feat/42-...` means #42). If there isn't one, ask.
3. **Write the body** by filling in `.github/pull_request_template.md`. Keep every heading.
   - **Summary**: what changed and why, in 1-3 sentences a reviewer can read in 10 seconds.
   - **Closes #N**: exactly this form, so GitHub closes the issue on merge.
   - **Changes**: bullets, grouped by area. Mention anything surprising.
   - **How was this tested?** The commands you ran and what happened, which tests were added,
     and any manual checks. Be specific: "ran `pre-commit run --all-files --hook-stage manual`,
     34 passed" beats "tested locally".
   - **Risks / rollback**: what could break and how to undo it. Write "Low: <reason>" if trivial.
   - **Checklist**: tick only what's actually true.
   Save the body to a temporary file outside the repo.
4. **Push** (this needs approval): `git push -u origin HEAD`.
5. **Create the PR**: `gh pr create --draft --title "<type>: <summary> (#N)" --body-file <tmpfile>`.
   Leave out `--draft` only if the user asked for a ready-for-review PR.
6. **Report** the PR URL and remind the user that CI will run.

## Rules

- Never claim a test was run unless you ran it in this session.
- One issue per PR. If the branch covers more, say so and suggest splitting it.
