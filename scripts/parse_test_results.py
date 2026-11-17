#!/usr/bin/env python3
"""
parse_test_results.py — Parse JUnit XML or common runner text logs into a
shared result object.

Supported text logs: pytest, unittest, Jest, Vitest, Playwright, Maven, Gradle.
Unknown text exits with an error and does not write a zero-test success file.
"""

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def _case(name, status, classname="", duration=0.0, error_message=None):
    return {
        "name": name,
        "classname": classname,
        "status": status,
        "duration_seconds": duration,
        "error_message": error_message,
    }


def _result(total, passed, failed, skipped, cases):
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "test_cases": cases,
    }


def _int_attr(elem, name):
    try:
        return int(float(elem.attrib.get(name, 0)))
    except (TypeError, ValueError):
        return 0


def parse_junit_xml(xml_path: str) -> dict:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    if _int_attr(root, "tests"):
        total = _int_attr(root, "tests")
        failures = _int_attr(root, "failures")
        errors = _int_attr(root, "errors")
        skipped = _int_attr(root, "skipped")
    else:
        suites = root.findall("testsuite") or [root]
        total = failures = errors = skipped = 0
        for suite in suites:
            total += _int_attr(suite, "tests")
            failures += _int_attr(suite, "failures")
            errors += _int_attr(suite, "errors")
            skipped += _int_attr(suite, "skipped")

    passed = total - (failures + errors + skipped)
    cases = []
    for testcase in root.iter("testcase"):
        name = testcase.attrib.get("name", "unknown")
        classname = testcase.attrib.get("classname", "")
        try:
            time_sec = float(testcase.attrib.get("time", 0.0))
        except (TypeError, ValueError):
            time_sec = 0.0

        status = "passed"
        failure_msg = None
        failure = testcase.find("failure")
        error = testcase.find("error")
        if failure is not None:
            status = "failed"
            failure_msg = failure.get("message") or failure.text
        elif error is not None:
            status = "error"
            failure_msg = error.get("message") or error.text
        elif testcase.find("skipped") is not None:
            status = "skipped"

        cases.append(_case(name, status, classname, time_sec, failure_msg))

    if total == 0 and cases:
        total = len(cases)
        passed = sum(1 for case in cases if case["status"] == "passed")
        failed = sum(1 for case in cases if case["status"] in ("failed", "error"))
        skipped = sum(1 for case in cases if case["status"] == "skipped")
        return _result(total, passed, failed, skipped, cases)

    return _result(total, passed, failures + errors, skipped, cases)


_PYTEST_SUMMARY = re.compile(r"=+\s*(.+?)\s+in\s+[\d.]+s\s*=+")
_COUNT_WORD = re.compile(
    r"(\d+)\s+(passed|failed|errors?|skipped|xfailed|xpassed)\b",
    re.IGNORECASE,
)
_PYTEST_VERBOSE = re.compile(
    r"^(\S+::\S+)\s+(PASSED|FAILED|ERROR|SKIPPED)\b",
    re.MULTILINE,
)
_PYTEST_SHORT = re.compile(
    r"^(FAILED|ERROR|SKIPPED)\s+(\S+?)(?:\s+-\s+(.*))?$",
    re.MULTILINE,
)
_UNITTEST_RAN = re.compile(r"^Ran (\d+) tests? in ", re.MULTILINE)
_UNITTEST_FAILED = re.compile(r"^FAILED \((.+)\)", re.MULTILINE)
_JEST_TESTS = re.compile(r"^Tests:\s+(.+)$", re.MULTILINE)
_VITEST_TESTS = re.compile(r"^\s*Tests\s{2,}(.+)$", re.MULTILINE)
_PLAYWRIGHT_COUNT = re.compile(
    r"^\s{2,}(\d+)\s+(passed|failed|flaky|skipped)\b",
    re.MULTILINE | re.IGNORECASE,
)
_SUREFIRE = re.compile(
    r"Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+),\s*Skipped:\s*(\d+)"
)
_SUREFIRE_FAILURE = re.compile(
    r"^\[(?:ERROR|FAILURE)\]\s+(\S+\.\S+?)(?::\d+)?(?:\s+(.*))?$",
    re.MULTILINE,
)


def _status_from_label(label):
    label = label.lower()
    if label in ("failed", "failure"):
        return "failed"
    if label in ("error", "errors"):
        return "error"
    if label in ("skipped", "skip"):
        return "skipped"
    return "passed"


def _counts_from_words(text):
    counts = {}
    for match in _COUNT_WORD.finditer(text):
        counts[match.group(2).lower()] = int(match.group(1))
    return counts


def _bucket_counts(counts):
    passed = counts.get("passed", 0) + counts.get("xpassed", 0)
    failed = counts.get("failed", 0) + counts.get("error", 0) + counts.get("errors", 0)
    skipped = counts.get("skipped", 0) + counts.get("xfailed", 0)
    return passed, failed, skipped


def _parse_pytest(text):
    summaries = list(_PYTEST_SUMMARY.finditer(text))
    if not summaries:
        return _parse_unittest(text)

    passed, failed, skipped = _bucket_counts(_counts_from_words(summaries[-1].group(1)))
    cases = []
    seen = set()
    for match in _PYTEST_VERBOSE.finditer(text):
        name = match.group(1)
        if name in seen:
            continue
        seen.add(name)
        cases.append(_case(name, _status_from_label(match.group(2))))

    if not cases:
        for match in _PYTEST_SHORT.finditer(text):
            name = match.group(2)
            if name in seen:
                continue
            seen.add(name)
            message = match.group(3).strip() if match.group(3) else None
            cases.append(_case(name, _status_from_label(match.group(1)), error_message=message))

    total = passed + failed + skipped
    if total == 0 and not cases:
        return None
    if total == 0:
        passed = sum(1 for case in cases if case["status"] == "passed")
        failed = sum(1 for case in cases if case["status"] in ("failed", "error"))
        skipped = sum(1 for case in cases if case["status"] == "skipped")
        total = len(cases)
    return _result(total, passed, failed, skipped, cases)


