---
name: start-ticket
description: Start work on a GitHub issue - read it, restate the acceptance criteria, post a short plan to the issue, and create a branch named after it. Use when the user says start, pick up, or work on issue #N / ticket N.
---

# Start a ticket

Goal: before writing any code, agree on what "done" means and set up a branch.

## Steps

1. **Get the issue number.** If the user didn't give one, ask. Don't guess.
2. **Read the issue.** Use the GitHub MCP server if it's connected; otherwise run
   `gh issue view <N> --comments`. Note the title, labels, body, and any decisions in comments.
3. **Restate the acceptance criteria** as a numbered checklist in your reply.
   - If the issue has none, or they're vague or untestable, draft concrete ones and
     **stop and ask the user to confirm** before continuing.
4. **Explore the code** you'll need to touch. Read; don't edit yet.
5. **Draft a plan** of 10 lines or fewer:
   - Approach (1-3 lines)
   - Files likely to change
   - Tests to add or update (one per acceptance criterion where possible)
   - Risks or open questions
6. **Post the plan to the issue**, but only after the user approves the wording:
   `gh issue comment <N> --body-file <tmpfile>` (or the MCP equivalent).
   Start the comment with `**Plan**` so it's easy to find later.
7. **Create the branch.**
   - Check `git status` is clean. If it isn't, stop and ask.
   - `git switch main && git pull --ff-only`
   - `git switch -c <type>/<N>-<short-slug>`, where `<type>` is `fix` for bug-labelled issues,
     `chore` for maintenance, and `feat` otherwise. Slug: 3-5 lowercase words from the title,
     joined with hyphens (e.g. `feat/42-export-csv-report`).
8. **Report**: the branch name, the acceptance-criteria checklist, and the first step you'll take.

## Rules

- Writing to GitHub (comments) is outward-facing: always confirm first.
- If the issue is too big for one PR, say so and propose a split instead of a plan.
