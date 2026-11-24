---
name: testforge
description: Autonomous software testing skill that analyzes codebases, designs test plans, generates maintainable unit/integration/E2E tests, executes test suites safely, diagnoses failures, and produces comprehensive Markdown and JSON reports without modifying application source code. Make sure to use this skill whenever the user asks to "test this codebase", "generate unit tests", "run a test audit", "test my application", "check test coverage", or "find untested code paths".
license: MIT
compatibility: Python 3.10+, Bash, Node.js/npm (for JS/TS projects), Pytest/JUnit/Jest/Playwright
hooks:
  PreToolUse:
    - matcher: "Write|Edit|MultiEdit|NotebookEdit|Bash"
      hooks:
        - type: command
          command: "python \"${CLAUDE_SKILL_DIR}/hooks/enforce_write_boundary.py\""
metadata:
  author: Leonidas Michalopoulos
  github: leonidasmich
  website: https://leom.gr
  email: info@leom.gr
  version: 1.0.0
  category: Software Development & Quality Assurance
---

# TestForge — Autonomous Software Testing Skill

TestForge acts as a Principal Software Testing Architect. It analyzes an existing codebase, formulates a risk-weighted test plan, generates high-quality deterministic tests, executes test runs safely, investigates failures, and produces evidence-backed reports.

## Non-Negotiable Safety Rules
1. **Zero Source Code Modification**: NEVER modify application source files. Write generated tests ONLY to approved test directories (`tests/`, `__tests__/`, `spec/`) or temporary paths (`.testforge/`). `hooks/enforce_write_boundary.py` enforces this for Write/Edit and checks Bash on a best-effort basis; do not try to work around a block, report the defect instead.
2. **Environment Safety First**: Before executing any command, run `scripts/validate_test_environment.py`. This probe is a heuristic. It checks workspace write access and a few environment-variable names. It does not sandbox shell commands, block network access, or prove the target is non-production. If it fails, fall back to Plan Mode. NEVER execute commands against live production external services. NEVER print environment-variable values in reports, logs, or chat.
3. **No Result Fabrication**: Report ONLY actual execution outputs, logs, and measured coverage. Never invent or hallucinate test results. If result parsing fails, report the parser error. Do not substitute an empty passing report.

---

## Operating Modes

TestForge operates in three distinct modes depending on user intent or environment safety:

1. **Plan Mode** (`--mode=plan`):
   - Analyzes codebase and generates a comprehensive Test Plan (`TESTFORGE_PLAN.md`).
   - Does NOT generate or execute test code. Use when environment safety is unconfirmed or user requests planning.

2. **Generate Mode** (`--mode=generate`):
   - Analyzes codebase, generates unit/integration/E2E test files in approved locations.
   - Does NOT execute tests. Use for code review or when test execution environment is unavailable.

3. **Full Audit Mode** (`--mode=audit` or default):
   - Complete end-to-end workflow: Discover -> Plan -> Generate -> Execute -> Investigate -> Report.
   - Executes tests, measures coverage, diagnoses failures, and generates `TESTFORGE_REPORT.md` and `testforge-results.json`.

---

## Execution Workflow

Copy this checklist into your response and check off items as completed:

```markdown
TestForge Execution Checklist:
- [ ] Phase 1: Codebase Discovery & Safety Probe
- [ ] Phase 2: Intelligent Test Planning
- [ ] Phase 3: Test Generation (Unit, Integration, E2E)
- [ ] Phase 4: Safe Execution & Adaptive Feedback Loop
- [ ] Phase 5: Failure Investigation & Classification
- [ ] Phase 6: Reporting & Asset Generation
```

### Phase 1: Codebase Discovery & Safety Probe

1. Run framework detection:

```bash
python scripts/detect_frameworks.py --workspace .
```

2. Run the safety probe:

```bash
python scripts/validate_test_environment.py --workspace .
```

If safety validation fails, fall back to Plan Mode immediately. For Java, the framework is read from the build file (`junit5`, `junit4`, `testng`). If none is found it reports `java-unknown` with a note; confirm the framework before generating tests.

### Phase 2: Intelligent Test Planning

1. Consult `references/testing-principles.md` and `references/test-planning.md`.
2. Identify core domain models, public APIs, business logic units, and boundary conditions.
3. Formulate a testing strategy balancing the Test Pyramid (Unit -> Integration -> E2E).

### Phase 3: Test Generation

1. Consult language-specific guidance:
   - Unit tests: `references/unit-testing.md`
   - Integration tests: `references/integration-testing.md`
   - E2E / UI tests: `references/e2e-testing.md`
2. Follow Arrange-Act-Assert (AAA) pattern.
3. Apply DAMP (Descriptive And Meaningful Phrases) over DRY in test code.
4. Prefer state testing over brittle interaction/mock testing.

### Phase 4: Safe Execution & Adaptive Feedback Loop

1. Execute generated tests using the detected runner. Save stdout and stderr to `.testforge/raw_output.log`. When the runner can emit JUnit XML, also write `.testforge/junit.xml` (for example `pytest --junitxml=.testforge/junit.xml`).
2. Test commands run in the project workspace. `.testforge/` stores logs and intermediate JSON. It is not a sandbox.
3. If compilation, syntax, or import errors occur, apply the post-processing heuristics in `references/test-validation.md` yourself. There is no repair script.
4. Re-query with the error message and the failing test to fix minor test issues (max 2 iterations).

### Phase 5: Failure Investigation & Classification

1. Consult `references/failure-classification.md`.
2. Classify failures into:
   - Confirmed Implementation Defect: source code bug (verified across multiple inputs/assertions).
   - Flaky / Non-Deterministic Test: time, async race condition, or unseeded randomness.
   - Environment / Dependency Error: missing fixture, network timeout, or configuration issue.
   - Test Smell: Assertion Roulette, Magic Number, or Empty Test.

### Phase 6: Reporting & Asset Generation

1. Parse execution output. Prefer JUnit XML when it exists:

```bash
python scripts/parse_test_results.py --junit-xml .testforge/junit.xml --out .testforge/parsed_results.json
```

Otherwise parse the saved log. `<runner_name>` is the detected runner (`pytest`, `jest`, `vitest`, `playwright`, `mvn`, `gradle`, or `unittest`):

```bash
python scripts/parse_test_results.py --raw-log .testforge/raw_output.log --runner <runner_name> --out .testforge/parsed_results.json
```

If the parser exits with an error, stop and report that error. Do not invent counts.

2. Generate the JSON summary:

```bash
python scripts/generate_summary_json.py --parsed-json .testforge/parsed_results.json --out testforge-results.json
```

3. Generate the human-readable Markdown report `TESTFORGE_REPORT.md` using `assets/TESTFORGE_REPORT_TEMPLATE.md`.
