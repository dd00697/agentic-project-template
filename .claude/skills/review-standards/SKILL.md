---
name: review-standards
description: Review a diff, branch, or pull request against the team's code_review.md and report findings by severity with file:line references. Use when asked to review code, a branch, a PR, or "check my changes".
---

# Review against the standards

Goal: a review a senior engineer would sign off on, based on `code_review.md` rather than taste.

## Steps

1. **Get the diff.**
   - Current branch: `git diff main...HEAD`. Include `git diff` too if there are uncommitted changes.
   - A PR: `gh pr diff <N>` and `gh pr view <N>` for the description.
2. **Load the standard.** Read `code_review.md` in full. It is the checklist.
3. **Load the intent.** Find the linked issue (`Closes #N`, or the branch name) and read its
   acceptance criteria. A correct change that doesn't meet them is still a blocker.
4. **Review file by file.** Open the surrounding code when the diff alone isn't enough to judge.
   Check every item in `code_review.md`, including the section on common AI-generated problems.
5. **Report** in the output format defined in `code_review.md`:
   - a verdict first, then findings grouped by severity
   - each finding: `path:line`, what's wrong, why it matters, and a concrete fix
   - say what you didn't review (e.g. generated files, binary assets)

## Rules

- Don't edit any files unless the user asks you to apply fixes.
- Don't pad the review. No findings in a category means nothing to say about it.
- If you're unsure whether something is a bug, say so and give the reason rather than inflating its severity.
