#!/usr/bin/env python3
"""Mirror .agents/skills (canonical, read by Codex) into .claude/skills (read by Claude Code).

Usage:
  python scripts/sync_skills.py          # update the copy; exit 1 if anything changed
  python scripts/sync_skills.py --check  # report drift only; exit 1 if out of sync

Exiting 1 after a change makes the pre-commit hook fail so you can `git add` the copy.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / ".agents" / "skills"
TARGET = ROOT / ".claude" / "skills"


def files_under(directory: Path) -> dict[Path, bytes]:
    if not directory.is_dir():
        return {}
    return {
        p.relative_to(directory): p.read_bytes()
        for p in sorted(directory.rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts
    }


def main() -> int:
    check_only = "--check" in sys.argv[1:]
    expected, actual = files_under(SOURCE), files_under(TARGET)
    stale = sorted(set(actual) - set(expected))
    changed = sorted(p for p, data in expected.items() if actual.get(p) != data)

    if not stale and not changed:
        return 0

    for rel in changed:
        print(
            f"{'out of date' if check_only else 'updated'}: .claude/skills/{rel.as_posix()}"
        )
    for rel in stale:
        print(
            f"{'stale' if check_only else 'removed'}: .claude/skills/{rel.as_posix()}"
        )

    if check_only:
        print(
            "Run `python scripts/sync_skills.py` and commit .claude/skills.",
            file=sys.stderr,
        )
        return 1

    for rel in changed:
        dest = TARGET / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(expected[rel])
    for rel in stale:
        (TARGET / rel).unlink()
    for directory in sorted((d for d in TARGET.rglob("*") if d.is_dir()), reverse=True):
        if not any(directory.iterdir()):
            directory.rmdir()

    print(
        "Synced .claude/skills. Review and `git add .claude/skills`.", file=sys.stderr
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
