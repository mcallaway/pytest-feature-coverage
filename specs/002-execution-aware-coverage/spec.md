# Feature Specification: Execution-Aware Feature Coverage

**Feature Branch**: `fix/collection-vs-execution-coverage`

**Created**: 2026-09-29

**Status**: Draft

**Input**: User description: "Count Only Successful Tests as Requirement Coverage - pytest-feature-coverage currently grants coverage credit during collection. A requirement should be covered only when at least one collected test carrying its req() marker completes successfully (passes)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Coverage Reflects Verified Requirements, Not Declared Ones (Priority: P1)

As a developer relying on `pytest --feature-coverage` as a CI gate, I want a requirement to count as covered only when a test that references it actually passed, so that a green feature-coverage report is honest evidence the requirement was verified, not just that a test was written and collected.

**Why this priority**: This is the core defect. Every other user story in this spec is a consequence of getting this one right. Without it, the coverage percentage and the CI threshold gate are both unreliable safety signals.

**Independent Test**: Can be fully tested by running a single test annotated with `req()` that fails, and confirming the requirement it references shows as uncovered in the report, then flipping the test to pass and confirming it becomes covered.

**Acceptance Scenarios**:

1. **Given** a requirement referenced only by a test that passes, **When** the suite runs with `--feature-coverage`, **Then** the requirement is reported as covered.
1. **Given** a requirement referenced only by a test that fails, **When** the suite runs with `--feature-coverage`, **Then** the requirement is reported as uncovered.
1. **Given** a requirement referenced only by a test that is skipped, **When** the suite runs with `--feature-coverage`, **Then** the requirement is reported as uncovered.
1. **Given** a requirement referenced only by a test marked `xfail` that fails as expected, **When** the suite runs with `--feature-coverage`, **Then** the requirement is reported as uncovered.
1. **Given** a requirement referenced only by a test whose setup (fixture) raises an error, **When** the suite runs with `--feature-coverage`, **Then** the requirement is reported as uncovered.

______________________________________________________________________

### User Story 2 - One Passing Test Is Enough When Several Reference the Same Requirement (Priority: P2)

As a developer, I want a requirement to count as covered as soon as any one of the tests that reference it passes, even if other tests referencing the same requirement fail, skip, or xfail, so that adding a deliberately-failing regression test alongside a passing one does not regress my coverage numbers.

**Why this priority**: Directly required by the acceptance criteria and by the "many-to-many" relationship the plugin already supports between requirements and tests; getting this wrong would make coverage numbers volatile and punish legitimate test suite composition (e.g. a passing happy path test plus a failing regression-reproduction test for the same requirement).

**Independent Test**: Can be fully tested by annotating two tests with the same requirement ID, one passing and one failing, and confirming the requirement is covered and the report identifies only the passing test's node ID as the covering evidence.

**Acceptance Scenarios**:

1. **Given** a requirement referenced by one passing test and one failing test, **When** the suite runs with `--feature-coverage`, **Then** the requirement is covered and the report lists only the passing test's node ID as covering evidence.
1. **Given** a requirement referenced by one passing test and one skipped test, **When** the suite runs with `--feature-coverage`, **Then** the requirement is covered and the report lists only the passing test's node ID.
1. **Given** a parametrized test where at least one parameter case passes and at least one fails, **When** the suite runs with `--feature-coverage`, **Then** the requirement is covered and the report identifies the specific passing case's node ID (including its parameter id), not the failing case's.
1. **Given** a parametrized test where no parameter case passes, **When** the suite runs with `--feature-coverage`, **Then** the requirement is reported as uncovered.

______________________________________________________________________

### User Story 3 - The CI Threshold Gate Reflects Execution-Aware Coverage (Priority: P2)

As a CI pipeline operator, I want `--feature-coverage-min` to be evaluated against execution-aware coverage (not collection-time coverage), so that a build cannot pass the coverage gate purely by declaring `req()` markers on tests that never actually pass.

**Why this priority**: The threshold gate is the primary way this plugin is consumed in CI (ADR-003, Layer 2). If the underlying coverage computation becomes execution-aware but the threshold check is not updated in lockstep, the gate silently loses its meaning even though the report itself looks correct.

