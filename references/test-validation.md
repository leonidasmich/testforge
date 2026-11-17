# Test Validation & Post-Processing Heuristics

Derived from empirical research (TestPilot / Schafer et al., Siddiq et al.):

## 1. Automated Post-Processing Heuristics
Before executing newly generated LLM tests, automatically clean common syntactic/formatting issues:
- **H1**: Strip natural language markdown explanations outside code blocks.
- **H2**: Remove duplicate package/import declarations.
- **H3**: Fix unclosed braces, brackets, and parentheses at file boundaries.
- **H4**: Correct invalid integer constants exceeding language bounds.
- **H5**: Remove trailing incomplete test method signatures resulting from token truncation.

## 2. Adaptive Failure-Driven Retry Loop
When a generated test fails execution:
1. Extract exact failure traceback, line number, and error message.
2. Re-prompt LLM with failing test snippet + execution error context.
3. Re-validate syntax and execute again.
4. Empirical studies demonstrate this adaptive feedback loop successfully repairs 15–20% of initial test failures.
