# Integration & Subcutaneous Testing Guidelines

## 1. Subcutaneous Testing Pattern
Subcutaneous testing exercises application functionality just below the graphical UI, connecting controllers, services, repositories, and local databases:
- Fast feedback compared to full browser tests.
- High confidence in end-to-end data flow and SQL/ORM query accuracy.

## 2. Database Integration Rules
- Use disposable, isolated databases (e.g., SQLite in-memory, Testcontainers, or transactional rollback fixtures).
- Ensure each test seeds its own minimal required state and cleans up upon teardown.
- Avoid shared global database state across parallel test threads.

## 3. Consumer-Driven Contract Testing (CDC)
When integrating with external microservices:
- Stub external network calls using tools like `responses` (Python), `msw` (JS/TS), or `WireMock` (Java).
- Verify request paths, headers, and payload structures match external service contracts.
