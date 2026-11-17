#!/usr/bin/env python3
"""
validate_test_environment.py — Heuristic safety probe.

Checks workspace write access and flags environment variables whose names look
like environment, stage, or database settings and whose values look like
production. This does not sandbox commands or block network access.

Variable values are never printed.
"""

import json
import os
import re
import sys
from pathlib import Path

# Match prod / production / live as tokens, including prod_db and my-prod-host.
# Do not match unrelated words such as PRODUCT or DELIVERY.
PRODUCTION_VALUE = re.compile(
    r"(?:^|[^A-Za-z])(?:production|prod|live)(?:[^A-Za-z]|$)",
    re.IGNORECASE,
)
# ENV covers NODE_ENV and ENVIRONMENT. DATABASE is matched as a word so
# DATABASE_URL counts; a bare "DB" still matches DB_HOST and POSTGRES_DB.
NAME_HINT = re.compile(r"ENV|STAGE|DATABASE|(?:^|_)DB(?:_|$)", re.IGNORECASE)


def validate_environment(workspace_dir: str) -> dict:
    workspace = Path(workspace_dir).resolve()
    issues = []
    warnings = []

    if not os.access(workspace, os.W_OK):
        issues.append(f"Workspace directory {workspace} is not writable.")

    for key, val in os.environ.items():
        if not isinstance(val, str):
            continue
        if NAME_HINT.search(key) and PRODUCTION_VALUE.search(val):
            issues.append(
                f"Environment variable {key} looks like a production setting. "
                "The value was not printed."
            )

    testforge_dir = workspace / ".testforge"
    try:
        testforge_dir.mkdir(exist_ok=True)
    except OSError as exc:
        issues.append(f"Failed to create temporary staging directory .testforge: {exc}")

    is_safe = len(issues) == 0
    return {
        "is_safe": is_safe,
        "workspace": str(workspace),
        "issues": issues,
        "warnings": warnings,
        "recommended_mode": "audit" if is_safe else "plan",
    }


def main():
    workspace = "."
    if len(sys.argv) > 2 and sys.argv[1] == "--workspace":
        workspace = sys.argv[2]

    res = validate_environment(workspace)
    print(json.dumps(res, indent=2))
    if not res["is_safe"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
