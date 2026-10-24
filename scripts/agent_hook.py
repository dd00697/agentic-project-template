#!/usr/bin/env python3
"""Shared hook for Claude Code and Codex.

Usage: agent_hook.py {guard|after-edit|stop|notify}

Reads the hook event as JSON on stdin (Codex `notify` passes it as the last
argument instead). Blocking is done with JSON on stdout and exit code 0, because
that is the one form both tools honour: Codex 0.163 on Windows ignores exit code 2
and only logs "PreToolUse Failed". Standard library only, so it runs the same on
Windows, macOS and Linux.

Per-person switches (environment variables, off unless set to 1):
  AGENT_STOP_TESTS  run tests for changed files when the agent stops
  AGENT_NOTIFY      desktop notification on finish / approval needed
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent

LOCK_FILES = {
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lockb",
    "uv.lock",
    "poetry.lock",
    "Pipfile.lock",
    "Cargo.lock",
}
SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
PRIVATE_KEY_NAMES = {"id_rsa", "id_ecdsa", "id_ed25519"}
GENERATED_DIR = PurePosixPath(".claude/skills")

# Secret files referenced in a shell command. Lock files are deliberately not
# matched here: package managers rewrite them, and installs are gated by "ask".
SHELL_SECRET = re.compile(
    r"""(?<![\w.$-])(?:[\w./\\-]*[/\\])?(?:\.env(?:\.[\w.-]+)?|[\w-]+\.env)(?![\w.-])"""
    r"""|[\w./\\-]+\.(?:pem|key|p12|pfx)(?=$|[\s'"`;|&)])"""
    r"""|\bid_(?:rsa|ecdsa|ed25519)\b(?!\.pub)"""
    r"""|(?:^|[\s'"=/\\])secrets[/\\]"""
)
PATCH_FILE = re.compile(
    r"^\*\*\* (?:Add|Update|Delete) File: (.+)$|^\*\*\* Move to: (.+)$", re.MULTILINE
)
BIOME_SUFFIXES = {
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".ts",
    ".tsx",
    ".mts",
    ".cts",
    ".json",
    ".jsonc",
    ".css",
}


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    handlers = {
        "guard": guard,
        "after-edit": after_edit,
        "stop": stop,
        "notify": notify,
    }
    if command not in handlers:
        print(__doc__, file=sys.stderr)
        return 1
    return handlers[command](read_event())


def read_event() -> dict:
    raw = (
        sys.argv[2]
        if len(sys.argv) > 2
        else ("" if sys.stdin.isatty() else sys.stdin.read())
    )
    try:
        event = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return {}
    return event if isinstance(event, dict) else {}


# --- guard -----------------------------------------------------------------


def guard(event: dict) -> int:
    """PreToolUse: block edits to secrets, lock files and generated skills."""
    edited, shell = tool_targets(event)
    for raw in edited:
        reason = protected_reason(raw)
        if reason:
            return deny(f"Blocked edit to {raw}: {reason}")
    if shell:
        match = SHELL_SECRET.search(shell)
        if match and not match.group(0).strip(" '\"=/\\").endswith(".env.example"):
            return deny(
                f"Blocked command: it references a secret file ({match.group(0).strip()}). "
                "Do not read or print secrets; ask the user if you need a value."
            )
    return 0


def tool_targets(event: dict) -> tuple[list[str], str]:
    """Return (file paths being edited, shell command text) for Claude or Codex events."""
    tool_input = event.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return [], ""
    paths = [
        tool_input[k]
        for k in ("file_path", "notebook_path", "path")
        if isinstance(tool_input.get(k), str)
    ]
    command = tool_input.get("command") or tool_input.get("cmd") or ""
    if isinstance(command, list):
        command = " ".join(map(str, command))
    if "*** Begin Patch" in command:  # Codex apply_patch
        paths += [(a or b).strip() for a, b in PATCH_FILE.findall(command)]
        return paths, ""
    return paths, command


def protected_reason(raw: str) -> str | None:
    path = PurePosixPath(raw.replace("\\", "/"))
    name = path.name
    if name == ".env.example":
        return None
    if name == ".env" or name.startswith(".env.") or name.endswith(".env"):
        return "environment files hold secrets. Edit .env.example (names only) instead."
    if (
        path.suffix.lower() in SECRET_SUFFIXES
        or name in PRIVATE_KEY_NAMES
        or "secrets" in path.parts
    ):
        return "this looks like a secret or key file."
    if name in LOCK_FILES:
        return "lock files change only through the package manager (e.g. npm install, uv add)."
    if is_under(raw, ROOT / GENERATED_DIR):
        return "generated copy. Edit .agents/skills/ and run `python scripts/sync_skills.py`."
    return None


def is_under(raw: str, directory: Path) -> bool:
    path = Path(raw)
    if not path.is_absolute():
        path = Path.cwd() / path
    try:
        path.resolve().relative_to(directory.resolve())
        return True
    except ValueError:
        return False


def deny(message: str) -> int:
    """PreToolUse: refuse the tool call. The message goes back to the agent."""
    reply = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": message,
        }
    }
    print(json.dumps(reply))
    return 0


def keep_working(message: str) -> int:
    """Stop: don't let the agent finish yet. The message becomes its next instruction."""
    print(json.dumps({"decision": "block", "reason": message}))
    return 0


# --- after-edit ------------------------------------------------------------