**Independent Test**: Can be fully tested by setting `--feature-coverage-min=100` against a suite whose only test referencing a requirement fails, and confirming the process exits non-zero.

**Acceptance Scenarios**:

1. **Given** a requirement covered only by a failing test and `--feature-coverage-min=100`, **When** the suite runs, **Then** the process exits non-zero and the underlying pytest failure exit status is not hidden or overwritten.
1. **Given** all requirements covered by passing tests and `--feature-coverage-min=100`, **When** the suite runs, **Then** the process exits zero.

______________________________________________________________________

### User Story 4 - Reports Agree Across Formats and Distinguish Verified Evidence (Priority: P3)

As a developer reading a coverage report in whichever format their tooling consumes (text, JSON, or Markdown), I want all three formats to agree on totals, percentages, and which test node IDs actually supplied coverage credit, so that I can trust any one format without cross-checking the others.

**Why this priority**: Lower priority than the core semantics (US1-US3) because it is a consistency requirement layered on top of a correct computation; it matters for trust and tooling but does not change whether the gate itself is honest.

**Independent Test**: Can be fully tested by running the same suite three times with `--feature-coverage-format=text`, `=json`, and `=markdown` and diffing the totals, percentages, and covering test IDs across the three outputs.

**Acceptance Scenarios**:

1. **Given** a mixed suite of passing, failing, and skipped tests referencing requirements, **When** the report is rendered in text, JSON, and Markdown, **Then** all three report the same total requirement count, covered count, percentage, and set of covering node IDs per requirement.

______________________________________________________________________

### Edge Cases

- A test marked `xfail` that unexpectedly passes (`xpass`, non-strict) does NOT count as coverage. An xfail marker is a declared expectation that the test will fail; an unexpectedly passing xfail test signals the marker itself is stale or the requirement's behavior changed, not a genuine verification of the requirement, so it must not be rewarded with coverage credit. This must be documented (in ADR-003 and the plugin's public output) so it is a deliberate policy rather than an accident of a pytest hook.
- A collected test that is later deselected (e.g. via `-k` or `-m`) and never executed does not count as coverage; it simply never enters the set of passing node IDs, the same as any other test that never ran.
- A test whose teardown (not just setup or call) raises an error does not count as coverage, even if the call phase passed cleanly; a teardown error means the test session did not complete cleanly for that node.
- Two tests referencing the same requirement where one passes on setup+call+teardown and another fails: the requirement is covered, and the report shows only the passing node ID, not the failing one, per User Story 2.
- A `req()` marker on a test that is itself an orphan (its ID matches no known requirement) continues to be flagged as an orphan at collection time regardless of whether that test later passes or fails; orphan detection is unrelated to execution outcome and must not regress.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The plugin MUST track, for every collected test node ID that carries at least one `req()` marker, whether that node ID's setup, call, and teardown phases all completed with a clean pass (no failure, no skip, no unhandled xfail).
- **FR-002**: The plugin MUST compute coverage such that a requirement is covered if and only if at least one of its associated node IDs achieved a clean pass as defined in FR-001.
- **FR-003**: A failing test, a skipped test, an expected failure (`xfail`), and a test with a setup or teardown error MUST NOT count toward coverage for any requirement they reference.
- **FR-004**: An unexpected pass (`xpass`, non-strict `xfail`) MUST NOT count toward coverage. This is a deliberate policy decision, not an accident of pytest's default hook behavior, and MUST be documented in ADR-003 and in user-facing plugin documentation.
- **FR-005**: When multiple node IDs reference the same requirement, the requirement MUST be covered if any one of them achieves a clean pass, independent of the outcome of the others.
- **FR-006**: For parametrized tests, each parameter case MUST be tracked and evaluated by its own node ID and outcome; a requirement referenced by a parametrized test is covered if at least one parameter case passes cleanly.
- **FR-007**: Reports (text, JSON, and Markdown) MUST list, for each covered requirement, only the node IDs that supplied a clean pass as covering evidence; node IDs that were merely collected and associated but did not pass MUST NOT appear as covering evidence.
- **FR-008**: `--feature-coverage-min` MUST be evaluated against execution-aware coverage (per FR-002), not collection-time coverage.
- **FR-009**: Applying the `--feature-coverage-min` threshold MUST NOT hide or override pytest's own failure exit status; a suite with failing tests remains a non-zero exit regardless of whether the feature-coverage threshold itself would have passed or failed.
- **FR-010**: Orphan `req()` marker detection and `feature_coverage_strict` error behavior MUST remain collection-time behavior, evaluated independent of runtime outcome, with no regression from current behavior.
- **FR-011**: The plugin MUST continue to support the existing `req()` marker syntax and feature YAML schema unchanged; no changes are required to how requirements are declared or how tests are annotated.
- **FR-012**: The plugin MUST remain completely inert (no runtime outcome tracking, no hook overhead beyond a no-op check) unless `--feature-coverage` is active.
- **FR-013**: The end-to-end behavior described in FR-001 through FR-010 MUST be verified with `pytester`-based acceptance tests that run a real nested pytest session with real passing, failing, skipped, xfailed, and erroring tests, not only through unit tests of internal state.

