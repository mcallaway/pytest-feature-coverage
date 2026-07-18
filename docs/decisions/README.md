# Architecture Decision Records

- **Purpose**: Point-in-time records of hard-to-reverse decisions with context and rejected alternatives. Once accepted, the record is immutable (amend with a new ADR that supersedes).
- **TTL**: immutable -- the record never changes; the decision may be superseded.
- **Author(s)**: Humans (with agent assistance) when a trade-off is encountered during implementation.
- **Audience(s)**: Anyone understanding constraints; future agents picking up adjacent work; reviewers.

See `RUBRIC.md` in this folder for the criteria an ADR must meet.

## ADR Format

- **Title**: Short imperative statement (e.g., "Use SQLite for local storage")
- **Status**: Proposed | Accepted | Deprecated | Superseded by ADR-NNN
- **Date**: ISO 8601 (YYYY-MM-DD)
- **Context**: What prompted the decision
- **Decision**: What was decided (imperative mood)
- **Consequences**: Both positive and negative effects

## Index

- [ADR-001: Create a Standalone pytest Plugin for Requirement Traceability](001-standalone-plugin-for-requirement-traceability.md) — why a dedicated plugin rather than template-embedded logic
- [ADR-002: Plugin Hook Coverage Strategy](002-plugin-hook-coverage-strategy.md) — how to achieve honest coverage on a pytest plugin that is itself loaded by pytest
- [ADR-003: What "Tested" Means in This Project](003-what-tested-means.md) — layered definition of done: execution coverage, feature coverage, structural review, and mutation testing
