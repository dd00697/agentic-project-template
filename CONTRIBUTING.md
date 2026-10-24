# Contributing

How we work on this repo, with or without an AI agent. The agent drafts and you decide.
For what each skill, MCP server and hook does, see [docs/agentic-workflow.md](docs/agentic-workflow.md).
For setup, see the [README](README.md).

## Principles

- **You own everything you submit**, whoever wrote it. "The agent wrote it" is never an answer in review.
- **Never push code you can't explain.** If you couldn't defend a line in review, don't ship it.
- **Evidence over claims.** "Done" means checks pass and each acceptance criterion is shown to work, not that the agent says so.
- **Small and boring wins.** Small tickets, small diffs, small commits. Large AI-generated diffs get skimmed, and bugs hide in them.
- **Checks are not obstacles.** If a hook, test or CI check fails, fix the cause. Never skip it, loosen it or bypass it (`--no-verify`).

## 1. Picking and writing a ticket

A good ticket is one outcome that fits in one PR.

- Use the issue form. **Acceptance criteria are required**, and each one must be testable ("exporting an empty list returns a header-only CSV"), not vague ("export works well").
- State what's **out of scope**. Agents widen scope unless told not to.
- Too big? Split it before starting. If you can't describe it in two sentences, it's two tickets.
- Bugs: include repro steps. The fix starts with a failing regression test.

## 2. Starting work

1. Tell the agent `start ticket #N` (`/start-ticket N` in Claude, `$start-ticket` in Codex).
2. **Read the plan before approving it.** Push back on: files you didn't expect, no tests, new dependencies, scope beyond the ticket.
3. Only then does it post the plan to the issue and create `feat|fix|chore/<N>-short-slug`.

For anything non-trivial, use plan mode (Claude: Shift+Tab until it shows plan mode) so the agent explores and
proposes before it edits anything.

## 3. Working with the agent

- **One task per session.** Start fresh (`/clear` in Claude, or a new Codex session) between tickets. Stale context makes agents drift.
- **Be specific.** Name files, behaviours and constraints. "Add CSV export to `reports/`, following how `json_export.py` works" beats "add export".
- **Tests first for bugs and logic.** Ask for the failing test, check it fails for the right reason, then ask for the fix.
- **Commit often, in small steps**, so you can undo one step without losing the rest.
- **Watch for the usual AI failures** (the full list is in [code_review.md](code_review.md)):
  - invented functions or flags: check anything unfamiliar against the docs (the Context7 MCP server helps)
  - tests weakened, skipped or rewritten to pass
  - changes outside the ticket, "while I'm here" refactors
  - broad `try/except`, `any`, `# type: ignore`, lint disables
  - extra layers, options and abstractions nobody asked for
