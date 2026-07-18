# Feature Specification: Coverage Report Filtering

- **Feature Branch**: `feat/w29-coverage-filter`
- **Created**: 2026-07-18
- **Status**: Draft
- **Input**: User description from `tmp/w29-feature-coverage-filter.md`
- **Extends**: Feature 001 (`specs/001-feature-coverage-plugin/spec.md`)

## Context

This is an extension of the Feature Coverage Plugin (001). It adds a
`--feature-coverage-filter` CLI option that narrows the coverage report to a
subset of features by substring match on the feature name. All other plugin
behaviour (test selection, orphan checking, threshold enforcement) is unchanged
except as explicitly listed in the requirements below.

The problem it solves: when a project has 20+ `.feature.yaml` files,
`--feature-coverage` outputs hundreds of lines covering all features. A
developer working on a single feature has no way to get a focused view of just
that feature's requirement coverage. The current workaround — combining
`-k <pattern>` with `--feature-coverage` — filters which tests run, but the
coverage report still lists all features, most at 0% because those tests were
deselected.

Requirements are tracked in `features/001-feature-coverage-plugin.feature.yaml`
under the `COVERAGE_FILTER` component (requirements 1–9).

## User Scenarios & Testing *(mandatory)*

### User Story 7 - Filter Coverage Report by Feature Name (Priority: P2)

A developer working on a specific feature in a large project passes
`--feature-coverage-filter <substr>` and sees only features whose name
contains that substring in the coverage report. The "Overall" summary and
`--feature-coverage-min` threshold enforcement are both scoped to the filtered
feature set, giving an accurate view of progress on the feature they care about.

**Why this priority**: Requires the baseline coverage report (US-3) to be
fully working. Significantly improves developer ergonomics in large projects
but does not block the core CI use case.

**Independent Test**: Can be fully tested by running pytest with
`--feature-coverage --feature-coverage-filter <substr>` on a project containing
multiple feature YAML files and verifying that only matching features appear in
the report and that Overall counts only their requirements.

**Acceptance Scenarios**:

1. **Given** a project with features `jinja-template-adapter` and `bigquery-domain-view`, **When** `--feature-coverage-filter jinja` is passed, **Then** only `jinja-template-adapter` appears in the report and Overall counts only its requirements
1. **Given** the same project, **When** `--feature-coverage-filter JINJA` is passed (uppercase), **Then** the match succeeds case-insensitively and `jinja-template-adapter` is still shown
1. **Given** both `--feature-coverage-filter jinja` and `--feature-coverage-filter bigquery` are passed, **When** the report is generated, **Then** both matching features are shown (OR semantics)
1. **Given** no `--feature-coverage-filter` flags are passed, **When** the report runs, **Then** all features appear (identical to the current unfiltered behaviour)
1. **Given** `--feature-coverage-filter xyz` matches no features, **When** the report runs, **Then** an empty report is shown with `Overall: 0/0 requirements covered (0.0%)` and the process does not error on account of the empty result alone

---

### User Story 7b - Threshold and Orphan Correctness Under Filter (Priority: P2)

When a filter is active, `--feature-coverage-min` threshold is evaluated
against the filtered Overall percentage and orphan `req()` detection continues
to use the full feature set, preventing both false CI passes and false orphan
errors.

**Why this priority**: Correctness properties — getting these wrong would
cause silently wrong CI results (threshold applied to the wrong scope) or
false orphan warnings (valid markers for filtered-out features flagged as
unknown).

**Independent Test**: Can be tested independently of the basic filter
by (a) configuring a threshold that the full project passes but the filtered
subset fails — confirming exit non-zero; and (b) verifying that a `req()` marker
for a filtered-out feature does not produce an orphan warning.

**Acceptance Scenarios**:

1. **Given** `--feature-coverage-filter jinja --feature-coverage-min 90` and `jinja` feature coverage is 80%, **When** the report runs, **Then** pytest exits non-zero even if full-project coverage exceeds 90%
1. **Given** `--feature-coverage-filter jinja` is active and a test has `@pytest.mark.req("bigquery.COMP.1")`, **When** the report runs, **Then** no orphan warning is emitted for `bigquery.COMP.1` (the ID is valid; its feature is simply filtered from the report)
1. **Given** `--feature-coverage-filter jinja` is active and a test has `@pytest.mark.req("nonexistent.COMP.1")` (not in any loaded YAML), **When** the report runs, **Then** an orphan warning IS emitted for `nonexistent.COMP.1`

---

### Edge Cases

