# Tasks: w29 — `--feature-coverage-filter`

**Feature**: Add `--feature-coverage-filter` CLI option to pytest-feature-coverage\
**Branch**: `feat/w29-coverage-filter`\
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)\
**Generated**: 2026-07-18

______________________________________________________________________

## Summary

Production code in `src/pytest_feature_coverage/plugin.py` is **already complete** (~15 lines across `pytest_addoption()` and `_compute_and_store_report()`). All remaining work is writing tests: 9 unit tests (`tests/unit/test_filter.py`) and 2 integration tests (`tests/integration/test_coverage_filter.py`).

| Phase                                          | Scope                                                        | Tasks  |
| ---------------------------------------------- | ------------------------------------------------------------ | ------ |
| Phase 1 — Verify Implementation                | Read `plugin.py`; confirm contract compliance                | 2      |
| Phase 2 — Foundational                         | Green baseline before adding new tests                       | 1      |
| Phase 3 — US7: Filter Coverage Report          | Unit tests 1–7 + integration test file + 2 integration tests | 11     |
| Phase 4 — US7b: Threshold & Orphan Correctness | Unit tests 8–9                                               | 2      |
| Final Phase — Polish                           | `req()` markers on all new tests + final run                 | 3      |
| **Total**                                      |                                                              | **19** |

______________________________________________________________________

## Phase 1 — Verify Implementation

> Confirm the two `plugin.py` changes exist and match the CLI contract before writing tests against them. Both tasks are read-only and can be done simultaneously.

- [ ] T001 [P] Verify `pytest_addoption()` in `src/pytest_feature_coverage/plugin.py` contains `--feature-coverage-filter` with `action='append'`, `default=None`, `metavar='TEXT'`, and help text matching `contracts/cli-options.md` ("Only show features whose name contains TEXT (case-insensitive). Repeatable; multiple values combine as OR. Default: show all features.")
- [ ] T002 [P] Verify `_compute_and_store_report()` in `src/pytest_feature_coverage/plugin.py` reads `features = state['features']` first (full list, never mutated), then applies `filters = config.getoption('--feature-coverage-filter') or []`, and reassigns the local `features` variable to the filtered slice before calling `compute_coverage(features, req_map)`

______________________________________________________________________

## Phase 2 — Foundational

> Confirm the full test suite is green before adding new test files. Must complete before Phase 3.

- [ ] T003 Run `uv run pytest tests/ -q` from the repo root and confirm all existing tests pass with zero failures and zero errors

______________________________________________________________________

## Phase 3 — US7: Filter Coverage Report by Feature Name

**Story goal**: `--feature-coverage-filter <substr>` narrows the report to features whose name contains the substring (case-insensitive, OR semantics); Overall counts and `--feature-coverage-min` threshold are both scoped to the filtered set.

**Independent test**:

```bash
uv run pytest tests/unit/test_filter.py tests/integration/test_coverage_filter.py -v
```

### Unit Tests — `tests/unit/test_filter.py` (new file)

> Pattern: use `types.SimpleNamespace()` for config stub with a `getoption` lambda, the `_PLUGIN_STATE_ATTR` constant, and a `_make_feature(name, requirements)` helper — identical to the approach in `tests/unit/test_plugin.py::TestComputeAndStoreReport`.

