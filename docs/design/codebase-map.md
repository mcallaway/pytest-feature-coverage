# Codebase Map

Last updated: 2025-05-20

## Directory Overview

```text
pytest-feature-coverage/
├── src/pytest_feature_coverage/   # Plugin source (installed as pytest11 entry point)
│   ├── plugin.py                  # Hook implementations, CLI/INI registration
│   ├── schema.py                  # Pydantic models, YAML loading, validation
│   ├── scanner.py                 # req() marker collection, orphan detection
│   ├── matrix.py                  # Coverage computation (CoverageEntry, CoverageReport)
│   └── reporters/                 # Output formatters
│       ├── text.py                # Default human-readable report
│       ├── json.py                # Machine-readable JSON output
│       └── markdown.py            # Markdown table output
├── tests/
│   ├── conftest.py                # pytester registration, shared fixtures
│   ├── data/                      # Test fixtures (reference.feature.yaml)
│   ├── unit/                      # Direct function-level tests
│   └── acceptance/                # pytester-based integration tests
├── specs/001-feature-coverage-plugin/  # Spec Kit feature artifacts
│   ├── spec.md                    # Feature specification (user stories, FRs)
│   ├── plan.md                    # Implementation plan
│   ├── tasks.md                   # Task breakdown (T001-T045)
│   ├── research.md                # Technical research notes
│   ├── data-model.md              # Entity definitions and relationships
│   └── contracts/cli.md           # CLI/output format contracts
├── docs/                          # Project documentation
│   ├── design/                    # Architecture and design docs
│   ├── decisions/                 # ADRs
│   ├── features/                  # Feature descriptions
│   └── guides/                    # How-to guides
├── .mise/tasks/                   # Task runner scripts (test, dev, code)
└── .github/                       # CI workflows, Copilot instructions, prompts
```

## Source Packages

| Package/Module                               | Purpose                                                                                                                                   | Key Files               |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| `pytest_feature_coverage.plugin`             | pytest hook wiring, CLI/INI options, activation guard, threshold resolution                                                               | `plugin.py`             |
| `pytest_feature_coverage.schema`             | Pydantic models (`FeatureFileModel`, `ComponentModel`, `FeatureModel`), `load_feature_file()`, `load_all_features()`, duplicate detection | `schema.py`             |
| `pytest_feature_coverage.scanner`            | `scan_requirements()` from `req()` markers, `find_orphans()`                                                                              | `scanner.py`            |
| `pytest_feature_coverage.matrix`             | `compute_coverage()`, `CoverageEntry`, `CoverageReport` dataclasses                                                                       | `matrix.py`             |
| `pytest_feature_coverage.reporters.text`     | `render_text()` — checkmark/X format with test node IDs                                                                                   | `reporters/text.py`     |
| `pytest_feature_coverage.reporters.json`     | `render_json()` — structured JSON matching contract                                                                                       | `reporters/json.py`     |
| `pytest_feature_coverage.reporters.markdown` | `render_markdown()` — table format with summary                                                                                           | `reporters/markdown.py` |

## Feature-to-Code Mapping

| Feature                     | Primary Code                                                  | Tests                                                                                                      | Design Doc                   |
| --------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------- |
| YAML schema loading (US1)   | `schema.py`                                                   | `tests/unit/test_schema.py`, `tests/acceptance/test_plugin_integration.py`                                 | `specs/.../data-model.md`    |
| req() marker scanning (US2) | `scanner.py`, `plugin.py` (collection hook)                   | `tests/unit/test_scanner.py`, `tests/acceptance/test_plugin_integration.py`                                | `specs/.../spec.md`          |
| Coverage report (US3)       | `matrix.py`, `reporters/text.py`, `plugin.py` (terminal hook) | `tests/unit/test_matrix.py`, `tests/unit/test_reporters.py`, `tests/acceptance/test_plugin_integration.py` | `specs/.../contracts/cli.md` |
| CI threshold (US4)          | `plugin.py` (sessionfinish hook)                              | `tests/acceptance/test_ci_threshold.py`                                                                    | `specs/.../contracts/cli.md` |
| JSON/Markdown formats (US5) | `reporters/json.py`, `reporters/markdown.py`                  | `tests/unit/test_reporters.py`, `tests/acceptance/test_plugin_integration.py`                              | `specs/.../contracts/cli.md` |
| Config resolution (US6)     | `plugin.py` (addoption/configure)                             | `tests/acceptance/test_plugin_integration.py`                                                              | `specs/.../contracts/cli.md` |

## Boundaries

- **Plugin activation**: All hooks early-return via `_is_active(config)` when `--feature-coverage` is not passed — the plugin is completely inert by default.
- **Schema ↔ Plugin**: `schema.py` is a pure library (no pytest imports); `plugin.py` calls it during `pytest_configure` and stores results on `config`.
- **Reporter isolation**: Each reporter module exposes a single `render_*()` function taking a `CoverageReport` — no pytest coupling.
- **Test layering**: Unit tests call module functions directly (no subprocess); acceptance tests use `pytester` for full end-to-end validation.

## Entry Points

- **Plugin**: `[project.entry-points.pytest11] feature_coverage = "pytest_feature_coverage.plugin"`
- **CLI activation**: `pytest --feature-coverage [--feature-coverage-format=text|json|markdown] [--feature-coverage-min=N]`
- **Tests**: `mise run test:unit`, `mise run test:acceptance`, `mise run test:all`
- **Lint**: `mise run test:lint` (ruff), `mise run test:typecheck` (ty)
