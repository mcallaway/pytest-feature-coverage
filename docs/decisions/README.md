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

<!-- Add ADR entries here as they are created -->
