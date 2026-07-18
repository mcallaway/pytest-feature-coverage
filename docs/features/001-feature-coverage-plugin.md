# Feature: Feature Coverage Plugin

**Status**: Implemented | **ID**: 001

**YAML**: [`features/001-feature-coverage-plugin.feature.yaml`](../../features/001-feature-coverage-plugin.feature.yaml)

## Summary

A pytest plugin that connects test functions to requirements defined in YAML files and produces deterministic coverage reports. Enables CI-gated enforcement of requirement coverage with no AI, no network calls, and no runtime dependencies beyond pytest, pydantic, and PyYAML.

## User Stories

### US-1 -- Define Requirements in YAML

As a developer, I want to declare my feature's components and requirements in a machine-readable YAML file, so that requirement gaps are caught at collection time rather than discovered after implementation.

### US-2 -- Annotate Tests with Requirement Markers

As a developer, I want to annotate test functions with `@pytest.mark.req("feature.COMPONENT.N")`, so that requirement coverage is visible without manual cross-referencing of tests to a spec.

### US-3 -- Generate a Coverage Report

As a developer, I want to run `pytest --feature-coverage` and see which requirements are covered and which are not, so that I can identify gaps before committing or merging.

### US-4 -- Enforce a CI Coverage Threshold

As a CI pipeline, I want pytest to exit non-zero when requirement coverage falls below a configured minimum, so that uncovered requirements block the build automatically.

### US-5 -- Produce Machine-Readable Output

As a developer or CI pipeline, I want to generate coverage reports in JSON or Markdown format, so that downstream tooling and repository documentation stay up to date.

### US-6 -- Configure via pyproject.toml

As a developer, I want to set default YAML paths, output format, and minimum threshold in `pyproject.toml`, so that I do not have to pass the same CLI flags on every invocation.

## Acceptance Criteria

Requirements are tracked in `features/001-feature-coverage-plugin.feature.yaml`. The criteria below map directly to those requirement IDs.

### YAML_SCHEMA -- Feature YAML loading and validation

- `YAML_SCHEMA.1`: A valid `.feature.yaml` loads without error and its requirements appear in the coverage report.
- `YAML_SCHEMA.2`: A YAML file with missing required fields fails pytest collection with a clear error message that names the file.
- `YAML_SCHEMA.3`: Two YAML files that define the same feature name fail collection with a clear duplicate error.

### REQ_MARKER -- req() test annotation marker

- `REQ_MARKER.1`: A test annotated with `@pytest.mark.req("feature.COMP.N")` appears under that requirement in the report.
- `REQ_MARKER.2`: A single test may carry multiple requirement IDs; all are registered.
- `REQ_MARKER.3`: A `req()` marker that references an ID not present in any YAML emits a warning by default.
- `REQ_MARKER.4`: When `feature_coverage_strict = true`, an orphan `req()` marker causes collection to fail.

### COVERAGE_REPORT -- Coverage report generation

- `COVERAGE_REPORT.1`: `pytest --feature-coverage` produces a text report grouped by feature then component.
- `COVERAGE_REPORT.2`: The report is byte-identical across repeated runs for the same inputs.
- `COVERAGE_REPORT.3`: When no `.feature.yaml` files are found the report prints `Overall: 0/0` and exits zero.

### CI_THRESHOLD -- CI coverage threshold enforcement

- `CI_THRESHOLD.1`: When coverage is below `--feature-coverage-min`, pytest exits non-zero with a message stating actual vs required.
- `CI_THRESHOLD.2`: When coverage meets or exceeds the threshold, pytest exits zero.
- `CI_THRESHOLD.3`: The default threshold of 0 never triggers a failure.

### OUTPUT_FORMATS -- Machine-readable output formats

- `OUTPUT_FORMATS.1`: `--feature-coverage-format=json` writes valid structured JSON to stdout.
- `OUTPUT_FORMATS.2`: `--feature-coverage-format=markdown` writes a deterministic Markdown table to stdout.

### CONFIGURATION -- pyproject.toml configuration

- `CONFIGURATION.1`: `feature_yaml_paths` set in `pyproject.toml` is used when the CLI flag is absent.
- `CONFIGURATION.2`: `feature_coverage_min` set in `pyproject.toml` enforces a threshold when the CLI flag is absent.
- `CONFIGURATION.3`: Activating `--feature-coverage` without `feature_yaml_paths` configured emits a clear error.

## Dependencies

None. This is the foundational plugin; no upstream features.

## Notes

- Requirement IDs use the format `{feature-name}.{COMPONENT}.{number}`, e.g. `feature-coverage-plugin.YAML_SCHEMA.1`.
- Component names in `req()` markers are case-sensitive and must match the YAML exactly.
- The plugin is opt-in: it is inert unless `--feature-coverage` is passed.
- Zero-requirement components are valid and are excluded from the overall coverage percentage.
