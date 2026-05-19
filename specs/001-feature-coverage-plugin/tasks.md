# Tasks: Feature Coverage Plugin

**Input**: Design documents from `specs/001-feature-coverage-plugin/`\
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Included (TDD approach per constitution Quality Gates and FR-014).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Source**: `src/pytest_feature_coverage/`
- **Tests**: `tests/unit/`, `tests/acceptance/`
- **Fixtures**: `tests/data/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and plugin entry point

- [x] T001 Add runtime dependencies (pydantic, pyyaml) and pytest entry point to pyproject.toml
- [x] T002 [P] Create reference feature YAML fixture in tests/data/reference.feature.yaml (FR-014)
- [x] T003 [P] Create tests/conftest.py with pytester plugin registration
- [x] T004 [P] Create src/pytest_feature_coverage/reporters/\_\_init\_\_.py (empty package init)

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core plugin skeleton — all user stories depend on this being wired up

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Implement plugin.py with pytest_addoption (register --feature-coverage, --feature-coverage-format, --feature-coverage-min) and pytest_configure (register req marker, register INI options) in src/pytest_feature_coverage/plugin.py
- [x] T006 Implement early-return guard in all hooks when --feature-coverage is not active in src/pytest_feature_coverage/plugin.py

**Checkpoint**: Plugin installs, registers CLI options, and is inert when flag not passed

## Phase 3: User Story 1 - Define Requirements in YAML (Priority: P1) MVP

**Goal**: Load and validate `*.feature.yaml` files at collection time with clear error messages

**Independent Test**: Create valid/invalid YAML, run pytest, verify load success or clear error

### Tests for User Story 1

- [x] T007 [P] [US1] Write unit tests for schema validation (valid YAML, missing fields, invalid types) in tests/unit/test_schema.py
- [x] T008 [P] [US1] Write unit tests for YAML loading from directory (file discovery, path resolution) in tests/unit/test_schema.py

### Implementation for User Story 1

- [x] T009 [US1] Implement Pydantic models (FeatureModel, ComponentModel, FeatureFileModel) in src/pytest_feature_coverage/schema.py
- [x] T010 [US1] Implement load_feature_file() and load_all_features() functions in src/pytest_feature_coverage/schema.py
- [x] T011 [US1] Wire schema loading into pytest_configure hook: discover YAML paths from config, load and validate, store on config object in src/pytest_feature_coverage/plugin.py
- [x] T012 [US1] Implement duplicate feature name detection across loaded files in src/pytest_feature_coverage/schema.py
- [x] T013 [US1] Write acceptance test: valid YAML loads without error in tests/acceptance/test_plugin_integration.py
- [x] T014 [US1] Write acceptance test: invalid YAML fails collection with clear error in tests/acceptance/test_plugin_integration.py
- [x] T015 [US1] Write acceptance test: missing feature_yaml_paths config emits error in tests/acceptance/test_plugin_integration.py

**Checkpoint**: YAML files load and validate; errors are clear and name the file

## Phase 4: User Story 2 - Annotate Tests with Requirement Markers (Priority: P1)

**Goal**: Collect `req()` markers from test items and map them to requirement IDs

**Independent Test**: Annotate tests with `req()`, verify markers are collected correctly

### Tests for User Story 2

- [x] T016 [P] [US2] Write unit tests for scanner (single marker, multiple args, multiple markers, no markers) in tests/unit/test_scanner.py

### Implementation for User Story 2

- [x] T017 [US2] Implement scan_requirements() function in src/pytest_feature_coverage/scanner.py
- [x] T018 [US2] Wire scanner into pytest_collection_modifyitems hook in src/pytest_feature_coverage/plugin.py
- [x] T019 [US2] Implement orphan marker detection (warning by default, error if strict) in src/pytest_feature_coverage/scanner.py
- [x] T020 [US2] Write acceptance test: req() markers collected and associated correctly in tests/acceptance/test_plugin_integration.py
- [x] T021 [US2] Write acceptance test: orphan marker emits warning in tests/acceptance/test_plugin_integration.py

**Checkpoint**: Markers are scanned; orphan detection works; warning/error behavior correct

## Phase 5: User Story 3 - Generate Coverage Report (Priority: P1)

**Goal**: Compute coverage matrix and print deterministic text report

**Independent Test**: Run `pytest --feature-coverage` and verify text output matches expected format

### Tests for User Story 3

- [x] T022 [P] [US3] Write unit tests for matrix computation (covered, uncovered, many-to-many, zero-req components) in tests/unit/test_matrix.py
- [x] T023 [P] [US3] Write unit tests for text reporter output format in tests/unit/test_reporters.py

### Implementation for User Story 3

- [x] T024 [US3] Implement CoverageMatrix.compute() in src/pytest_feature_coverage/matrix.py
- [x] T025 [US3] Implement TextReporter in src/pytest_feature_coverage/reporters/text.py
- [x] T026 [US3] Wire matrix computation and text report into pytest_terminal_summary hook in src/pytest_feature_coverage/plugin.py
- [x] T027 [US3] Write acceptance test: full text report output matches expected format in tests/acceptance/test_plugin_integration.py
- [x] T028 [US3] Write acceptance test: determinism (identical output on repeated runs) in tests/acceptance/test_plugin_integration.py
- [x] T029 [US3] Write acceptance test: no YAML files found emits clear message in tests/acceptance/test_plugin_integration.py

**Checkpoint**: MVP complete — `pytest --feature-coverage` shows a correct text coverage report

## Phase 6: User Story 4 - CI Coverage Threshold (Priority: P2)

**Goal**: Exit non-zero when coverage falls below `--feature-coverage-min`

**Independent Test**: Run pytest with threshold above actual coverage, verify exit code

### Tests for User Story 4

- [ ] T030 [P] [US4] Write acceptance tests for threshold behavior (below, above, zero default) in tests/acceptance/test_ci_threshold.py

### Implementation for User Story 4

- [ ] T031 [US4] Implement threshold check in pytest_sessionfinish hook in src/pytest_feature_coverage/plugin.py
- [ ] T032 [US4] Add "FAILED: Feature coverage X% is below minimum Y%" message to text reporter in src/pytest_feature_coverage/reporters/text.py

**Checkpoint**: CI gating works; exit code reflects coverage vs threshold

## Phase 7: User Story 5 - Machine-Readable Output Formats (Priority: P2)

**Goal**: Generate JSON and Markdown coverage reports

**Independent Test**: Run with `--feature-coverage-format=json` and verify valid JSON structure

### Tests for User Story 5

- [ ] T033 [P] [US5] Write unit tests for JSON reporter (structure matches contract) in tests/unit/test_reporters.py
- [ ] T034 [P] [US5] Write unit tests for Markdown reporter (table format matches contract) in tests/unit/test_reporters.py

### Implementation for User Story 5

- [ ] T035 [US5] Implement JsonReporter in src/pytest_feature_coverage/reporters/json.py
- [ ] T036 [US5] Implement MarkdownReporter in src/pytest_feature_coverage/reporters/markdown.py
- [ ] T037 [US5] Wire format selection into pytest_terminal_summary hook in src/pytest_feature_coverage/plugin.py
- [ ] T038 [US5] Write acceptance test: JSON output is valid and matches contract schema in tests/acceptance/test_plugin_integration.py
- [ ] T039 [US5] Write acceptance test: Markdown output matches contract format in tests/acceptance/test_plugin_integration.py

**Checkpoint**: All three output formats work correctly

## Phase 8: User Story 6 - Configuration via pyproject.toml (Priority: P3)

**Goal**: INI options provide defaults; CLI flags override them

**Independent Test**: Set values in pyproject.toml, verify they take effect without CLI flags

### Tests for User Story 6

- [ ] T040 [P] [US6] Write acceptance tests for INI option precedence (config defaults, CLI overrides) in tests/acceptance/test_plugin_integration.py

### Implementation for User Story 6

- [ ] T041 [US6] Ensure all INI options are registered with correct types and defaults in src/pytest_feature_coverage/plugin.py
- [ ] T042 [US6] Implement config resolution: CLI flag > INI option > hardcoded default in src/pytest_feature_coverage/plugin.py

**Checkpoint**: Configuration works from pyproject.toml with CLI override

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, documentation, and quality verification

- [ ] T043 Verify all ruff lint and ty type-check passes across src/ and tests/
- [ ] T044 Verify determinism: run acceptance test suite twice, confirm identical output
- [ ] T045 Update README.md with usage documentation and installation instructions

## Dependencies

```text
Phase 1 (Setup) → Phase 2 (Foundation) → Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3)
                                                                              ↓
                                                           Phase 6 (US4) ←────┘
                                                           Phase 7 (US5) ←────┘
                                                                              ↓
                                                           Phase 8 (US6) ←────┘
                                                                              ↓
                                                           Phase 9 (Polish) ←─┘
