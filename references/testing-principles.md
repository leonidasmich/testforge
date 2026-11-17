# Core Testing Principles & Methodology

## 1. The Test Pyramid & Granularity
The Test Pyramid (Cohn, Fowler, Google SWE) balances execution speed, isolation, and fidelity:

1. **Unit Tests (Base / ~70%)**:
   - Fast, isolated, deterministic checks of individual functions, classes, or modules.
   - Rely on test doubles (Fakes/Stubs) for external dependencies (databases, network).
2. **Integration Tests (Middle / ~20%)**:
   - Verify interaction between internal modules and external boundaries (e.g., DB repositories, file systems, internal APIs).
   - Focus on subcutaneous testing (testing below the UI layer through service APIs).
3. **End-to-End / UI Tests (Top / ~10%)**:
   - Broad-stack validation of critical user journeys.
   - Slower and more brittle; kept focused on primary golden paths.

## 2. Google Software Engineering Testing Practices
- **The Beyoncé Rule**: "If you liked it, then you shoulda put a test on it." Un-tested behavior is unsupported behavior.
- **Test State, Not Interactions**: Prefer verifying output values and state changes over verifying that specific internal methods were called.
- **Test Public APIs**: Test through public package interfaces rather than private internal implementation details.
- **DAMP over DRY**: Tests should be *Descriptive And Meaningful Phrases*. Favor clarity and self-contained readability over aggressive code deduplication in test suites.

## 3. ISTQB Testing Principles
- **Early Testing (Shift-Left)**: Static analysis and test design should begin as early as possible in the lifecycle to catch defects when repair cost is lowest.
- **Pesticide Paradox**: Repeatedly running the same static tests won't find new defects; test sets must evolve alongside software changes.
- **Defect Clustering**: A small module subset typically contains the majority of operational defects.

## 4. Structural Test Patterns
All generated tests MUST follow the **Arrange-Act-Assert (AAA)** or **Given-When-Then** structure:
- **Arrange (Given)**: Set up preconditions, test data, and state.
- **Act (When)**: Invoke the specific target method or trigger the action.
- **Assert (Then)**: Verify observable state changes and return values using clear assertions.
