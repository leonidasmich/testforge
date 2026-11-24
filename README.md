# TestForge — Autonomous Software Testing Skill for Claude Code

TestForge is an open-source [Agent Skill](https://code.claude.com/docs/en/skills) that guides Claude through a software-testing workflow. It inspects a codebase, writes a risk-weighted test plan, generates unit, integration, and end-to-end tests, runs the suite, classifies failures, and writes a Markdown report plus a JSON summary.

Instructions are split the way Agent Skills expect: `SKILL.md` holds the workflow, `references/` holds testing guidance loaded only when needed, and `scripts/` covers detection, the safety probe, and report parsing.

## Features

- Enforces the write boundary with a `PreToolUse` hook (`hooks/enforce_write_boundary.py`): Write/Edit outside `tests/`, `test/`, `__tests__/`, `spec/`, `src/test/`, `.testforge/`, test-named files, or the report files is rejected. Bash is checked best-effort only.
- Detects Python (pytest or unittest), JavaScript/TypeScript (Jest, Vitest, Playwright), and Maven or Gradle projects (JUnit 5, JUnit 4, TestNG).
- On syntax or import failures, the model may revise the generated test up to twice, using the heuristics in `references/test-validation.md`.
- Writes `TESTFORGE_REPORT.md` from `assets/TESTFORGE_REPORT_TEMPLATE.md` and `testforge-results.json` validated against `assets/testforge-results-schema.json`.

## Installation

Python 3.10 or newer is required. The scripts use the standard library only. JavaScript, TypeScript, and Java projects also need the test runner those projects already use (Node.js, Maven, or Gradle).

### Claude Code

Copy this folder to one of:

- `~/.claude/skills/testforge` for every project
- `<project>/.claude/skills/testforge` for one project

The folder must contain `SKILL.md`. Restart Claude Code, then ask it to use TestForge.

### Cursor

Copy this folder to one of:

- `~/.cursor/skills/testforge` for every project
- `<project>/.cursor/skills/testforge` for one project

Cursor reads skills from `.cursor/skills/`. A project copy belongs there, not under `.claude/skills/`.

## Usage

Ask in conversation:

- **Full audit** (default): "Run a TestForge test audit on this project."
- **Plan only**: "Use TestForge in plan mode to design a test suite."
- **Generate only**: "Use TestForge in generate mode and do not run the tests."

Plan mode writes `TESTFORGE_PLAN.md` and does not generate or run tests. Generate mode writes test files and does not run them. Audit mode runs discovery, planning, generation, execution, failure classification, and reporting.

## Repository layout

```
testforge/
├── SKILL.md
├── references/          # testing guidance, loaded on demand
├── scripts/             # framework detection, safety probe, result parsing
├── assets/              # report template and JSON schema
└── evals/evals.json     # scenario descriptions (no test runner)
```

## Safety

Before an audit, the workflow runs `scripts/validate_test_environment.py`. The probe checks that the workspace is writable and scans environment-variable names that look like environment, stage, or database settings. If a matching value looks like production, the script reports the variable name only and recommends plan mode.

That probe is a heuristic. It does not sandbox shell commands, block network access, or prove a database is disposable. Test commands still run in the project. `.testforge/` is where logs and intermediate JSON go. The write boundary is a hook, not a file-system lock: it blocks Write/Edit reliably, but Bash checking is a best-effort pattern match and a determined shell command can get around it. The hook is declared in `SKILL.md` frontmatter and active only while the skill runs; verify your Claude Code version honors skill-scoped hooks, or copy the hook into `settings.json`. Review generated tests before you commit them.

## Limitations

- Language coverage is Python, JavaScript/TypeScript, and Java. Java framework (JUnit 5, JUnit 4, TestNG) is inferred from the build file text; if none is found it reports `java-unknown`.
- `scripts/parse_test_results.py` understands JUnit XML and the text summaries from pytest, unittest, Jest, Vitest, Playwright, Maven, and Gradle. Other formats need `--junit-xml`. If parsing fails, the script exits with an error instead of writing an empty success report.
- Repair of generated tests is done by the model from `references/test-validation.md`. There is no repair script.
- `evals/evals.json` lists expected behaviors for two scenarios. Nothing in this repo executes those evals.

## Author

Leonidas Michalopoulos · [leonidasmich](https://github.com/leonidasmich) · [leom.gr](https://leom.gr) · info@leom.gr

## License

MIT. See [LICENSE](LICENSE).