### Key Entities

- **Node outcome**: The accumulated verdict for one collected test node ID (or parametrized case) across its setup, call, and teardown phases: whether it achieved a clean pass. This is new runtime state; it does not replace the existing collection-time `req_map` (requirement ID to associated node IDs), it is applied on top of it when the report is computed.
- **Covering test**: A node ID that both (a) was associated with a requirement via a `req()` marker at collection time and (b) achieved a clean pass at runtime. Only covering tests, not merely associated ones, appear in reports as evidence.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A requirement whose only associated test fails, skips, xfails, or errors during setup/teardown is reported as uncovered in 100% of such cases, where today it is reported as covered.
- **SC-002**: A requirement covered by at least one passing test among several associated tests of mixed outcomes is reported as covered, and the report identifies only the passing node ID(s) as evidence, in 100% of such cases.
- **SC-003**: The `--feature-coverage-min` CI gate exits non-zero whenever execution-aware coverage is below the configured threshold, even when collection-time coverage (the old computation) would have met the threshold.
- **SC-004**: Text, JSON, and Markdown reports produced from the same test run agree on total requirement count, covered count, coverage percentage, and the set of covering node IDs, in 100% of runs.
- **SC-005**: All existing feature-coverage acceptance tests and the project's own `mise run test:all`, `mise run test:coverage`, and `mise run test:features` checks pass after the change, with zero regressions in orphan detection, strict-mode errors, or output format structure.

## Assumptions

- "Clean pass" means the pytest `TestReport.outcome` for the setup, call, and teardown phases of a node ID were all `"passed"`, and the call phase was not an unexpected pass (`xpass`) of an `xfail`-marked test. This definition is deliberately narrower than "the process did not raise an unhandled exception."
- Deselected, filtered-out (`-k`/`-m`), or otherwise never-executed collected tests are out of scope for special-casing: they simply never appear in the set of passing node IDs, which already produces the correct "not covered" outcome without additional logic.
- The existing `req()` marker syntax, feature YAML schema, and CLI/INI option surface (`--feature-coverage`, `--feature-coverage-format`, `--feature-coverage-min`, `--feature-coverage-filter`, `feature_yaml_paths`, `feature_coverage_strict`) are unchanged by this feature; this is a change to how coverage is computed, not to how it is configured or declared.
- This feature extends the existing `feature-coverage-plugin` (`001`) feature rather than introducing an unrelated new feature area; new requirement IDs are added to `features/001-feature-coverage-plugin.feature.yaml` under a new component, and `docs/features/001-feature-coverage-plugin.md` is updated in place rather than creating a duplicate feature doc.
- ADR-003 ("What 'Tested' Means in This Project") requires an update because its current Layer 2 wording ("every declared requirement has at least one covering test") predates a precise definition of "covering" and could be misread as collection-time association; the update clarifies that "covering" means execution-aware, per this spec.
