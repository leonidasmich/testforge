# TestForge Audit & Assessment Report

## Executive Summary
- **Execution Timestamp**: `{{TIMESTAMP}}`
- **Operating Mode**: `{{OPERATING_MODE}}`
- **Total Test Cases Executed**: `{{TOTAL_TESTS}}`
- **Passed**: `{{PASSED_TESTS}}` | **Failed**: `{{FAILED_TESTS}}` | **Skipped**: `{{SKIPPED_TESTS}}`
- **Overall Pass Rate**: `{{PASS_RATE}}%`

---

## 1. Codebase Discovery & Environment
- **Detected Languages**: `{{LANGUAGES}}`
- **Testing Frameworks**: `{{FRAMEWORKS}}`
- **Test Runner Command**: `{{COMMAND}}`
- **Safety Status**: `{{SAFETY_STATUS}}`

---

## 2. Testing Scope & Pyramid Distribution
| Test Level | Generated Count | Executed Count | Pass Rate |
| :--- | :--- | :--- | :--- |
| **Unit Tests** | {{UNIT_GEN}} | {{UNIT_EXEC}} | {{UNIT_PASS}}% |
| **Integration Tests** | {{INT_GEN}} | {{INT_EXEC}} | {{INT_PASS}}% |
| **End-to-End Tests** | {{E2E_GEN}} | {{E2E_EXEC}} | {{E2E_PASS}}% |

---

## 3. Detailed Failure Investigation & Defect Analysis

### Confirmed Implementation Defects
`{{CONFIRMED_DEFECTS_SECTION}}`

### Flaky / Non-Deterministic Tests
`{{FLAKY_TESTS_SECTION}}`

### Test Smells Identified
`{{TEST_SMELLS_SECTION}}`

---

## 4. Actionable Quality Recommendations
1. `{{RECOMMENDATION_1}}`
2. `{{RECOMMENDATION_2}}`
3. `{{RECOMMENDATION_3}}`
