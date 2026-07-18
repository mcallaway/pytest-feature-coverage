# ADR-002: Plugin Hook Coverage Strategy

- **Status**: Accepted
- **Date**: 2026-07-18

## Context

`pytest-feature-coverage` is itself a pytest plugin, registered via the `project.entry-points.pytest11` entry point. This creates a structural conflict with `pytest-cov`: pytest loads all registered plugins **before** `pytest-cov` begins instrumenting source code. As a result, module-level code in `plugin.py` — including all `def` statements for hook functions — executes outside the coverage context and is reported as uncovered, even when those hooks are exercised by integration tests.

Two options were considered:

1. Accept the reported gap and annotate hook `def` lines with `# pragma: no cover`.
1. Restructure the plugin so hooks delegate immediately to extracted helper functions, then unit-test the helpers directly.

## Decision

Use **both strategies together**:

- Extract all non-trivial logic from hooks into private helper functions (`_is_active`, `_get_threshold`, `_get_known_requirement_ids`, `_compute_and_store_report`). These are unit-testable with plain `types.SimpleNamespace` stubs — no mocks required.
- Annotate the hook function `def` lines with `# pragma: no cover` and run coverage with `-p no:feature_coverage` so the module loads fresh within the coverage context. The hooks themselves are covered by the integration suite (`tests/integration/`), which exercises the full plugin lifecycle through `pytester`.
- Document the rationale for `pragma: no cover` in `pyproject.toml` so the exclusion is never mistaken for hidden untested code.

Reject mocks (`unittest.mock.MagicMock`) for unit tests. The helper functions only require attribute access and simple callables; `SimpleNamespace` with `lambda` fields is sufficient and makes the test intent explicit.

## Consequences

### Positive

- 100% line and branch coverage on all helper functions (the logic that can go wrong at runtime).
- `pragma: no cover` annotations are honest: they mark code that genuinely cannot be measured in the unit coverage run, not code that is untested.
- The design pressure to extract helpers from hooks improves the overall architecture — hooks become thin dispatchers.

### Negative

- The coverage run requires `-p no:feature_coverage` in `coverage.sh`, which is non-obvious. Future maintainers must understand why this flag is present.
- Hook behavior (argument parsing, early exit conditions) is only validated by the slower integration suite, not the fast unit suite.
- Any project that dogfoods its own pytest plugin will face this same entry-point timing constraint.
- The coverage run also requires a `pytest_addoption` hook in `tests/conftest.py` that re-registers all plugin INI options with a `try/except ValueError` guard. Without it, pytest rejects `feature_yaml_paths` and other settings when the plugin is disabled, producing `PytestConfigWarning` errors that obscure real failures.
