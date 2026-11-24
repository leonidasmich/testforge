#!/usr/bin/env python3
"""
enforce_write_boundary.py - Claude Code PreToolUse hook for TestForge.

Blocks Write/Edit/NotebookEdit to any path outside the approved test
locations. Exit code 2 blocks the call and shows stderr to the model.

Bash is checked on a best-effort basis (redirects, tee, sed -i, rm, mv, cp).
It is NOT a guarantee: a shell can write files in ways a regex cannot see.
"""

import fnmatch
import json
import os
import re
import shlex
import sys
from pathlib import Path

ALLOWED_DIRS = ("tests", "test", "__tests__", "spec", "src/test", ".testforge")
ALLOWED_ROOT_FILES = ("TESTFORGE_REPORT.md", "TESTFORGE_PLAN.md", "testforge-results.json")
ALLOWED_NAME_GLOBS = ("test_*.py", "*_test.py", "*_test.go", "*.test.*", "*.spec.*", "*Test.java", "*Tests.java")

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}


def is_allowed(path: str, workspace: Path) -> bool:
    p = Path(path)
    if not p.is_absolute():
        p = workspace / p
    try:
        rel = Path(os.path.realpath(p)).relative_to(os.path.realpath(workspace))
    except ValueError:
        return False  # outside the workspace
    parts = rel.parts
    if not parts:
        return False
    rel_posix = rel.as_posix()
    if rel_posix in ALLOWED_ROOT_FILES:
        return True
    for d in ALLOWED_DIRS:
        dparts = tuple(d.split("/"))
        if parts[: len(dparts)] == dparts and len(parts) > len(dparts):
            return True
    # Test-named files anywhere (co-located tests such as foo.test.ts, FooTest.java)
    return any(fnmatch.fnmatch(parts[-1], g) for g in ALLOWED_NAME_GLOBS)


def bash_targets(cmd: str):
    """Best-effort extraction of paths a shell command writes to."""
    targets = [m.group(1) for m in re.finditer(r"(?<![<\d&])>>?\s*([^\s|&;<>]+)", cmd)]
    for seg in re.split(r"[;&|]+", cmd):
        try:
            tok = shlex.split(seg)
        except ValueError:
            continue
        if not tok:
            continue
        args = [t for t in tok[1:] if not t.startswith("-")]
        if tok[0] == "tee":
            targets += args
        elif tok[0] == "sed" and any(t.startswith("-i") or t == "--in-place" for t in tok[1:]):
            targets += args[1:]  # first positional is the script
        elif tok[0] in ("rm", "mv", "cp", "touch", "truncate"):
            targets += args if tok[0] != "cp" else args[-1:]
    return [t.strip("\"'") for t in targets if t not in ("/dev/null", "&1", "&2")]


def check(payload: dict):
    """Return an error message if the call must be blocked, else None."""
    tool = payload.get("tool_name", "")
    inp = payload.get("tool_input", {}) or {}
    workspace = Path(payload.get("cwd") or os.getcwd())
    if tool in WRITE_TOOLS:
        path = inp.get("file_path") or inp.get("notebook_path") or ""
        if path and not is_allowed(path, workspace):
            return path
    elif tool == "Bash":
        for t in bash_targets(inp.get("command", "")):
            if not is_allowed(t, workspace):
                return t
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0  # not our payload; do not break the session
    bad = check(payload)
    if bad:
        sys.stderr.write(
            f"TestForge write boundary: refusing to write '{bad}'. "
            "TestForge may only write under tests/, test/, __tests__/, spec/, src/test/, "
            ".testforge/, test-named files, or its report files. "
            "Do not modify application source; report the defect instead.\n"
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
