#!/usr/bin/env python3
"""
detect_frameworks.py — Inspects repository manifests and source layout to detect
programming languages, testing frameworks, and execution commands.
"""

import json
import re
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

    # Check Java. The framework comes from the build file; never assume one.
    java_builds = [n for n in ("pom.xml", "build.gradle", "build.gradle.kts") if (workspace / n).exists()]
    if java_builds:
        results["languages"].append("java")
        build_text = ""
        for name in java_builds:
            try:
                build_text += (workspace / name).read_text(encoding="utf-8", errors="replace").lower()
            except OSError:
                pass
        java_fw = []
        if "junit-jupiter" in build_text or "org.junit.jupiter" in build_text:
            java_fw.append("junit5")
        if "junit:junit" in build_text or re.search(r"<groupid>\s*junit\s*</groupid>", build_text):
            java_fw.append("junit4")
        if "testng" in build_text:
            java_fw.append("testng")
        if java_fw:
            results["frameworks"].extend(java_fw)
        else:
            results["frameworks"].append("java-unknown")
            results.setdefault("notes", []).append(
                "Java build found but no JUnit 5, JUnit 4, or TestNG dependency detected. "
                "Confirm the test framework from the build file before generating tests."
            )
        if (workspace / "pom.xml").exists():
            cmd = "./mvnw test" if (workspace / "mvnw").exists() else "mvn test"
        else:
            cmd = "./gradlew test" if (workspace / "gradlew").exists() else "gradle test"
        results["test_runners"].append(cmd)
        results["recommended_command"] = cmd

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