def _parse_unittest(text):
    ran = _UNITTEST_RAN.search(text)
    if not ran:
        return None
    total = int(ran.group(1))
    failed = errors = skipped = 0
    failed_line = _UNITTEST_FAILED.search(text)
    if failed_line:
        details = failed_line.group(1)
        for label, target in (
            ("failures", "failed"),
            ("errors", "errors"),
            ("skipped", "skipped"),
        ):
            match = re.search(rf"{label}=(\d+)", details)
            if not match:
                continue
            count = int(match.group(1))
            if target == "failed":
                failed = count
            elif target == "errors":
                errors = count
            else:
                skipped = count
    passed = max(0, total - failed - errors - skipped)
    return _result(total, passed, failed + errors, skipped, [])


def _parse_js(text, runner):
    jest_lines = list(_JEST_TESTS.finditer(text))
    vitest_lines = list(_VITEST_TESTS.finditer(text))
    counts = None
    if jest_lines and "vitest" not in runner:
        counts = _counts_from_words(jest_lines[-1].group(1))
    elif vitest_lines:
        counts = _counts_from_words(vitest_lines[-1].group(1))
    elif jest_lines:
        counts = _counts_from_words(jest_lines[-1].group(1))

    cases = []
    if counts is not None:
        passed, failed, skipped = _bucket_counts(counts)
        if "total" in counts:
            total = counts["total"]
        else:
            total = passed + failed + skipped
        for match in re.finditer(r"^[\s●]*[●×]\s+(.+)$", text, re.MULTILINE):
            cases.append(_case(match.group(1).strip(), "failed"))
        if total == 0 and not cases:
            return None
        return _result(total, passed, failed, skipped, cases)

    if "playwright" in runner or _PLAYWRIGHT_COUNT.search(text):
        pw_counts = {}
        for match in _PLAYWRIGHT_COUNT.finditer(text):
            pw_counts[match.group(2).lower()] = int(match.group(1))
        if not pw_counts:
            return None
        passed = pw_counts.get("passed", 0)
        failed = pw_counts.get("failed", 0) + pw_counts.get("flaky", 0)
        skipped = pw_counts.get("skipped", 0)
        return _result(passed + failed + skipped, passed, failed, skipped, cases)

    return None


def _parse_surefire(text):
    runs = list(_SUREFIRE.finditer(text))
    if not runs:
        return None
    results_at = text.rfind("Results:")
    chosen = None
    if results_at >= 0:
        for match in runs:
            if match.start() > results_at:
                chosen = match
                break
    if chosen is None:
        chosen = runs[-1]
    total, failures, errors, skipped = (int(chosen.group(i)) for i in range(1, 5))
    passed = max(0, total - failures - errors - skipped)
    cases = []
    for match in _SUREFIRE_FAILURE.finditer(text):
        message = match.group(2).strip() if match.group(2) else None
        cases.append(_case(match.group(1), "failed", error_message=message))
    return _result(total, passed, failures + errors, skipped, cases)


def parse_raw_log(log_path: str, runner: str) -> dict:
    text = Path(log_path).read_text(encoding="utf-8", errors="replace")
    stripped = text.lstrip()
    if stripped.startswith(("<?xml", "<testsuites", "<testsuite")):
        return parse_junit_xml(log_path)

    runner_key = (runner or "").lower()
    parsed = None
    if any(token in runner_key for token in ("pytest", "unittest", "py.test")):
        parsed = _parse_pytest(text)
    elif any(token in runner_key for token in ("jest", "vitest", "playwright", "npm", "npx")):
        parsed = _parse_js(text, runner_key)
    elif any(token in runner_key for token in ("mvn", "maven", "gradle", "junit")):
        parsed = _parse_surefire(text)
    else:
        for attempt in (
            lambda: _parse_pytest(text),
            lambda: _parse_js(text, runner_key),
            lambda: _parse_surefire(text),
        ):
            parsed = attempt()
            if parsed is not None:
                break

    if parsed is None:
        raise ValueError(
            "Could not parse test results from the log. "
            "Re-run the suite with a JUnit XML report and pass --junit-xml."
        )
    return parsed


def _arg(flag):
    if flag not in sys.argv:
        return None
    index = sys.argv.index(flag)
    if index + 1 >= len(sys.argv):
        raise ValueError(f"Missing value for {flag}")
    return sys.argv[index + 1]


def main():
    usage = (
        "Usage: parse_test_results.py --junit-xml <path> --out <out.json>\n"
        "       parse_test_results.py --raw-log <path> --runner <runner> --out <out.json>"
    )
    if "--junit-xml" not in sys.argv and "--raw-log" not in sys.argv:
        print(usage, file=sys.stderr)
        sys.exit(1)

    out_path = _arg("--out") or "parsed_results.json"
    try:
        if "--junit-xml" in sys.argv:
            results = parse_junit_xml(_arg("--junit-xml"))
        else:
            results = parse_raw_log(_arg("--raw-log"), _arg("--runner") or "")
    except (ValueError, FileNotFoundError, ET.ParseError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)
    print(f"Results successfully parsed to {out_path}")


if __name__ == "__main__":
    main()
