# Implementation Plan: w29 — `--feature-coverage-filter`

**Status**: COMPLETE | **Branch**: `feat/w29-coverage-filter` | **Date**: 2026-07-18 | **Closed**: 2026-07-18 | **Spec**: [spec.md](spec.md)\
**Input**: Feature specification from `.specify/specs/w29-coverage-filter/spec.md`

______________________________________________________________________

## Summary

Add a repeatable `--feature-coverage-filter TEXT` CLI option to the pytest-feature-coverage plugin that narrows the coverage report to features whose name contains `TEXT` (case-insensitive, OR semantics). The filter is applied by slicing the feature list _before_ `compute_coverage()` is called in `_compute_and_store_report()`; the full feature list is preserved in plugin state so orphan `req()` detection is unaffected. No changes to `matrix.py`, `schema.py`, `scanner.py`, or any reporter file. Total new production code: ~15 lines in `plugin.py`.

______________________________________________________________________

## Technical Context

**Language/Version**: Python 3.11+ (as declared in `pyproject.toml`)\
**Primary Dependencies**: pytest (≥8), pydantic, PyYAML — no new dependencies\
**Storage**: N/A — stateless per session\
**Testing**: pytest + pytester fixture for integration tests\
**Target Platform**: Any platform running Python 3.11+\
**Project Type**: pytest plugin library\
**Performance Goals**: Filter is a list comprehension over ≤100 features — negligible overhead\
**Constraints**: No runtime dependencies beyond pytest, pydantic, and PyYAML (constitution rule)\
**Scale/Scope**: Single function change in `plugin.py` + one new unit test file + one new integration test

______________________________________________________________________

## Constitution Check

_Re-verified after Phase 1 design._

| Gate                                     | Status  | Notes                                                                      |
| ---------------------------------------- | ------- | -------------------------------------------------------------------------- |
| Simplest approach chosen                 | ✅ PASS | List comprehension in `_compute_and_store_report()`; no new abstractions   |
| No new runtime dependencies              | ✅ PASS | Pure stdlib string methods (`str.lower`, `in`)                             |
| TDD mandatory                            | ✅ PASS | 9 unit tests + 1 integration test specified before implementation          |
| No mocks in acceptance/integration tests | ✅ PASS | Integration test uses real pytester fixtures                               |
| Names describe what things ARE           | ✅ PASS | `lower_filters`, `features` (filtered local), `state['features']` (full)   |
| Reduce duplication                       | ✅ PASS | Reuses `compute_coverage()` unchanged; reporters require zero changes      |
| No INI option added                      | ✅ PASS | Spec explicitly forbids it; filter is session-specific, not project config |

No violations. Complexity tracking section not needed.

______________________________________________________________________

## Project Structure

### Documentation (this feature)

```text
.specify/specs/w29-coverage-filter/
├── plan.md              ← this file
├── research.md          ← Phase 0 (confirms no open questions)
├── data-model.md        ← Phase 1 (no new entities; documents filter interaction)
├── quickstart.md        ← Phase 1 (usage examples for the new option)
├── contracts/
│   └── cli-options.md   ← Phase 1 (new CLI option contract)
└── tasks.md             ← Phase 2 (/speckit.tasks — NOT created here)
```

### Source Changes (repository root)

```text
src/pytest_feature_coverage/
└── plugin.py                              MODIFY: addoption() + _compute_and_store_report()

tests/unit/
└── test_filter.py                         CREATE: 9 unit test cases

tests/integration/
└── test_coverage_filter.py                CREATE: CLI help + filtered output integration test

features/
└── 001-feature-coverage-plugin.feature.yaml   already updated (COVERAGE_FILTER component present)

docs/plans/README.md                       MODIFY: point Current Focus to this plan
.github/copilot-instructions.md            MODIFY: SPECKIT marker points to this plan
```

**Structure Decision**: Single-project layout. All changes confined to `plugin.py` and new test files. No module refactoring required.

______________________________________________________________________

## Phase 0 — Research

> All design questions were resolved during specification (session 2026-07-18, `tmp/w29-feature-coverage-filter.md`). No open unknowns. `research.md` captures key decisions for future reference.

See [`research.md`](research.md).

______________________________________________________________________

## Phase 1 — Design & Contracts

