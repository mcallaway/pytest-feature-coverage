# CLI Interface Contract: pytest-feature-coverage

**Date**: 2025-05-19\
**Type**: CLI (pytest plugin options)

## Command-Line Options

All options are registered via `pytest_addoption` and available when the plugin is installed.

### `--feature-coverage`

| Property    | Value                             |
| ----------- | --------------------------------- |
| Type        | Flag (boolean)                    |
| Default     | `false` (not present)             |
| Required    | Yes — activates the plugin        |
| Description | Enable feature coverage reporting |

When absent, the plugin is completely inert (no YAML loading, no marker scanning, no report).

### `--feature-coverage-format`

| Property    | Value                                 |
| ----------- | ------------------------------------- |
| Type        | Choice                                |
| Choices     | `text`, `json`, `markdown`            |
| Default     | `text`                                |
| Requires    | `--feature-coverage`                  |
| Description | Output format for the coverage report |

### `--feature-coverage-min`

| Property    | Value                                               |
| ----------- | --------------------------------------------------- |
| Type        | Integer (0-100)                                     |
| Default     | `0`                                                 |
| Requires    | `--feature-coverage`                                |
| Description | Minimum coverage percentage; exit non-zero if below |

## INI Options (pyproject.toml)

Configured under `[tool.pytest.ini_options]`. CLI flags override INI values.

| Option                    | Type      | Default    | Description                                      |
| ------------------------- | --------- | ---------- | ------------------------------------------------ |
| `feature_yaml_paths`      | list[str] | (required) | Directories to search for `*.feature.yaml` files |
| `feature_coverage_format` | str       | `"text"`   | Default output format                            |
| `feature_coverage_min`    | int       | `0`        | Default minimum coverage threshold               |
| `feature_coverage_strict` | bool      | `false`    | Treat orphan `req()` markers as errors           |

## Exit Codes

| Code | Meaning                                                |
| ---- | ------------------------------------------------------ |
| 0    | All tests passed AND coverage >= threshold             |
| 1    | Tests failed OR coverage < threshold                   |
| 2    | Interrupted                                            |
| 3    | Internal error                                         |
| 4    | Usage error (e.g., no `feature_yaml_paths` configured) |

## Output Formats

### Text (default)

```text
Feature: {feature.name} ({feature.id})
  {COMPONENT}
    ✓ {number}: {description}
         → {test_nodeid}
    ✗ {number}: {description}
         → (no covering test)

  Coverage: {covered}/{total} ({percentage}%)

Overall: {covered}/{total} requirements covered ({percentage}%)
```

- Features sorted alphabetically by name
- Components sorted alphabetically by key
- Requirements sorted numerically

### JSON

```json
{
  "features": [
    {
      "id": "002",
      "name": "contract-validation",
      "components": [
        {
          "key": "STRUCTURE",
          "name": "Contract YAML structure",
          "requirements": [
            {
              "number": 1,
              "description": "Contract YAML files have all required fields",
              "composite_id": "contract-validation.STRUCTURE.1",
              "covered": true,
              "covering_tests": ["test_contracts.py::test_required_fields"]
            }
          ]
        }
      ],
      "coverage": {"covered": 2, "total": 3, "percentage": 66.7}
    }
  ],
  "overall": {"covered": 4, "total": 7, "percentage": 57.1},
  "orphan_markers": []
}
```

### Markdown

```markdown
# Feature Coverage Report

## contract-validation (002)

### STRUCTURE

| # | Requirement | Status | Tests |
|---|-------------|--------|-------|
| 1 | Contract YAML files have all required fields | ✓ | `test_contracts.py::test_required_fields` |
| 2 | Ontology class references | ✗ | — |

### Summary

| Feature | Covered | Total | % |
|---------|---------|-------|---|
| contract-validation | 4 | 7 | 57.1% |
| **Overall** | **4** | **7** | **57.1%** |
```

## Error Messages

| Condition                          | Output                                                                                                                                |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| No `feature_yaml_paths` configured | `ERROR: feature_yaml_paths not configured in pyproject.toml. Add [tool.pytest.ini_options] feature_yaml_paths = ["path/to/features"]` |
| Invalid YAML schema                | `ERROR: {filepath}: Validation failed\n  {field_path}: {message}`                                                                     |
| Duplicate feature name             | `ERROR: Duplicate feature name '{name}' in {file1} and {file2}`                                                                       |
| Duplicate requirement ID           | `ERROR: Duplicate requirement ID '{composite_id}' in {file1} and {file2}`                                                             |
| Orphan marker (warning)            | `WARNING: req() marker '{id}' in {test_nodeid} does not match any known requirement`                                                  |
| Orphan marker (strict)             | `ERROR: req() marker '{id}' in {test_nodeid} does not match any known requirement (strict mode)`                                      |
| Coverage below threshold           | `FAILED: Feature coverage {actual}% is below minimum {threshold}%`                                                                    |
