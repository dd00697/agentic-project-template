# AGENTS.md

Instructions for AI coding agents (Claude Code, Codex, and others). This is the only copy of
these rules: `CLAUDE.md` just imports it. Keep it short, specific, and true.

## Project

<!-- TODO: replace with 2-3 lines: what this project is, who uses it, and the main tech. -->
_Describe the project here._

## Commands

Run everything from the repo root. pre-commit is the single source of truth: git hooks, agent
hooks, and CI all run these same commands.

| Purpose | Command |
|---|---|
| Format, lint, typecheck, secret scan | `pre-commit run --all-files` |
| Tests | `pre-commit run --all-files --hook-stage manual` |
| Checks on specific files | `pre-commit run --files <paths...>` |
| After editing skills | `python scripts/sync_skills.py` |

## Workflow

1. Work starts from a GitHub issue: use the **start-ticket** skill (branch `feat|fix|chore/<N>-<slug>`).
2. Make small, focused commits on that branch. Never commit to `main`.
3. Before saying you're done, use **definition-of-done**. Every acceptance criterion needs evidence.
4. Open the PR with **write-pr** (`Closes #N`, how it was tested).
5. Use **review-standards** to self-review against `code_review.md` before asking for human review.
6. Record significant technical decisions with **write-adr** in `docs/adr/`.

## Rules

- Change only what the ticket needs. Note unrelated problems in your reply instead of fixing them.
- Follow the existing patterns, naming, and structure of the surrounding code.
- Every behaviour change comes with a test that would fail without it. Bug fixes start with a
  failing regression test.
- Don't weaken, skip, or delete tests or checks to get green. Never use `--no-verify`.
- Don't use APIs you haven't confirmed exist. Check the installed version's docs (Context7 MCP)
  or the source.
- Handle errors explicitly. Never swallow exceptions silently.
- No secrets, tokens, or personal data in code, tests, logs, or commit messages. Configuration
  comes from environment variables, documented by name in `.env.example`.
- Never edit by hand: `.env*` files, lock files (use the package manager), or `.claude/skills/`
  (a generated copy of `.agents/skills/`).

## Ask the user first

- Adding, removing, or upgrading dependencies
- Deleting files or directories
- `git push`, and anything that writes to GitHub (issue comments, PRs)
- Changing CI, auth, security settings, or secrets handling
- Changing a public API, database schema, or data format
- Anything irreversible, or anything you're unsure about

## Repo map

| Path | What |
|---|---|
| `AGENTS.md` | These instructions (`CLAUDE.md` imports it) |
| `code_review.md` | Review standard. Read it when reviewing or self-reviewing |
| `.agents/skills/` | Canonical skills, read by Codex |
| `.claude/skills/` | Generated copy for Claude Code (`scripts/sync_skills.py`) |
| `.claude/settings.json`, `.codex/` | Agent permissions, hooks, MCP servers |
| `scripts/agent_hook.py` | Shared Claude/Codex hook (guard, format, stop, notify) |
| `docs/adr/` | Architecture decision records |
| `docs/agentic-workflow.md` | What each skill, MCP server and hook does, and why (for humans) |

<!-- ==== PYTHON (delete this section if unused) ==== -->
## Python

- Tooling: `uv` (env + deps), `ruff` (format + lint), `mypy` (types), `pytest` (tests).
- Add dependencies with `uv add <pkg>` (ask first). Run tools with `uv run <tool>`.
- Type-annotate all public functions. No bare `except:`. No `print` for logging (use `logging`).
- Code lives in `src/<package>/` and tests in `tests/`, mirroring the source layout (`test_<module>.py`).

<!-- ==== TYPESCRIPT (delete this section if unused) ==== -->
## TypeScript

- Tooling: `npm`, Biome (format + lint), `tsc --noEmit` (types), Vitest (tests).
- Add dependencies with `npm install <pkg>` (ask first). Commit `package-lock.json`.
- `strict` mode stays on. No `any` (use `unknown` and narrow). No non-null `!` without a comment saying why.
- Tests sit next to the code as `*.test.ts`.
