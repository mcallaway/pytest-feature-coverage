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
- [ADR-004: Apply the `--feature-coverage-filter` at Report Time, Not Load Time](004-apply-coverage-filter-at-report-time.md) — why the filter is applied in `_compute_and_store_report()` rather than at load time, and why no INI option was added
- [ADR-005: Support Python >=3.11 While Developing on 3.14](005-support-python-311-develop-on-314.md) — declare a 3.11 install floor; keep local/publish on 3.14; type-check and CI against the floor
- [ADR-006: Define "Covering Test" as Execution-Aware, Not Collection-Time](006-execution-aware-covering-test.md) — amends ADR-003 Layer 2: coverage requires a clean pass, not mere collection; documents the xpass policy
