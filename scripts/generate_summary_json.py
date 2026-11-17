#!/usr/bin/env python3
"""
generate_summary_json.py — Compiles parsed test results and metadata into final
schema-compliant testforge-results.json report.
"""

import json
import sys
import time

def generate_summary(parsed_json_path: str, output_path: str):
    try:
        with open(parsed_json_path, "r", encoding="utf-8") as f:
            parsed = json.load(f)
    except Exception:
        parsed = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "test_cases": []}

    report = {
        "testforge_version": "1.0.0",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "summary": {
            "total_tests": parsed.get("total", 0),
            "passed_tests": parsed.get("passed", 0),
            "failed_tests": parsed.get("failed", 0),
            "skipped_tests": parsed.get("skipped", 0),
            "pass_rate_percentage": (parsed.get("passed", 0) / max(1, parsed.get("total", 1))) * 100.0
        },
        "test_cases": parsed.get("test_cases", []),
        "defects_identified": [
            tc for tc in parsed.get("test_cases", []) if tc.get("status") in ["failed", "error"]
        ]
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Summary JSON report successfully generated at {output_path}")

def main():
    parsed_path = ".testforge/parsed_results.json"
    out_path = "testforge-results.json"
    
    if "--parsed-json" in sys.argv:
        parsed_path = sys.argv[sys.argv.index("--parsed-json") + 1]
    if "--out" in sys.argv:
        out_path = sys.argv[sys.argv.index("--out") + 1]

    generate_summary(parsed_path, out_path)

if __name__ == "__main__":
    main()
