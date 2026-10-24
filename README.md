# agentic-project-template

A small starting point for projects built with AI coding agents. It works the same in
**Claude Code** and **OpenAI Codex**: switching tools needs no changes.

- **One set of instructions**: [`AGENTS.md`](AGENTS.md). `CLAUDE.md` only imports it.
- **One set of skills**: [`.agents/skills/`](.agents/skills), mirrored for Claude Code.
  `start-ticket` → `definition-of-done` → `write-pr` → `review-standards`, plus `write-adr`.
- **Guarantees that don't depend on the agent**: pre-commit (commit and push) and GitHub Actions CI.
  Agent hooks are an extra layer on top.
- **Language-agnostic by default**, with ready-made Python and TypeScript sections you can switch on.

> Replace this README with your project's own once you've created a repo from the template.
> Keep the "Setup" section.

## Setup (about 10 minutes)

### 1. Prerequisites

| Tool | Why | Install |
|---|---|---|
| Git (Windows: **Git for Windows**, which includes Git Bash) | Claude Code runs hooks in Git Bash on Windows | git-scm.com |
| Python 3.10+ | pre-commit and the hook scripts | python.org |
| GitHub CLI | skills read issues and open PRs | `gh auth login` |
| uv | Python projects only | docs.astral.sh/uv |
| Node 20+ | TypeScript projects and the Playwright MCP server only | nodejs.org |

### 2. Create the repo and install the git hooks

Click **Use this template** on GitHub, clone the new repo, then:

```sh
pip install pre-commit        # or: uv tool install pre-commit / pipx install pre-commit
pre-commit install            # installs both the commit and push hooks
pre-commit run --all-files    # first run downloads the hook tools
```

### 3. Secrets (environment variables only)

Neither agent reads `.env`. Put these in your environment ([`.env.example`](.env.example) lists them all):

