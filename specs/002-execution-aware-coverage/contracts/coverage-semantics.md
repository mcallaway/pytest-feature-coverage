# Coverage Semantics Contract: What "Covering Test" Means

**Date**: 2026-09-29\
**Type**: Behavioral contract (no CLI/INI surface change; see [specs/001-feature-coverage-plugin/contracts/cli.md](../../001-feature-coverage-plugin/contracts/cli.md) for the unchanged CLI/INI/exit-code contract)

This document is the authoritative definition of when a test counts toward requirement coverage. It supersedes the informal pre-existing behavior ("any collected node ID with a matching `req()` marker counts") with the execution-aware definition below. See [ADR-006](../../../docs/decisions/006-execution-aware-covering-test.md) for the rationale.

## Outcome Table

| Test outcome                          | Counts as coverage |
| ------------------------------------- | ------------------ |
| Passed                                | Yes                |
| Failed                                | No                 |
| Skipped                               | No                 |
| Expected failure (`xfail`)            | No                 |
| Setup or teardown error               | No                 |
| Unexpected pass (`xpass`, non-strict) | No                 |
| Deselected or not run                 | No                 |

## Rules

1. A requirement is covered if and only if at least one of its associated node IDs (per `req()` markers, unchanged from today) achieved a clean pass, per the table above.
1. When multiple node IDs are associated with the same requirement, one clean pass is sufficient; the outcome of other associated node IDs does not affect coverage for that requirement.
1. Each parametrized test case has its own node ID (e.g. `test_f[case-1]`, `test_f[case-2]`) and its own outcome; the rule above applies per node ID, not per test function.
1. Reports (text, JSON, Markdown) list only the node IDs that supplied a clean pass as covering evidence for a requirement. A node ID that was merely collected and associated, but did not pass, never appears in a requirement's covering-test list.
1. Collection-time behavior is unaffected by this contract: orphan `req()` marker detection and `feature_coverage_strict` continue to evaluate purely on requirement-ID association, independent of runtime outcome.
1. `--feature-coverage-min` is evaluated against coverage computed per rules 1-2 above, not against collection-time association counts.

## Non-Changes (explicitly out of scope)

- `req()` marker syntax and feature YAML schema are unchanged.
- `--feature-coverage`, `--feature-coverage-format`, `--feature-coverage-min`, `--feature-coverage-filter`, `feature_yaml_paths`, `feature_coverage_min`, `feature_coverage_strict` INI/CLI options are unchanged.
- Exit code table in `specs/001-feature-coverage-plugin/contracts/cli.md` is unchanged; only the *coverage percentage* feeding into that table's threshold check is computed differently.