- **Correct the cause, not just the output.** If the agent keeps making the same mistake, add a short rule to `AGENTS.md` (keep it concrete and brief, it's loaded every session).
- **Stuck or looping?** Stop it. Re-state the goal, narrow the task, or start a fresh session. Don't keep pushing on a confused session.
- **Run it yourself.** Run the tests and use the feature. Reading a diff isn't the same as seeing it work.

### Which tool when

| You want to... | Use |
|---|---|
| Understand the ticket and set up the branch | `start-ticket` |
| Check work is really finished | `definition-of-done` |
| Open the PR | `write-pr` |
| Review a diff against our standard | `review-standards` |
| Record a design choice | `write-adr` |
| Read or update issues and PRs | GitHub MCP (or `gh`) |
| Check a library's real, current API | Context7 MCP |
| Test a web UI in a real browser | Playwright MCP (enable per project) |
| Get design context | Figma MCP (enable per project) |

## 4. Commits, branches and pushing

- **Never commit or push to `main`.** Always work on a ticket branch. Branch protection and the pre-commit hook enforce this.
- Branches: `feat/<N>-slug`, `fix/<N>-slug`, `chore/<N>-slug`.
- Commit messages: [Conventional Commits](https://www.conventionalcommits.org/), for example `feat: add CSV export`, `fix: handle empty report`. One logical change per commit, explaining why when it isn't obvious.
- Run `pre-commit run --all-files` and the test stage before pushing. The push hook runs the tests anyway.
- Pushing is a deliberate step. The agent asks first, and you should look at what's going out (`git diff origin/main...`).
- Never force-push a shared branch, and never use `--no-verify`.

## 5. Opening the PR

- Use `write-pr`: fill every section of the template, with `Closes #N`.
- Open it as a **draft** until CI is green and you've read your own diff end to end.
- **Keep it small:** aim for about 400 changed lines or fewer, and one ticket per PR. If it's bigger, split it.
- **"How was this tested?" must be true.** List the commands you actually ran and what they showed.
- Tick the checklist honestly. An unticked box with a reason beats a false tick.

## 6. Reviewing

Review is the main defence against AI slop. A rubber stamp defeats the purpose.

1. **Intent first.** Read the issue, then the PR description. Does the change solve the right problem, within scope?
2. **Then the code**, against [code_review.md](code_review.md). Read tests before implementation: do they prove the acceptance criteria?
3. **Run it.** Check out the branch, run the tests, try the feature.
4. **Hunt for the AI failures** (invented APIs, hollow tests, scope creep, dead code).
5. **Give findings by severity** (blocking, should fix, nit), each with `file:line` and a suggested fix.
6. **Only approve what you understand.** "I don't follow this" is a valid blocking comment.

Using an agent as a second reviewer helps, but it doesn't replace you:

- **Review in a fresh session**, not the one that wrote the code. A new session has no attachment to the original reasoning and is better at spotting problems.
- Use `review-standards`, or Claude's built-in `/code-review` and `/security-review`, or `codex exec review` in Codex.
- In Claude Code you can also ask for a **sub-agent** to review a diff or investigate part of the code. It works in its own context, so your main session stays focused. Give it a narrow brief ("review `reports/` against `code_review.md`, report only blocking issues").
- Treat agent review as a checklist runner. It finds mechanical problems well, and design judgement stays with you.
- Ask it to **verify its own claims**: "show the test that covers criterion 2".

## 7. What not to delegate

Do these yourself, or review them line by line:

- security-sensitive code (auth, permissions, crypto, input handling)
- database schema changes and data migrations
- anything touching secrets, CI, deployment or branch settings
- dependency additions (check the package is real, maintained and necessary)
- the decision to merge

## 8. When things go wrong

- **A hook or check fails:** read the message and fix the cause. Don't bypass it.
- **CI fails but local passes:** compare versions and config. Never mark the check as optional.
- **A secret was committed or pushed:** rotate it **first**. Rewriting history does not make it safe again. Then remove it from the repo.
- **The agent edited something it shouldn't have:** `git restore` the files, then tighten the ticket or add a rule to `AGENTS.md`.
- **The agent went in a wrong direction:** discard the branch changes and re-plan. Throwing away a bad attempt is cheaper than repairing it.

## 9. More tips

- **Parallel work:** use git worktrees (Claude Code can create them) to run separate agent sessions on separate tickets without them stepping on each other.
- **Check what the agent actually sees:** `/context` in Claude shows which instruction files and skills are loaded.
- **Keep instructions lean.** Long `AGENTS.md` files get followed less reliably. Move rarely-needed detail into a skill.
- **Write the decision down.** If a choice took a conversation, use `write-adr` so nobody has to rediscover it.
- **Use the cheapest check first.** Format, lint and types are fast. Run them often, and save full tests for milestones.
- **Be wary of confident explanations.** If a summary of the change sounds better than the diff, trust the diff.

## 10. Repo settings that make this stick

Set these on GitHub for every repo made from the template (settings don't carry over from a template):

- Protect `main`: require a pull request, require the `checks` and `secrets` status checks, block force-pushes.
- Require **at least one human approval**. On a solo repo you can't approve your own PR, so there rely on the checks plus a careful self-review.
- Delete branches after merge, and prefer squash merges so history stays one commit per ticket.
- Run `pre-commit install` in every clone. Local hooks don't exist until you do.