def after_edit(event: dict) -> int:
    """PostToolUse: run the project's formatter on edited files. Silent, never blocks."""
    edited, _ = tool_targets(event)
    for raw in edited:
        path = Path(raw) if Path(raw).is_absolute() else Path.cwd() / raw
        if not path.is_file():
            continue
        formatter = formatter_for(path)
        if formatter:
            try:
                subprocess.run(
                    [*formatter, str(path)],
                    cwd=ROOT,
                    capture_output=True,
                    timeout=25,
                    check=False,
                )
            except (OSError, subprocess.SubprocessError):
                pass
    return 0


def formatter_for(path: Path) -> list[str] | None:
    suffix = path.suffix.lower()
    if suffix in {".py", ".pyi"} and hook_enabled("ruff-format"):
        # Same pinned ruff as the commit hook, with no extra project dependency.
        return [*pre_commit_runner(), "run", "ruff-format", "--files"]
    if suffix in BIOME_SUFFIXES and any(
        (ROOT / n).exists() for n in ("biome.json", "biome.jsonc")
    ):
        biome = local_bin("biome", ROOT / "node_modules")
        if biome:
            return [biome, "format", "--write", "--no-errors-on-unmatched"]
    return None


def hook_enabled(hook_id: str) -> bool:
    """True if .pre-commit-config.yaml has this hook uncommented."""
    try:
        config = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    except OSError:
        return False
    return (
        re.search(rf"^\s*-\s*id:\s*{re.escape(hook_id)}\s*$", config, re.MULTILINE)
        is not None
    )


def pre_commit_runner() -> list[str]:
    found = shutil.which("pre-commit")
    return [found] if found else [sys.executable, "-m", "pre_commit"]


def local_bin(name: str, env_dir: Path) -> str | None:
    """Find an executable inside a project-local .venv or node_modules."""
    candidates = [
        env_dir / "bin" / name,
        env_dir / "Scripts" / f"{name}.exe",
        env_dir / ".bin" / name,
    ]
    if os.name == "nt":
        candidates.insert(0, env_dir / ".bin" / f"{name}.cmd")
    return next((str(c) for c in candidates if c.is_file()), None)


# --- stop ------------------------------------------------------------------


def stop(event: dict) -> int:
    """Stop: optionally run tests for changed files; keep the agent working if they fail."""
    if os.environ.get("AGENT_STOP_TESTS") == "1" and not event.get("stop_hook_active"):
        changed = changed_files()
        if changed:
            try:
                result = subprocess.run(
                    [
                        *pre_commit_runner(),
                        "run",
                        "--hook-stage",
                        "manual",
                        "--files",
                        *changed,
                    ],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                print("Tests timed out after 300s; not blocking.", file=sys.stderr)
            else:
                if result.returncode != 0:
                    tail = "\n".join(
                        (result.stdout + result.stderr).strip().splitlines()[-60:]
                    )
                    return keep_working(
                        f"Tests are failing. Fix them before finishing.\n{tail}"
                    )
    send_notification("Agent finished", event)
    return 0


def changed_files() -> list[str]:
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    files, entries = [], iter(out.split("\0"))
    for entry in entries:
        if len(entry) < 4:
            continue
        status, path = entry[:2], entry[3:]
        if "R" in status or "C" in status:
            next(entries, None)  # skip the rename source
        if "D" not in status and (ROOT / path).is_file():
            files.append(path)
    return files


# --- notify ----------------------------------------------------------------


def notify(event: dict) -> int:
    """Notification (Claude) or `notify` (Codex): desktop alert, opt-in."""
    send_notification(event.get("message") or "Agent needs your attention", event)
    return 0


def send_notification(default: str, event: dict) -> None:
    if os.environ.get("AGENT_NOTIFY") != "1":
        return
    title = event.get("title") or f"Agent · {ROOT.name}"
    message = str(event.get("last-assistant-message") or default)[:200]
    try:
        if sys.platform == "win32":
            windows_toast(title, message)
        elif sys.platform == "darwin":
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    "on run argv",
                    "-e",
                    "display notification (item 1 of argv) with title (item 2 of argv)",
                    "-e",
                    "end run",
                    message,
                    title,
                ],
                timeout=10,
                check=False,
            )
        elif shutil.which("notify-send"):
            subprocess.run(["notify-send", title, message], timeout=10, check=False)
        else:
            sys.stderr.write("\a")
    except (OSError, subprocess.SubprocessError):
        pass


def windows_toast(title: str, message: str) -> None:
    """Toast via built-in WinRT APIs (no modules needed); beep if that fails."""
    script = r"""
$ErrorActionPreference = 'Stop'
try {
  [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
  [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null
  $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
  $t = [Security.SecurityElement]::Escape($env:AGENT_TOAST_TITLE)
  $m = [Security.SecurityElement]::Escape($env:AGENT_TOAST_MESSAGE)
  $xml.LoadXml("<toast><visual><binding template='ToastGeneric'><text>$t</text><text>$m</text></binding></visual></toast>")
  $app = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe'
  [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($app).Show(
    [Windows.UI.Notifications.ToastNotification]::new($xml))
} catch { [console]::beep(880, 300) }
"""
    env = {**os.environ, "AGENT_TOAST_TITLE": title, "AGENT_TOAST_MESSAGE": message}
    subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
        env=env,
        capture_output=True,
        timeout=15,
        check=False,
    )


if __name__ == "__main__":
    sys.exit(main())
