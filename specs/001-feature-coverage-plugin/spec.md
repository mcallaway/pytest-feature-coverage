# Feature Specification: Feature Coverage Plugin

- **Feature Branch**: `feat/001-feature-coverage-plugin`
- **Created**: 2025-05-19
- **Status**: Draft
- **Input**: User description from `tmp/w21-pytest-feature-coverage.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Define Requirements in YAML (Priority: P1)

A developer creates a `*.feature.yaml` file alongside their feature documentation to declare the feature's components and requirements in a machine-readable format. The YAML file is validated at pytest collection time.

**Why this priority**: Without machine-readable requirements, no coverage matrix can be computed. This is the foundational data model.

**Independent Test**: Can be fully tested by creating a valid YAML file and running pytest to confirm it loads without error; delivers the ability to define and validate requirements.

**Acceptance Scenarios**:

1. **Given** a valid `*.feature.yaml` file in a configured path, **When** pytest collects tests, **Then** the feature and its requirements are loaded successfully
1. **Given** a YAML file missing required fields, **When** pytest collects tests, **Then** collection fails with a clear error message identifying the invalid file and missing fields
1. **Given** a YAML file with duplicate requirement IDs across features, **When** pytest collects tests, **Then** collection fails with a clear error identifying the duplicates

______________________________________________________________________

### User Story 2 - Annotate Tests with Requirement Markers (Priority: P1)

A developer annotates their test functions with `@pytest.mark.req("feature.COMPONENT.N")` to declare which requirements each test covers. A single test may cover multiple requirements and a requirement may be covered by multiple tests.

**Why this priority**: Without the annotation mechanism, there is no way to connect tests to requirements. This is equally foundational as User Story 1.

**Independent Test**: Can be tested by annotating tests with `req()` markers and verifying the markers are collected and associated with the correct requirement IDs.

**Acceptance Scenarios**:

1. **Given** a test annotated with `@pytest.mark.req("feature.COMPONENT.1")`, **When** pytest collects tests, **Then** the test is associated with that requirement
1. **Given** a test annotated with multiple requirement IDs, **When** pytest collects tests, **Then** the test is associated with all specified requirements
1. **Given** a `req()` marker referencing an ID not present in any YAML file, **When** pytest collects tests, **Then** a warning is emitted (configurable to error)

______________________________________________________________________

### User Story 3 - Generate Coverage Report (Priority: P1)

A developer runs `pytest --feature-coverage` and sees a deterministic text report showing which requirements are covered by tests and which are not, grouped by feature and component.

**Why this priority**: The coverage report is the primary deliverable — the answer to "which requirements are covered?" This is the core value of the plugin.

**Independent Test**: Can be tested by running pytest with the flag on a project with YAML files and annotated tests, then verifying the output matches expected format and content.

**Acceptance Scenarios**:

1. **Given** a project with feature YAML and annotated tests, **When** `pytest --feature-coverage` is run, **Then** a text report is printed showing covered and uncovered requirements grouped by feature and component
1. **Given** identical inputs (same YAML, same tests), **When** `pytest --feature-coverage` is run multiple times, **Then** the output is identical each time (deterministic)
1. **Given** a project with no feature YAML files, **When** `pytest --feature-coverage` is run, **Then** a clear message indicates no features were found

______________________________________________________________________

### User Story 4 - CI Coverage Threshold (Priority: P2)

A CI pipeline runs `pytest --feature-coverage --feature-coverage-min=80` and the process exits non-zero when coverage falls below the threshold, failing the build.

**Why this priority**: Enables automated enforcement. Depends on the coverage matrix being computed (US1-3) but is not needed for initial developer feedback.

**Independent Test**: Can be tested by running pytest with a threshold higher than actual coverage and verifying exit code is non-zero.

**Acceptance Scenarios**:

1. **Given** feature coverage is 57% and threshold is set to 80, **When** pytest runs, **Then** the process exits with a non-zero exit code
1. **Given** feature coverage is 85% and threshold is set to 80, **When** pytest runs, **Then** the process exits with exit code 0
1. **Given** threshold is set to 0 (default), **When** pytest runs, **Then** the threshold check always passes

______________________________________________________________________

### User Story 5 - Machine-Readable Output Formats (Priority: P2)

A developer or CI pipeline generates coverage reports in JSON or Markdown format for downstream tooling or repository documentation.

**Why this priority**: Extends the core reporting with formats suitable for automation and documentation. Depends on the coverage matrix (US1-3).

**Independent Test**: Can be tested by running with `--feature-coverage-format=json` and verifying valid JSON output; same for markdown.

**Acceptance Scenarios**:

1. **Given** a project with feature YAML and annotated tests, **When** `pytest --feature-coverage --feature-coverage-format=json` is run, **Then** structured JSON is written to stdout
1. **Given** the same project, **When** `pytest --feature-coverage --feature-coverage-format=markdown` is run, **Then** a deterministic markdown table is written to stdout

______________________________________________________________________

### User Story 6 - Configuration via pyproject.toml (Priority: P3)

A developer configures the plugin's behavior (YAML search paths, default format, minimum threshold) through standard pytest configuration in `pyproject.toml`.

**Why this priority**: Convenience and convention. The plugin works with CLI flags alone; configuration just provides defaults.

**Independent Test**: Can be tested by setting values in pyproject.toml and verifying they are used when CLI flags are not provided.

**Acceptance Scenarios**:

1. **Given** `feature_yaml_paths = ["docs/features"]` in pyproject.toml, **When** pytest runs, **Then** YAML files are searched in `docs/features/`
1. **Given** `feature_coverage_min = 80` in pyproject.toml, **When** pytest runs without `--feature-coverage-min`, **Then** the 80% threshold is enforced

______________________________________________________________________

### Edge Cases

- What happens when a YAML file exists but has zero requirements defined?
- How does the system handle requirement IDs with special characters or spaces?
- What happens when `--feature-coverage` is not passed but `req()` markers exist on tests?
- What happens when multiple YAML files define the same feature ID?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST load and validate `*.feature.yaml` files from explicitly configured directories at pytest collection time; if no paths are configured, emit a clear error
- **FR-002**: System MUST fail pytest collection with clear error messages when YAML files do not match the expected schema
- **FR-003**: System MUST provide a `req()` pytest marker for annotating tests with one or more requirement IDs
- **FR-004**: System MUST support many-to-many relationships between tests and requirements
- **FR-005**: System MUST compute a coverage matrix cross-referencing requirements from YAML with tests bearing `req()` markers
- **FR-006**: System MUST produce a deterministic text report grouped by feature and component when `--feature-coverage` is passed
- **FR-007**: System MUST exit non-zero when coverage percentage falls below the configured `--feature-coverage-min` threshold
- **FR-008**: System MUST support JSON output format via `--feature-coverage-format=json`
- **FR-009**: System MUST support Markdown output format via `--feature-coverage-format=markdown`
- **FR-010**: System MUST emit a warning when a `req()` marker references an ID not present in any loaded YAML; when `feature_coverage_strict = true`, emit an error instead and fail collection
- **FR-011**: System MUST fail collection when duplicate requirement IDs exist across feature YAML files
- **FR-012**: System MUST be configurable via `pyproject.toml` under `[tool.pytest.ini_options]`; `feature_yaml_paths` is required (no default)
- **FR-013**: System MUST produce identical output for identical inputs (determinism)
- **FR-014**: Project MUST include a reference `*.feature.yaml` fixture in `tests/data/` that exercises all valid schema constructs (multiple components, multiple requirements per component, a zero-requirement component) to serve as both TDD fixture and living schema documentation

### Key Entities

- **Feature**: A top-level grouping with an ID and name, defined in YAML. Contains components.
- **Component**: A named grouping within a feature. Contains requirements.
- **Requirement**: A numbered statement within a component. Has a composite ID (`feature-name.COMPONENT.number`) and description text. Matching between `req()` markers and YAML is case-sensitive.
- **Coverage Matrix**: The cross-reference mapping requirements to their covering tests (or lack thereof).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `pytest --feature-coverage` produces byte-identical output when run against the same inputs on any run
- **SC-002**: Invalid YAML files cause pytest collection to fail within the first 5 seconds with an error message that names the file and describes the schema violation
- **SC-003**: Orphan `req()` markers (referencing non-existent requirement IDs) are detected and reported during collection
- **SC-004**: Coverage threshold enforcement exits non-zero with a message stating actual vs. required coverage
- **SC-005**: The plugin adds zero runtime overhead to test execution itself (overhead only at collection and reporting phases)
- **SC-006**: The plugin has no runtime dependencies beyond pytest, pydantic, and PyYAML

## Clarifications

### Session 2025-05-19

- Q: Default YAML discovery behavior when no paths configured? → A: Require explicit configuration; emit error if no paths set
- Q: Does `--feature-coverage-min` alone activate the plugin? → A: No; `--feature-coverage` is always required to activate
- Q: Default severity for orphan `req()` markers? → A: Warning by default; configurable to error via `feature_coverage_strict`
- Q: How to handle a component with zero requirements? → A: Valid; shows 0/0 in report, excluded from overall percentage
- Q: Case sensitivity for component names in `req()` matching? → A: Case-sensitive; must match YAML exactly

## Assumptions

- Users have pytest >= 7.0 installed in their environment
- Feature YAML files are committed to the repository (not generated at runtime)
- Requirement IDs follow the `{feature-name}.{COMPONENT}.{number}` convention strictly
- The plugin is invoked explicitly via `--feature-coverage`; it does not alter behavior when the flag is absent
- Mobile and browser support are not applicable (this is a CLI/CI tool)
- Initial release targets a single project repository (monorepo support is out of scope for v1)
