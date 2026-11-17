#!/usr/bin/env python3
"""
detect_frameworks.py — Inspects repository manifests and source layout to detect
programming languages, testing frameworks, and execution commands.
"""

import json
import sys
from pathlib import Path

def detect_frameworks(workspace_dir: str) -> dict:
    workspace = Path(workspace_dir).resolve()
    results = {
        "workspace": str(workspace),
        "languages": [],
        "frameworks": [],
        "test_runners": [],
        "recommended_command": "",
        "test_dirs": []
    }

    # Check Python
    if any(workspace.glob("*.py")) or (workspace / "pyproject.toml").exists() or (workspace / "requirements.txt").exists():
        results["languages"].append("python")
        if (workspace / "pytest.ini").exists() or (workspace / "pyproject.toml").exists() or any(workspace.glob("**/test_*.py")):
            results["frameworks"].append("pytest")
            results["test_runners"].append("pytest")
            results["recommended_command"] = "pytest --tb=short"
        else:
            results["frameworks"].append("unittest")
            results["test_runners"].append("python3 -m unittest discover")

    # Check JavaScript / TypeScript
    pkg_json = workspace / "package.json"
    if pkg_json.exists():
        results["languages"].append("javascript")
        try:
            with open(pkg_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                if "jest" in deps:
                    results["frameworks"].append("jest")
                    results["test_runners"].append("npx jest")
                    results["recommended_command"] = "npx jest"
                if "@playwright/test" in deps or "playwright" in deps:
                    results["frameworks"].append("playwright")
                    results["test_runners"].append("npx playwright test")
                    if not results["recommended_command"]:
                        results["recommended_command"] = "npx playwright test"
                if "vitest" in deps:
                    results["frameworks"].append("vitest")
                    results["test_runners"].append("npx vitest run")
                    results["recommended_command"] = "npx vitest run"
        except (OSError, json.JSONDecodeError):
            pass

    # Check Java. JUnit 5 is an assumption for any Maven or Gradle build.
    if (workspace / "pom.xml").exists() or (workspace / "build.gradle").exists():
        results["languages"].append("java")
        results["frameworks"].append("junit5")
        if (workspace / "pom.xml").exists():
            results["test_runners"].append("mvn test")
            results["recommended_command"] = "mvn test"
        else:
            results["test_runners"].append("./gradlew test")
            results["recommended_command"] = "./gradlew test"

    # Identify test directories
    for possible_dir in ["tests", "__tests__", "test", "spec", "src/test"]:
        if (workspace / possible_dir).exists():
            results["test_dirs"].append(possible_dir)

    return results

def main():
    workspace = "."
    if len(sys.argv) > 2 and sys.argv[1] == "--workspace":
        workspace = sys.argv[2]
    
    info = detect_frameworks(workspace)
    print(json.dumps(info, indent=2))

if __name__ == "__main__":
    main()