No new persistent entities. The filter operates as a transient local slice of `state['features']`. See [`data-model.md`](data-model.md) and [`contracts/cli-options.md`](contracts/cli-options.md).

Usage examples: [`quickstart.md`](quickstart.md).

______________________________________________________________________

## Implementation Guide

### 1 — `plugin.py :: pytest_addoption()`

Add after the existing `--feature-coverage-min` option in `pytest_addoption()`:

```python
group.addoption(
    '--feature-coverage-filter',
    action='append',
    default=None,
    metavar='TEXT',
    help=(
        'Only show features whose name contains TEXT (case-insensitive). '
        'Repeatable; multiple values combine as OR. Default: show all features.'
    ),
)
```

### 2 — `plugin.py :: _compute_and_store_report()`

After `features = state['features']`, insert the filter block:

```python
features = state['features']          # full list — never mutated; used by orphan check

filters = config.getoption('--feature-coverage-filter') or []
if filters:
    lower_filters = [f.lower() for f in filters]
    features = [
        ff for ff in features
        if any(lf in ff.feature.name.lower() for lf in lower_filters)
    ]
```

The local `features` shadows the full list only within this call. `compute_coverage()` receives the filtered slice; all downstream work (reporters, threshold, `coverage_percentage`) is naturally scoped to that slice. `_get_known_requirement_ids()` reads `state['features']` directly and is unaffected.

### 3 — Nothing else changes

`matrix.py`, `schema.py`, `scanner.py`, and all reporter files require zero modifications.

______________________________________________________________________

## Test Plan

### `tests/unit/test_filter.py` (new — 9 cases)

All tests call `_compute_and_store_report()` via a fake `config` stub (same pattern as `tests/unit/test_plugin.py`).

| #   | Test name                                       | Assertion                                                                         |
| --- | ----------------------------------------------- | --------------------------------------------------------------------------------- |
| 1   | `test_single_filter_exact_match`                | Only the matching feature appears in `report.features`                            |
| 2   | `test_single_filter_substring_match`            | All features whose name contains the substring are included                       |
| 3   | `test_multiple_filters_or_semantics`            | Feature matching either filter is included                                        |
| 4   | `test_filter_case_insensitive`                  | Uppercase filter matches lowercase feature name                                   |
| 5   | `test_filter_zero_matches_empty_report`         | `report.features == []`; Overall counts 0/0                                       |
| 6   | `test_no_filter_all_features_shown`             | With `filters=None`, all features pass through unchanged                          |
| 7   | `test_overall_percentage_uses_filtered_set`     | `coverage_percentage` counts only filtered features' requirements                 |
| 8   | `test_orphan_markers_unaffected_by_filter`      | `report.orphan_markers` contains the orphan even when its feature is filtered out |
| 9   | `test_threshold_evaluated_against_filtered_set` | `pytest_sessionfinish` sets `exitstatus=2` when filtered coverage is below min    |

### `tests/integration/test_coverage_filter.py` (new — 2 cases)

Uses `pytester` fixture (real subprocess). Reuse fixture YAML files from `tests/data/` where possible.

| #   | Test name                                             | Assertion                                                                                                                |
| --- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| 1   | `test_help_shows_filter_option`                       | `--feature-coverage-filter` with its description appears in `pytest --help` output                                       |
| 2   | `test_filtered_output_excludes_non_matching_features` | With two-feature fixture, `--feature-coverage-filter <substr>` produces output containing only the matching feature name |

______________________________________________________________________

## Agentic Workflow: Project Memory

- **TTL**: short — actively being worked.
- **Author(s)**: speckit.plan (2026-07-18)
- **Audience(s)**: Fresh agent sessions resuming work on `feat/w29-coverage-filter`.

### Project Context

- `docs/plans/README.md` — updated to point Current Focus to this plan.
- `docs/features/` — motivating feature is `features/001-feature-coverage-plugin.feature.yaml` under `COVERAGE_FILTER` (requirements 1–9 already present).
- `docs/design/` — no architecture changes; no design doc updates needed.

### Decision Capture Reminder

Key decisions already captured in `research.md`. If new trade-offs surface during implementation, capture them with `/speckit.agentic.document-decisions`.

### Quality Gate

The `after_plan` hook will offer to evaluate this plan against `docs/plans/RUBRIC.md`. Run manually: `/speckit.agentic.apply-rubric docs/plans/RUBRIC.md`