- [ ] T004 [US7] Create `tests/unit/test_filter.py` with: module docstring `"""Unit tests for --feature-coverage-filter option."""`, `from __future__ import annotations`, imports for `types` and `pytest`, the constant `_PLUGIN_STATE_ATTR = '_feature_coverage_state'`, a module-level helper `_make_feature(name: str, requirements: dict[int, str] | None = None) -> FeatureFileModel` that builds a `FeatureFileModel` with a single `'COMP'` component (importing `ComponentModel`, `FeatureFileModel`, `FeatureModel` from `pytest_feature_coverage.schema` inside the helper), and an empty `class TestFilterBehaviour` with a class docstring
- [ ] T005 [US7] Add `test_single_filter_exact_match` to `class TestFilterBehaviour` in `tests/unit/test_filter.py`: state has two features (`'jinja-template-adapter'` with 1 req, `'bigquery-domain-view'` with 1 req); `config.getoption('--feature-coverage-filter')` returns `['jinja-template-adapter']`; after calling `_compute_and_store_report(config)`, assert `len(state['report'].features) == 1` and `state['report'].features[0].feature.name == 'jinja-template-adapter'`
- [ ] T006 [US7] Add `test_single_filter_substring_match` to `class TestFilterBehaviour` in `tests/unit/test_filter.py`: same two-feature state; filter is `['jinja']` (substring, not full name); assert result contains exactly 1 feature and its name is `'jinja-template-adapter'` (confirms partial-name matching per COVERAGE_FILTER.1)
- [ ] T007 [US7] Add `test_multiple_filters_or_semantics` to `class TestFilterBehaviour` in `tests/unit/test_filter.py`: same two-feature state; filters are `['jinja', 'bigquery']`; assert `len(state['report'].features) == 2` — both features are included because OR semantics means matching either filter is sufficient (COVERAGE_FILTER.4)
- [ ] T008 [US7] Add `test_filter_case_insensitive` to `class TestFilterBehaviour` in `tests/unit/test_filter.py`: feature named `'jinja-template-adapter'`; filter is `['JINJA']` (uppercase); assert feature is included in the report — confirms case-insensitive match as required by COVERAGE_FILTER.1
- [ ] T009 [US7] Add `test_filter_zero_matches_empty_report` to `class TestFilterBehaviour` in `tests/unit/test_filter.py`: two-feature state; filter is `['xyz']` which matches nothing; assert `state['report'].features == []`, `state['report'].total_requirements == 0`, and `state['report'].coverage_percentage == 0.0` — confirms COVERAGE_FILTER.9 (empty report, no unhandled exception)
- [ ] T010 [US7] Add `test_no_filter_all_features_shown` to `class TestFilterBehaviour` in `tests/unit/test_filter.py`: two-feature state; `config.getoption('--feature-coverage-filter')` returns `None` (option absent); assert `len(state['report'].features) == 2` — confirms COVERAGE_FILTER.5 (unfiltered baseline is unchanged)
- [ ] T011 [US7] Add `test_overall_percentage_uses_filtered_set` to `class TestFilterBehaviour` in `tests/unit/test_filter.py`: state has two features — `'jinja-template-adapter'` has requirement `jinja-template-adapter.COMP.1` in `req_map` (covered), `'bigquery-domain-view'` has no covered reqs; filter is `['jinja']`; assert `state['report'].covered_requirements == 1`, `state['report'].total_requirements == 1`, and `state['report'].coverage_percentage == 100.0` — confirms COVERAGE_FILTER.2 (Overall counts only filtered features' requirements)

### Integration Tests — `tests/integration/test_coverage_filter.py` (new file)

> Use `pytester` fixture (real subprocess). Match the structure in `tests/integration/test_ci_threshold.py`: `pytestmark = pytest.mark.integration`, one class, `pytester.mkdir` + `write_text` for YAML fixtures, `pytester.makeini` for `feature_yaml_paths`, `pytester.makepyfile` for test content.

- [ ] T012 [P] [US7] Create `tests/integration/test_coverage_filter.py` with: module docstring `"""Acceptance tests for --feature-coverage-filter option (US7)."""`, `from __future__ import annotations`, `import pytest`, `pytestmark = pytest.mark.integration`, and an empty `class TestCoverageFilterIntegration` with a class docstring
- [ ] T013 [US7] Add `test_help_shows_filter_option` to `class TestCoverageFilterIntegration` in `tests/integration/test_coverage_filter.py`: call `pytester.runpytest('--help')`; assert `'--feature-coverage-filter'` and `'case-insensitive'` both appear in `result.stdout.str()` — confirms COVERAGE_FILTER.7 (option visible in help with accurate description)
- [ ] T014 [US7] Add `test_filtered_output_excludes_non_matching_features` to `class TestCoverageFilterIntegration` in `tests/integration/test_coverage_filter.py`: create `features/` dir with two YAML files — `jinja-template-adapter.feature.yaml` (id `'001'`, name `'jinja-template-adapter'`, one component with one requirement) and `bigquery-domain-view.feature.yaml` (id `'002'`, name `'bigquery-domain-view'`, one component with one requirement); `pytester.makeini` with `feature_yaml_paths = features`; `pytester.makepyfile` with one no-op test; run `pytester.runpytest('--feature-coverage', '--feature-coverage-filter', 'jinja')`; assert stdout contains `'jinja-template-adapter'` and does NOT contain `'bigquery-domain-view'` — confirms COVERAGE_FILTER.1 and COVERAGE_FILTER.8 (all reporters scope to filtered set; text reporter verified here)

______________________________________________________________________

## Phase 4 — US7b: Threshold and Orphan Correctness Under Filter

**Story goal**: `--feature-coverage-min` is evaluated against the filtered Overall percentage; orphan `req()` detection continues to use the full (unfiltered) feature set.

**Independent test**:

```bash
uv run pytest tests/unit/test_filter.py::TestFilterBehaviour::test_orphan_markers_unaffected_by_filter \
              tests/unit/test_filter.py::TestFilterBehaviour::test_threshold_evaluated_against_filtered_set -v
```

- [ ] T015 [US7b] Add `test_orphan_markers_unaffected_by_filter` to `class TestFilterBehaviour` in `tests/unit/test_filter.py`: state has two features (`'jinja-template-adapter'`, `'bigquery-domain-view'`) and `state['orphans'] = ['bigquery-domain-view.COMP.1']`; filter is `['jinja']` (excludes the bigquery feature from report); after `_compute_and_store_report(config)`, assert `state['report'].orphan_markers == ['bigquery-domain-view.COMP.1']` — confirms COVERAGE_FILTER.6 (orphan for filtered-out feature is NOT falsely suppressed; the marker was valid, its feature was simply filtered)
- [ ] T016 [US7b] Add `test_threshold_evaluated_against_filtered_set` to `class TestFilterBehaviour` in `tests/unit/test_filter.py`: state has two features — `'jinja-template-adapter'` with one req and NO covered entries in `req_map` (0%), `'bigquery-domain-view'` with one req covered (100%); filter is `['jinja']`; after `_compute_and_store_report(config)`, assert `state['report'].coverage_percentage == 0.0` and `state['report'].total_requirements == 1` (threshold is evaluated against this filtered value, so a `--feature-coverage-min 50` would fail); also assert `len(getattr(config, _PLUGIN_STATE_ATTR)['features']) == 2` (full `state['features']` list is unmodified) — confirms COVERAGE_FILTER.3 and COVERAGE_FILTER.6 state-isolation guarantee

______________________________________________________________________

## Final Phase — Polish & Cross-Cutting Concerns

- [ ] T017 [P] Add `@pytest.mark.req` decorators to every test method in `tests/unit/test_filter.py` using the mapping: `test_single_filter_exact_match` → `COVERAGE_FILTER.1`; `test_single_filter_substring_match` → `COVERAGE_FILTER.1`; `test_multiple_filters_or_semantics` → `COVERAGE_FILTER.4`; `test_filter_case_insensitive` → `COVERAGE_FILTER.1`; `test_filter_zero_matches_empty_report` → `COVERAGE_FILTER.9`; `test_no_filter_all_features_shown` → `COVERAGE_FILTER.5`; `test_overall_percentage_uses_filtered_set` → `COVERAGE_FILTER.2`; `test_orphan_markers_unaffected_by_filter` → `COVERAGE_FILTER.6`; `test_threshold_evaluated_against_filtered_set` → `COVERAGE_FILTER.3` — full marker ID format: `'feature-coverage-plugin.COVERAGE_FILTER.N'`
- [ ] T018 [P] Add `@pytest.mark.req` decorators to every test method in `tests/integration/test_coverage_filter.py` using the mapping: `test_help_shows_filter_option` → `'feature-coverage-plugin.COVERAGE_FILTER.7'`; `test_filtered_output_excludes_non_matching_features` → `'feature-coverage-plugin.COVERAGE_FILTER.8'`
- [ ] T019 Run `uv run pytest tests/ -q` from the repo root; confirm all tests pass including 11 new tests (9 unit + 2 integration); confirm zero failures, zero errors, and that running `uv run pytest tests/ --feature-coverage --feature-coverage-min 1 -q` shows `COVERAGE_FILTER.*` requirements with coverage > 0% in the feature coverage report

______________________________________________________________________

## Dependencies

```text
T001, T002  (independent of each other — both verify plugin.py read-only)
T003        (needs T001+T002 logically; must be green before test writing)
T004        (needs T003)
T005–T011   (each needs T004; independent of each other — different test methods)
T012        (needs T003; independent of T004–T011 — different file)
T013        (needs T012)
T014        (needs T012; independent of T013 — different test method)
T015, T016  (each needs T004; independent of each other — different test methods)
T017        (needs T005–T011, T015, T016 — adds markers to test_filter.py)
T018        (needs T013, T014 — adds markers to test_coverage_filter.py)
T019        (needs T017, T018)
```

### Parallel Execution Opportunities

**Track A** (test_filter.py) and **Track B** (test_coverage_filter.py) can proceed concurrently after T003:

```text
T001 [P] ──┐
T002 [P] ──┘── T003 ──┬─ T004 ─── T005–T011 ─── T015 ─── T016 ─── T017 [P] ──┐
                      │                                                          ├── T019
                      └─ T012 [P] ─── T013 ─── T014 ─────────────── T018 [P] ──┘
```

Within each track, test methods (T005–T011, T013–T014, T015–T016) are added sequentially to a single file but are independent of each other and require no ordering between themselves.

______________________________________________________________________

## Implementation Strategy

| Increment       | Tasks     | Coverage Added                        | Exit Criterion                                                                                                                                              |
| --------------- | --------- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MVP**         | T001–T013 | COVERAGE_FILTER.1, .2, .4, .5, .7, .9 | `uv run pytest tests/unit/test_filter.py tests/integration/test_coverage_filter.py::TestCoverageFilterIntegration::test_help_shows_filter_option -v` passes |
| **Increment 2** | T014–T016 | COVERAGE_FILTER.3, .6, .8             | All 11 new tests pass                                                                                                                                       |
| **Increment 3** | T017–T019 | `req()` markers wired                 | Full suite green; `COVERAGE_FILTER.*` requirements covered in plugin's own report                                                                           |

______________________________________________________________________

## Agentic Workflow: Post-Implementation Checklist

> This section is added by the agentic-workflow preset. It prompts for review and documentation steps after the tasks are complete.

### After All Tasks Complete

1. **Code Review**: Run `/speckit.agentic.code-review` to evaluate the implementation against the spec's acceptance criteria.

1. **Design Alignment**: If architectural changes were made, run `/speckit.agentic.review-alignment` to check for drift between `docs/design/` and the actual implementation.

1. **Decision Capture**: If any trade-offs or technology choices were made during implementation, run `/speckit.agentic.document-decisions` to capture them as ADRs in `docs/decisions/`.

1. **Plan Close-out**: Run `/speckit.agentic.close-plan` to finalize the plan and move it to the completed section of `docs/plans/README.md`.

1. **Lesson Extraction**: If reusable patterns emerged, run `/speckit.agentic.extract-lessons` to promote them to `docs/guides/` or `docs/design/`.