```

- US1 → US2: scanner needs schema (loaded features) to detect orphan markers
- US2 → US3: matrix needs both requirements (US1) and marker data (US2)
- US3 → US4: threshold check needs coverage percentage from matrix
- US3 → US5: JSON/Markdown reporters need the same matrix data
- US6 can be done after US3 (just wires config → existing parameters)

## Parallel Execution Opportunities

Within each phase, tasks marked [P] can run in parallel:

- **Phase 1**: T002, T003, T004 (independent file creation)
- **Phase 3**: T007, T008 (independent test files)
- **Phase 4**: T016 (independent test file)
- **Phase 5**: T022, T023 (independent test files)
- **Phase 6**: T030 (independent test file)
- **Phase 7**: T033, T034 (independent test files)
- **Phase 8**: T040 (independent test file)

## Implementation Strategy

- **MVP**: Phases 1-5 (Setup + US1 + US2 + US3 = working text coverage report)
- **Full feature**: Phases 6-8 (threshold, formats, config)
- **Ship**: Phase 9 (polish)

## Agentic Workflow: Post-Implementation Checklist

> This section is added by the agentic-workflow preset. It prompts for review and documentation steps after the tasks are complete.

### After All Tasks Complete

1. **Code Review**: Run `/speckit.agentic.code-review` to evaluate the implementation against the spec's acceptance criteria.

1. **Design Alignment**: If architectural changes were made, run `/speckit.agentic.review-alignment` to check for drift between `docs/design/` and the actual implementation.

1. **Decision Capture**: If any trade-offs or technology choices were made during implementation, run `/speckit.agentic.document-decisions` to capture them as ADRs in `docs/decisions/`.

1. **Plan Close-out**: Run `/speckit.agentic.close-plan` to finalize the plan and move it to the completed section of `docs/plans/README.md`.

1. **Lesson Extraction**: If reusable patterns emerged, run `/speckit.agentic.extract-lessons` to promote them to `docs/guides/` or `docs/design/`.
