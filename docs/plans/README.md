# Plans -- Project Roadmap

- **Purpose**: GPS dashboard showing active, upcoming, and completed work. This is a roadmap index, not a place for individual plan files -- those live in `.specify/specs/NNN/plan.md`.
- **TTL**: short (updated each session that changes what's active).
- **Author(s)**: Updated every session that touches the active plan.
- **Audience(s)**: Fresh agent sessions resuming work; humans tracking progress.

See `RUBRIC.md` in this folder for criteria applied to Spec Kit plans via the `after_plan` hook.

## Current Focus

<!-- No active plan-level work at the moment. -->

## Next Steps

<!-- Upcoming work -->

## Completed

- **002-execution-aware-coverage**: Make `--feature-coverage` execution-aware -- a requirement is covered only when at least one associated test passes, not merely collected. [Plan](002-execution-aware-coverage.md) | [Spec](../../specs/002-execution-aware-coverage/spec.md) -- Closed 2026-09-29 (PR [#29](https://github.com/bayer-int/pytest-feature-coverage/pull/29))
- **w29-coverage-filter**: `--feature-coverage-filter` CLI option — narrows coverage report to features matching a substring. [Plan](.../../.specify/specs/w29-coverage-filter/plan.md) | [Spec](../../.specify/specs/w29-coverage-filter/spec.md) — Closed 2026-07-18
- **001-feature-coverage-plugin**: pytest plugin for requirement-to-test coverage tracking. [Plan](../../specs/001-feature-coverage-plugin/plan.md) | [Spec](../../specs/001-feature-coverage-plugin/spec.md) — Closed 2025-05-20