- What happens when the filter substring is empty string `""`? → Every feature name contains the empty string, so all features are shown (equivalent to no filter).
- What happens when `--feature-coverage-filter` is passed without `--feature-coverage`? → The plugin does not activate; the option is silently accepted but unused, consistent with other `--feature-coverage-*` options.
- What happens when two features both match the same filter? → Both are shown; OR semantics means any match is sufficient.
- What happens when the filter produces 0 matching features and `--feature-coverage-min 50` is set? → `0/0 = 0.0%` is below 50%, so pytest exits non-zero (the empty-result rule applies to the report itself, not to threshold enforcement).

## Requirements *(mandatory)*

### Functional Requirements

- **COVERAGE_FILTER.1**: System MUST accept `--feature-coverage-filter TEXT` as a repeatable CLI option that narrows the coverage report to features whose name contains `TEXT` (case-insensitive); features whose names do not match any filter are excluded from the report
- **COVERAGE_FILTER.2**: When one or more filters are active, "Overall" totals and coverage percentages MUST count only the filtered features' requirements
- **COVERAGE_FILTER.3**: `--feature-coverage-min` threshold MUST be evaluated against the filtered Overall percentage, not the full feature set's percentage
- **COVERAGE_FILTER.4**: Multiple `--feature-coverage-filter` flags MUST combine as OR: a feature is included if its name contains any of the provided substrings
- **COVERAGE_FILTER.5**: When no `--feature-coverage-filter` flags are passed, behaviour MUST be identical to the current unfiltered baseline; no existing behaviour may be changed as a side-effect of this addition
- **COVERAGE_FILTER.6**: Orphan `req()` marker detection MUST remain unaffected by the filter; orphan checking MUST use the full set of loaded features, not the filtered subset
- **COVERAGE_FILTER.7**: The `--feature-coverage-filter` option MUST appear in `pytest --help` output with a description that conveys substring matching, case-insensitivity, and OR combination behaviour
- **COVERAGE_FILTER.8**: All three output format reporters (text, JSON, markdown) MUST produce output scoped exclusively to the filtered feature set when the option is active
- **COVERAGE_FILTER.9**: Filtering to 0 matching features MUST produce an empty report with `Overall: 0/0 requirements covered (0.0%)` and MUST NOT raise an unhandled exception or exit non-zero on account of the empty result alone

### Key Entities

No new entities are introduced. The filter acts on the existing **Feature** list before it is passed to coverage matrix computation. The **CoverageReport** produced by `compute_coverage()` is naturally scoped to whatever feature list is provided; reporters consume the report without needing filter awareness.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-F1**: A project with 21 `.feature.yaml` files filtered to 1 matching feature produces a report containing exactly 1 feature section; the Overall line reflects only that feature's requirements
- **SC-F2**: `pytest --help` output includes `--feature-coverage-filter` with a human-readable description
- **SC-F3**: When a filter is active and a test carries a `req()` marker for a filtered-out (but validly loaded) feature, zero orphan warnings are emitted for that marker
- **SC-F4**: A project whose full coverage passes `--feature-coverage-min` but whose filtered subset does not exits non-zero with a message stating actual vs. required percentage
- **SC-F5**: A filter that matches 0 features exits zero (unless the threshold forces non-zero) and prints `Overall: 0/0 requirements covered (0.0%)`
- **SC-F6**: JSON output with an active filter contains only the filtered features' data; Markdown output contains only the filtered features' rows

## Clarifications

### Session 2026-07-18

All 9 acceptance criteria are specified without ambiguity in
`tmp/w29-feature-coverage-filter.md`. No open clarifications.

Key design decisions captured from w29:

- The filter is **report-scope only** — it does not affect pytest test collection
- The filter is applied by slicing the feature list before `compute_coverage()` is called, not by modifying any reporter or schema module
- The full feature list is preserved in plugin state for orphan checking throughout the session
- No INI option is added (the filter is a session-specific developer convenience, not a stable project-wide setting; adding an INI option would encourage committing filters that silently hide features in CI)
- `-m` / pytest marker expressions are not used for filtering because feature names contain dashes and dots that are not valid Python identifiers

## Assumptions

- Users may combine `--feature-coverage-filter` with `-k` to also narrow which tests run; the two options are orthogonal and under the user's control
- Feature names follow the `kebab-case` convention already used in all existing YAML files in this project
- Matching uses the feature's `name` field (not its numeric `id`), consistent with the w29 specification
- An empty-string filter (`--feature-coverage-filter ""`) matching all feature names is acceptable behaviour
- Implementation requires changes only in `src/pytest_feature_coverage/plugin.py`; no changes to `schema.py`, `scanner.py`, `matrix.py`, or any reporter file are needed
