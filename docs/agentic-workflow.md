# Agentic workflow: what's included and why

This repo is set up so AI agents (Claude Code and Codex) work the same way a careful engineer
would: start from an issue, plan, branch, test, review, and never push to `main` directly.
This page explains each piece. Setup steps are in the [README](../README.md).

## The flow

1. Write an issue with testable acceptance criteria (the issue forms require them).
2. `start-ticket`: the agent reads the issue, restates the criteria, drafts a plan, and creates a branch.
3. The agent codes on that branch in small commits, with tests.
4. `definition-of-done`: checks, tests and evidence for every criterion.
5. `write-pr`: opens a draft PR with `Closes #N` and how it was tested.
6. `review-standards`, then a human review. CI must pass before merge.

The agent follows this because `AGENTS.md` tells it to. You still start each step (for example
"start ticket #12", or `/start-ticket 12` in Claude and `$start-ticket` in Codex).

## Skills

Reusable how-to guides the agent loads when relevant. The authoritative steps are in each
`.agents/skills/<name>/SKILL.md`.

| Skill | What it does | Why it helps |
|---|---|---|
| `start-ticket` | Reads the issue, restates acceptance criteria, drafts a plan, creates the branch. Asks before posting anything to GitHub | Agreement on "done" before any code is written |
| `definition-of-done` | Runs checks and tests, proves each criterion, scans the diff for debug code and secrets. Refuses to say "done" on any failure | Stops "it works" claims without evidence |
| `write-pr` | Fills the PR template with `Closes #N` and how it was tested. Asks before pushing | Reviewable PRs that link back to the issue |
| `review-standards` | Reviews a diff against `code_review.md`, by severity | Consistent self-review, including known AI mistakes |
| `write-adr` | Records an architecture decision from `docs/adr/0000-template.md` | Decisions stay written down |

## MCP servers (extra tools for the agent)

| Server | Use | Notes |
|---|---|---|
| GitHub | Read and update issues and PRs | Needs a fine-grained `GITHUB_PAT`. Without it the skills use the `gh` CLI |
| Context7 | Current library docs, so the agent doesn't invent APIs | Works without a key. A free `CONTEXT7_API_KEY` raises rate limits |
| Playwright | Browser automation for web projects | Off by default |
| Figma | Design context for design projects | Off by default |

## Hooks (automatic, in agent sessions)

All run `scripts/agent_hook.py`, so Claude and Codex behave the same.

| Hook | What it does | Protects against |
|---|---|---|
| Guard (before edits and shell commands) | Blocks edits to `.env`, keys, lock files and `.claude/skills/`. Blocks shell commands that read secret files | Leaked secrets, hand-edited lock files, generated files drifting |
| Format on edit | Formats the file the agent just changed (Ruff or Biome, if enabled) | Formatting noise in diffs |
| Run tests when the agent stops | Runs tests for changed files and sends failures back so the agent keeps fixing. Opt-in: `AGENT_STOP_TESTS=1` | The agent calling it done while tests are red |
| Notification | Desktop alert when the agent finishes or needs approval. Opt-in: `AGENT_NOTIFY=1` | Missing a permission prompt |

Hooks are an extra layer. If one misbehaves in Codex (hooks are approved per project and
the feature is newer), the guarantees below still hold.

## Permissions

- Run without asking: read-only git and `gh` commands, `pre-commit`, and test runners.
- Always ask first: `git push`, anything that writes to GitHub, installs and removals of dependencies, deleting files.
- Blocked outright: force-push, `--no-verify`, reading `.env` and key files.

## Safety nets that don't depend on the agent

| Layer | Runs | Checks |
|---|---|---|
| pre-commit (commit) | Every commit, by anyone | Format, lint, types, secret scan, skills sync, no commits to `main` |
| pre-commit (push) | Every push | Tests |
| CI | Every PR and push to `main` | The above plus a secret scan of the full history |
| Branch protection | On GitHub, set per repo | Requires a PR and green CI before merging to `main` |

Local hooks only exist after `pre-commit install`, and `--no-verify` bypasses them. CI and
branch protection are what actually stop a bad change reaching `main`.
