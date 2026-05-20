# Implementation Plan: Feature Coverage Plugin

- **Branch**: `feat/001-feature-coverage-plugin` | **Date**: 2025-05-19 | **Spec**: [spec.md](spec.md)
- **Input**: Feature specification from `specs/001-feature-coverage-plugin/spec.md`
- **Status**: COMPLETE (2025-05-20)

## Summary

A pytest plugin that loads requirements from `*.feature.yaml` files, collects `req()` markers from tests, computes a coverage matrix, and reports which requirements are covered. Enforces a configurable coverage threshold for CI gating.

## Technical Context

**Language/Version**: Python >=3.14\
**Primary Dependencies**: pytest >=8.4, pydantic >=2.0, PyYAML\
**Storage**: N/A (file-based, read-only)\
**Testing**: pytest (self-testing plugin)\
**Target Platform**: Any OS with Python >=3.14\
**Project Type**: Library (pytest plugin)\
**Performance Goals**: Collection overhead \<1s for 100 YAML files\
**Constraints**: Zero runtime dependencies beyond pytest+pydantic+PyYAML; no network; deterministic output\
**Scale/Scope**: Single repository; dozens of feature YAML files; hundreds of requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle                           | Status | Notes                                        |
| ----------------------------------- | ------ | -------------------------------------------- |
| I. Honest Technical Judgment        | PASS   | No ambiguity in technical choices            |
| II. Investigate Before Acting       | PASS   | Design doc provides clear architecture       |
| III. Durable Shared Understanding   | PASS   | Spec fully clarified, all questions resolved |
| Development Standards: YAGNI        | PASS   | Minimal architecture; only what's needed     |
| Development Standards: Dependencies | PASS   | Only pytest + pydantic + PyYAML              |
| Quality Gates: TDD                  | PASS   | FR-014 mandates fixture-first approach       |
| Quality Gates: Test separation      | PASS   | Unit + acceptance test structure             |

**Gate Result**: PASS — no violations. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/001-feature-coverage-plugin/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI interface contract)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
└── pytest_feature_coverage/
    ├── __init__.py          # Package init, version
    ├── plugin.py            # pytest plugin hooks (entry point)
    ├── schema.py            # Pydantic models for feature YAML
    ├── scanner.py           # Collects req() markers from test items
    ├── matrix.py            # Cross-references requirements ↔ tests
    └── reporters/
        ├── __init__.py      # Reporter base/registry
        ├── text.py          # Terminal output (default)
        ├── json.py          # Machine-readable JSON
        └── markdown.py      # Deterministic markdown table

tests/
├── data/
│   └── reference.feature.yaml  # FR-014: comprehensive schema fixture
├── unit/
│   ├── test_schema.py          # Pydantic model validation
│   ├── test_scanner.py         # req() marker collection
│   ├── test_matrix.py          # Coverage matrix computation
│   └── test_reporters.py       # Output formatting
└── acceptance/
    ├── test_plugin_integration.py  # End-to-end pytest invocation
    └── test_ci_threshold.py        # Exit code behavior
```

**Structure Decision**: Single project (src layout). The plugin architecture follows the design doc's module separation: schema → scanner → matrix → reporters, orchestrated by plugin.py.

## Complexity Tracking

No violations to justify — architecture is straightforward.

## Agentic Workflow: Project Memory

> This section is added by the agentic-workflow preset. It connects plans to the project-level knowledge in `docs/`.

### TTL Metadata

- **TTL**: short -- this plan is actively being worked; update each session.
- **Author(s)**: speckit.plan
- **Audience(s)**: Fresh agent sessions resuming work; humans tracking progress.

### Project Context

- `docs/plans/README.md` -- updated to point to this plan.
- `docs/features/` -- no separate feature doc needed; spec is in `specs/001-feature-coverage-plugin/spec.md`.
- `docs/design/` -- no existing architecture to update; this is greenfield.

### Decision Capture Reminder

During implementation, watch for decisions that should become ADRs:

- Technology choices that are hard to reverse
- Trade-offs between competing approaches
- Constraints discovered during research

Use `/speckit.agentic.document-decisions` to capture these as they arise.

### Quality Gate

The `after_plan` hook will offer to evaluate this plan against `docs/plans/RUBRIC.md`. You can also run it manually: `/speckit.agentic.apply-rubric docs/plans/RUBRIC.md`
