# Usage Guide: pytest-feature-coverage

## Introduction

This guide is for developers who want to track which requirements are covered by tests. After reading it you will be able to define requirements in YAML, annotate tests with markers, and generate coverage reports in multiple formats.

## Prerequisites

- Python >= 3.14
- pytest >= 7.0
- `pytest-feature-coverage` installed (e.g., via `pip install -e .` or as a dependency)

> **Note:** To install from Artifactory, your project must have the index configured in `pyproject.toml`:
>
> ```toml
> [[tool.uv.index]]
> name = "shared-python-prod-shared"
> url = "https://artifactory.bayer.com/artifactory/api/pypi/shared-python-prod-shared/simple"
> ```
>
> Then add the dependency:
>
> ```bash
> uv add pytest-feature-coverage --index shared-python-prod-shared --dev
> ```

## Step 1: Define requirements in YAML

Create `*.feature.yaml` files in a dedicated directory. Each file declares one feature with its components and numbered requirements.

```yaml
# features/authentication.feature.yaml
feature:
  id: "001"
  name: authentication

components:
  LOGIN:
    name: Login flow
    requirements:
      1: Accepts valid credentials
      2: Rejects invalid credentials
      3: Locks account after 5 failed attempts

  SESSION:
    name: Session management
    requirements:
      1: Issues a session token on successful login
      2: Expires session after configured timeout
```

### Rules

- `feature.name` must be unique across all YAML files (duplicate names cause a collection error)
- Component keys are case-sensitive and used verbatim in requirement IDs
- A component with zero requirements is valid (shows 0/0 in the report)
- Requirement numbers must be integers

## Step 2: Configure pytest

Add the plugin configuration to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
feature_yaml_paths = ["features"]
```

This tells the plugin where to find `*.feature.yaml` files. The path is relative to the project root.

### Optional settings

```toml
[tool.pytest.ini_options]
feature_yaml_paths = ["features", "docs/specs"]  # multiple directories
feature_coverage_format = "text"                  # default output format
feature_coverage_min = 80                         # fail if below 80%
feature_coverage_strict = true                    # treat orphan markers as errors
```

All INI settings can be overridden by CLI flags.

## Step 3: Annotate tests with req() markers

Use `@pytest.mark.req()` to declare which requirements a test covers. The argument is a composite ID: `{feature-name}.{COMPONENT}.{number}`.

```python
import pytest


@pytest.mark.req("authentication.LOGIN.1")
def test_valid_credentials_accepted():
    result = login("user@example.com", "correct-password")
    assert result.success


@pytest.mark.req("authentication.LOGIN.2", "authentication.LOGIN.3")
def test_invalid_credentials_rejected_and_lockout():
    for _ in range(5):
        result = login("user@example.com", "wrong")
    assert result.locked
```

### Marker rules

- A test can cover multiple requirements (pass multiple IDs)
- Multiple tests can cover the same requirement (many-to-many)
- Matching is case-sensitive — `LOGIN` must match the YAML key exactly
- Orphan markers (IDs that don't match any YAML requirement) emit a warning by default

## Step 4: Run with coverage reporting

The plugin is inert unless explicitly activated:

```shell
pytest --feature-coverage
```

### Output formats

```shell
# Human-readable text (default)
pytest --feature-coverage

# Machine-readable JSON
pytest --feature-coverage --feature-coverage-format=json

# Markdown table (for docs or PRs)
pytest --feature-coverage --feature-coverage-format=markdown
```

### CI threshold enforcement

```shell
# Fail the build if coverage drops below 80%
pytest --feature-coverage --feature-coverage-min=80
```

Exit code 2 is returned when coverage is below the threshold (distinct from exit code 1 which means tests failed).

## Example output

### Text format

```text
Feature: authentication (001)
  LOGIN
    ✓ 1: Accepts valid credentials
         → tests/test_auth.py::test_valid_credentials_accepted
    ✓ 2: Rejects invalid credentials
         → tests/test_auth.py::test_invalid_credentials_rejected_and_lockout
    ✓ 3: Locks account after 5 failed attempts
         → tests/test_auth.py::test_invalid_credentials_rejected_and_lockout
  SESSION
    ✗ 1: Issues a session token on successful login
         → (no covering test)
    ✗ 2: Expires session after configured timeout
         → (no covering test)
  Coverage: 3/5 (60.0%)

Overall: 3/5 requirements covered (60.0%)
```

### JSON format

```json
{
  "features": [
    {
      "id": "001",
      "name": "authentication",
      "components": [...],
      "coverage": {"covered": 3, "total": 5, "percentage": 60.0}
    }
  ],
  "overall": {"covered": 3, "total": 5, "percentage": 60.0},
  "orphan_markers": []
}
```

## Troubleshooting

### "feature_yaml_paths INI option is required"

You activated `--feature-coverage` but didn't configure where to find YAML files. Add `feature_yaml_paths` to your `[tool.pytest.ini_options]`.

### Orphan marker warnings

A `req()` marker references an ID that doesn't exist in any YAML file. Check for typos in the composite ID. Set `feature_coverage_strict = true` to make these errors instead of warnings.

### Plugin seems to do nothing

The plugin is inert without `--feature-coverage`. Make sure you pass the flag.

## See also

- [Spec](../../specs/001-feature-coverage-plugin/spec.md) — full feature specification
- [CLI contract](../../specs/001-feature-coverage-plugin/contracts/cli.md) — detailed option and output format reference
- [Data model](../../specs/001-feature-coverage-plugin/data-model.md) — entity definitions and YAML schema
