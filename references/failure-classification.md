# Failure Investigation & Classification Taxonomy

When a test fails, classify the root cause using the following taxonomy:

## 1. Confirmed Implementation Defect
- **Definition**: The test correctly reflects requirements, but the application source code returns incorrect output or throws an unhandled exception.
- **Verification Rule**: Must be verified with multiple input variations or assertions before flagging as a confirmed defect.

## 2. Flaky / Non-Deterministic Test
- **Definition**: Test passes intermittently due to time dependencies, unseeded random number generators, or async race conditions.
- **Eradication**: Inject fixed seeds, freeze system clocks (using `freezegun` or `time-machine`), or use web-first polling.

## 3. Environment & Configuration Failure
- **Definition**: Test fails due to missing environment variables, missing local database fixtures, or port conflicts.

## 4. Test Smell Identification
- **Assertion Roulette**: A test function contains multiple un-documented assertions making it unclear which condition failed.
- **Magic Number Test**: Raw unexplained numeric literals in assertions without named constants or context.
- **Empty Test**: A test function with no assertions or assertions that always evaluate to true (`assert True`).
