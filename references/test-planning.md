# Test Planning & Discovery Guide

## 1. Codebase Analysis Checklist
When planning tests for a codebase, systematically inspect:
1. **Entry Points & Public Surfaces**: REST routes, CLI commands, exported library classes.
2. **Core Domain Logic**: Business rules, state machines, data validation, calculation engines.
3. **Data Transformations**: Parsing, serialization, schema migrations.
4. **Boundary & Edge Conditions**: Null inputs, empty collections, numerical limits, unexpected types.

## 2. Risk-Weighted Prioritization
Prioritize test generation based on risk factors:
- **High Risk (Priority 1)**: Financial transactions, authentication/authorization, data persistence, core business calculations.
- **Medium Risk (Priority 2)**: Complex data transformations, external integrations, utility helpers.
- **Low Risk (Priority 3)**: Simple getters/setters, purely declarative boilerplate, UI styling.

## 3. Entry & Exit Criteria
- **Entry Criteria**: Codebase compiles/parses, dependency manifests exist, target test directory is writable.
- **Exit Criteria**: All high-risk paths covered, no compilation errors in generated tests, 100% of generated tests pass or have verified defect diagnoses.