- **`GITHUB_PAT`**: a [fine-grained token](https://github.com/settings/personal-access-tokens/new)
  - Repository access: *only select repositories*
  - Permissions: **Issues** read and write, **Pull requests** read and write, **Contents** read-only.
    Metadata is added automatically. Pushing goes through `git`, not MCP.
  - Expiry: 90 days or less
  - *Work orgs:* an organisation can block or require approval for personal access tokens.
    Check your org's policy first. If tokens aren't allowed, leave the GitHub MCP server
    unconfigured: every skill falls back to the `gh` CLI, which logs in with OAuth/SSO.
  Without it the `github` server shows as failed in `/mcp`. That's harmless, and the skills use `gh`.
- **`CONTEXT7_API_KEY`** (optional): Context7 serves up-to-date library docs and works without a key.
  A free key from [context7.com](https://context7.com) (it starts with `ctx7sk`) raises the rate limits.
  Leave it unset rather than using a placeholder, because a wrong key makes every call fail.

```powershell
# Windows (then open a new terminal)
setx GITHUB_PAT "github_pat_..."
setx CONTEXT7_API_KEY "ctx7sk-..."
```
```sh
# macOS / Linux: add to ~/.zshrc or ~/.bashrc
export GITHUB_PAT="github_pat_..."
export CONTEXT7_API_KEY="ctx7sk-..."
```

`setx` stores values in your user profile, unencrypted. If you'd rather not, launch the agent
through your password manager's CLI (for example `op run -- claude`).

### 4. Claude Code

Open the folder and accept the **trust** prompt. Committed allow rules and MCP servers wait until
you trust the folder. Then check:

- `/context` lists `CLAUDE.md` and `AGENTS.md`
- `/mcp` shows `github` and `context7` connected
- `/hooks` lists the guard, after-edit, stop and notification hooks
- typing `/` shows the five skills

### 5. Codex

Open the folder and **trust the project** when asked. Project config, MCP servers, hooks and
rules in `.codex/` load only for trusted projects. Then:

- `/hooks`: review and approve the project hooks (one time)
- `/mcp` shows `github` and `context7`
- `/skills` (or type `$`) shows the five skills

Optional desktop notifications. Project config can't set these, so add them to your own
`~/.codex/config.toml`:

```toml
notify = ["python", "/absolute/path/to/repo/scripts/agent_hook.py", "notify"]  # also set AGENT_NOTIFY=1

[tui]
notifications = ["agent-turn-complete", "approval-requested"]
```

### 6. Make it yours

1. Fill in the **Project** section of `AGENTS.md`.
2. Switch on your language. Uncomment the `PYTHON` or `TYPESCRIPT` block in **both**
   `.pre-commit-config.yaml` and `.github/workflows/ci.yml`, and delete the other language's
   section from `AGENTS.md`.
   - Python: `uv init`, then `uv add --dev mypy pytest`, and set `[tool.mypy] files = ["src", "tests"]`.
   - TypeScript: `npm init -y`, `npm i -D @biomejs/biome typescript vitest`, `npx biome init`, `npx tsc --init`.
     Then in `biome.json` set `"formatter": { "useEditorconfig": true }`. Biome's default is tab
     indentation, which would reformat the template's JSON files and clash with `.editorconfig`.
     Make sure `tsconfig.json` has `"strict": true` and `"noEmit": true`.
3. Run `pre-commit run --all-files` and `pre-commit run --all-files --hook-stage manual`.
4. On GitHub: protect `main` and require the **checks** and **secrets** status checks.
   For the template repo itself, tick *Settings → Template repository*.

## How it works

### Where each tool looks

| What | Claude Code reads | Codex reads |
|---|---|---|
| Instructions | `CLAUDE.md` → `@AGENTS.md` | `AGENTS.md` |
| Skills | `.claude/skills/` (generated copy) | `.agents/skills/` (canonical) |
| MCP servers | `.mcp.json` | `.codex/config.toml` |
| Permissions | `.claude/settings.json` | sandbox defaults + `.codex/rules/default.rules` |
| Hooks | `.claude/settings.json` → `scripts/agent_hook.py` | `.codex/config.toml` → `scripts/agent_hook.py` |

### Layers of enforcement

| Layer | Applies to | What it does |
|---|---|---|
| **pre-commit**, commit stage | Every commit, from anyone | Formatting, lint, typecheck, gitleaks, private keys, merge markers, large files, skills sync, no commits to `main` |
| **pre-commit**, push stage | Every push | Tests |
| **CI** | Every PR and push to `main` | All of the above, plus a gitleaks scan of the full history |
| Claude Code hooks and permissions | Claude sessions | Blocks edits to `.env*`, keys and lock files. Formats edited files. Optional tests at stop and notifications. Prompts before installs, deletes, pushes and writes to GitHub |
| Codex hooks and rules | Codex sessions | The same hook script. Rules prompt before installs, deletes, pushes and writes to GitHub |

**Known Codex gaps.** These are best-effort, and the real guarantee is pre-commit plus CI:
- Codex rules are experimental.
- Codex can't deny file *reads*. The hook only blocks shell commands that mention secret files.
- Codex has no project-level notification hook.

### Per-person options

Off by default so shared repos stay quiet. Set these in your environment (both tools) or in the
`env` block of your gitignored `.claude/settings.local.json` (Claude only):

| Variable | Effect |
|---|---|
| `AGENT_STOP_TESTS=1` | When the agent stops, run tests for changed files. If they fail, the agent keeps working |
| `AGENT_NOTIFY=1` | Desktop notification when the agent finishes or needs approval |

## Common changes

- **Edit a skill:** edit `.agents/skills/<name>/SKILL.md`, run `python scripts/sync_skills.py`,
  and commit both folders. Never edit `.claude/skills/` directly: pre-commit and CI reject drift.
  Keep frontmatter to `name` and `description` so both tools accept it.
- **Add a skill:** create `.agents/skills/<name>/SKILL.md`. `name` must match the folder:
  lowercase letters and hyphens, at most 64 characters. Then sync.
- **Enable Playwright (web) or Figma (design) MCP:** in Claude, remove the server from
  `disabledMcpjsonServers` in `.claude/settings.json`. In Codex, set `enabled = true` in
  `.codex/config.toml`. Figma uses OAuth: run `/mcp` in Claude or `codex mcp login figma` in Codex.
- **Allow commits to `main`** (quick personal projects): delete the `no-commit-to-branch` hook from
  `.pre-commit-config.yaml` and remove it from `SKIP:` in `ci.yml`.
- **Bump pinned versions:** run `pre-commit autoupdate` and update `GITLEAKS_VERSION` in `ci.yml`.
  Then re-test any language block you use, because commented-out blocks drift if nobody runs them.

## Windows notes

- **Line endings:** `.gitattributes` forces LF, so `core.autocrlf` doesn't cause churn.
- **Python name:** hooks call `python` first, then `python3`. On Windows, `python3` is often the
  Microsoft Store alias rather than your real install.
- **Without Git Bash**, Claude Code runs hooks in PowerShell and the hook commands fail.
  Install Git for Windows.
- **Skills are copied, not symlinked**, so a fresh clone works without Developer Mode. If you prefer
  symlinks: enable Developer Mode, run `git config --global core.symlinks true` before cloning,
  replace each `.claude/skills/<name>` with a link to `../../.agents/skills/<name>`, and remove the
  `sync-skills` hook.
- **Playwright MCP on Windows** may need `"command": "cmd", "args": ["/c", "npx", ...]` in `.mcp.json`.
