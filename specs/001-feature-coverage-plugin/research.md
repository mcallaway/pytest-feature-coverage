# Research: Feature Coverage Plugin

**Date**: 2025-05-19\
**Feature**: [spec.md](spec.md)

## 1. pytest Plugin Registration & Hooks

### Decision: Use `pyproject.toml` entry point + standard hook sequence

**Rationale**: This is the official pytest plugin registration mechanism. Auto-discovered by pytest at startup.

**Entry point**:

```toml
[project.entry-points.pytest11]
feature_coverage = "pytest_feature_coverage.plugin"
```

**Hook sequence for this plugin**:

1. `pytest_addoption` — register `--feature-coverage`, `--feature-coverage-min`, `--feature-coverage-format`
1. `pytest_configure` — register `req` marker; load and validate YAML files; store state on `config`
1. `pytest_collection_modifyitems` — scan `req()` markers from collected test items
1. `pytest_terminal_summary` — generate and print the coverage report
1. `pytest_sessionfinish` — enforce threshold via exit code

**Alternatives considered**:

- `conftest.py`-based plugin: rejected because this must be installable via pip as a standalone package
- `pytest_collect_file` hook: rejected because we don't collect YAML as test items — we read them as metadata

## 2. Custom Marker Pattern

### Decision: Single `req` marker with variadic positional args

**Rationale**: A test may cover multiple requirements. Using `*args` allows `@pytest.mark.req("a.B.1", "a.B.2")` in a single decorator.

**Pattern**:

```python
# Registration
config.addinivalue_line("markers", "req(*ids): Associate test with requirement IDs")

# Collection
for marker in item.iter_markers(name="req"):
    for req_id in marker.args:
        # Map req_id → test node ID
```

**Alternatives considered**:

- Multiple stacked `@pytest.mark.req("id")` decorators: works but verbose; `iter_markers` handles both patterns naturally
- A single marker with a list kwarg `req(ids=["a", "b"])`: rejected as less ergonomic

## 3. YAML Schema Validation with Pydantic v2

### Decision: Load with PyYAML `safe_load`, validate with Pydantic `BaseModel`

**Rationale**: Pydantic v2 provides clear validation errors with field paths. Combined with wrapping to include the file path, this satisfies SC-002 (clear error naming file + violation).

**Pattern**:

```python
from pydantic import BaseModel, ValidationError
import yaml

class RequirementModel(BaseModel):
    # number → description mapping
    pass

class ComponentModel(BaseModel):
    name: str
    requirements: dict[int, str]

class FeatureModel(BaseModel):
    id: str
    name: str

class FeatureFile(BaseModel):
    feature: FeatureModel
    components: dict[str, ComponentModel]
```

**Error reporting**: Catch `ValidationError`, prepend file path, re-raise as a pytest `UsageError` to fail collection cleanly.

**Alternatives considered**:

- JSON Schema: rejected — adds a dependency and less Pythonic
- `dataclasses` + manual validation: rejected — Pydantic gives free error messages and nested validation
- `strictyaml`: rejected — adds dependency; PyYAML + Pydantic covers everything needed

## 4. Plugin Testing with pytester

### Decision: Use `pytester` fixture for acceptance tests; direct unit tests for internal modules

**Rationale**: `pytester` runs pytest in a subprocess, providing true end-to-end testing of the plugin. Unit tests call module functions directly for speed.

**Key patterns**:

- `pytester.makepyfile()` — create test files with `req()` markers
- `pytester.makefile(".feature.yaml", ...)` — create feature YAML fixtures
- `pytester.makepyprojecttoml(...)` — configure `feature_yaml_paths` etc.
- `pytester.runpytest("--feature-coverage")` — invoke with plugin flags
- `result.stdout.fnmatch_lines(...)` — assert report output
- `result.ret` — assert exit code

**Note**: `pytester` requires `pytest_plugins = ["pytester"]` in conftest or the test file.

## 5. Exit Code Enforcement

### Decision: Use `pytest_sessionfinish` to modify `session.exitstatus`

**Rationale**: This hook runs after all tests complete and the terminal summary is printed. We can check coverage against threshold and set the exit code without interrupting the test session.

**Pattern**:

```python
@pytest.hookimpl
def pytest_sessionfinish(session, exitstatus):
    if coverage_below_threshold:
        session.exitstatus = ExitCode.TESTS_FAILED
```

**Alternatives considered**:

- `pytest.exit()` in `pytest_terminal_summary`: rejected — aborts before the summary is fully printed
- Raising `pytest.UsageError`: rejected — that's for config errors, not coverage failures
- Custom exit code (e.g., 6): rejected — non-standard; `TESTS_FAILED=1` is universally understood by CI

## 6. Activation Model

### Decision: `--feature-coverage` flag activates everything; sub-flags ignored without it

**Rationale**: Clarification session confirmed: the plugin does nothing unless `--feature-coverage` is explicitly passed. This avoids interfering with normal test runs.

**Flow**:

1. If `--feature-coverage` not present → plugin is inert (all hooks return early)
1. If present → load YAML, scan markers, compute matrix, report, check threshold
