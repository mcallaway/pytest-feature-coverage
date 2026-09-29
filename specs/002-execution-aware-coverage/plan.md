# Implementation Plan: Execution-Aware Feature Coverage

**Branch**: `fix/collection-vs-execution-coverage` | **Date**: 2026-09-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-execution-aware-coverage/spec.md`

**Note**: The spec directory is `specs/002-execution-aware-coverage` (sequential numbering after `specs/001-feature-coverage-plugin`), but per explicit task instruction this work continues on the already-checked-out `fix/collection-vs-execution-coverage` branch rather than a branch matching the spec directory name. The spec-kit `before_specify` branch-creation hook was intentionally skipped for this reason.

## Summary

The plugin currently grants requirement coverage credit at collection time: any collected test node ID carrying a matching `req()` marker counts as covering, regardless of whether the test later passes, fails, skips, xfails, or errors. This plan makes coverage execution-aware: a requirement is covered only when at least one associated node ID achieves a clean pass (per [contracts/coverage-semantics.md](contracts/coverage-semantics.md)).

The approach adds a new `outcomes.py` module (`OutcomeTracker`) fed by a `pytest_runtest_makereport` hookwrapper in `plugin.py`, and narrows `req_map` to only genuinely-passing node IDs immediately before `matrix.compute_coverage()` is called in `_compute_and_store_report()`. `matrix.py`, `scanner.py`, and all three reporters (`reporters/text.py`, `reporters/json.py`, `reporters/markdown.py`) require zero code changes: their existing contracts ("given a map of covering node IDs, compute/render coverage") already do the right thing once the map itself only contains genuinely-covering node IDs.

## Technical Context

**Language/Version**: Python 3.11+ (install floor per ADR-005; developed on 3.14)

**Primary Dependencies**: pytest (>=9.0.3, already a dependency) — no new dependencies. The new logic uses only `pytest.TestReport`/`pytest.CallInfo` attributes and standard library.

**Storage**: N/A — stateless per pytest session, held on `pytest.Config` as today.

**Testing**: pytest + `pytester` fixture for acceptance tests; plain unit tests with `types.SimpleNamespace` stubs for pure helper functions (no mocks), per `tests/AGENTS.md`.

**Target Platform**: Any platform running Python 3.11+.

**Project Type**: pytest plugin library (single project).

**Performance Goals**: Outcome tracking is O(1) dict updates per phase report and O(n) set membership filtering over already-small `req_map` lists; negligible overhead relative to running the test suite itself.

**Constraints**: No runtime dependencies beyond pytest, pydantic, and PyYAML (constitution rule). Must not change `req()` marker syntax, feature YAML schema, or any existing CLI/INI option.

**Scale/Scope**: One new module (`outcomes.py`, ~30 lines), one new hookimpl plus two small helper functions in `plugin.py`, no changes to `matrix.py`/`scanner.py`/reporters, new unit tests for `outcomes.py` and the new plugin helpers, new acceptance tests in `tests/integration/test_execution_coverage.py`, a new `EXECUTION_COVERAGE` component in the project's own dogfood feature YAML, and doc updates (README, `docs/features/001-...md`, ADR-003 pointer + new ADR-006 already drafted).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Honest Technical Judgment**: The xpass ambiguity called out in the feature request was resolved with an explicit, documented decision (ADR-006) rather than silently defaulting; complexity is justified (one new small module) rather than folding runtime tracking into `matrix.py`.
- **Investigate Before Acting**: `docs/decisions/002-plugin-hook-coverage-strategy.md` and `docs/decisions/003-what-tested-means.md` were read before design; existing hook patterns (`config`-scoped state, `# pragma: no cover` on hook `def` lines with helpers extracted and unit tested) are being reused, not reinvented.
- **Durable Shared Understanding**: spec.md, this plan, research.md, data-model.md, and the coverage-semantics contract were all written before implementation; ADR-006 records the one non-obvious tradeoff (xpass policy).
- **No runtime dependencies beyond pytest/pydantic/PyYAML**: satisfied — the new hook uses only `pytest.TestReport`/`CallInfo` attributes already available via the existing `pytest` dependency.
- **TDD mandatory**: satisfied by the task breakdown in `tasks.md` — acceptance tests are written first and confirmed to fail against the pre-fix implementation (explicit requirement from the feature request and FR-013), then unit tests for `outcomes.py` and plugin helpers, then the implementation.
- **Separate unit tests from integration tests**: this repo's actual convention (per `tests/AGENTS.md`, which is more specific than the constitution's "acceptance" wording) is `tests/unit/` and `tests/integration/`; new tests follow that existing, real convention rather than introducing a `tests/acceptance/` directory that does not otherwise exist in this repo.
- **No mocks in integration tests**: satisfied — new acceptance tests use real `pytester`-created files and real nested pytest runs, no mocking.

No violations requiring the Complexity Tracking table.

*Post-Phase-1 re-check*: Design artifacts (data-model.md, contracts/coverage-semantics.md, quickstart.md) do not introduce any new dependency, storage, or interface beyond what was evaluated above. Gate still passes.

## Project Structure

### Documentation (this feature)

```text
specs/002-execution-aware-coverage/
├── plan.md                        # This file
├── research.md                    # Phase 0 output
├── data-model.md                  # Phase 1 output
├── quickstart.md                  # Phase 1 output
├── contracts/
│   └── coverage-semantics.md      # Phase 1 output: outcome-table contract
├── checklists/
│   └── requirements.md            # Spec quality checklist
└── tasks.md                       # Phase 2 output (/speckit-tasks, not this command)
```

### Source Code (repository root)

```text
src/pytest_feature_coverage/
├── plugin.py            # + pytest_runtest_makereport hookwrapper, _apply_outcome_filter helper
├── outcomes.py           # NEW: OutcomeTracker, _NodeOutcome
├── matrix.py             # unchanged
├── scanner.py            # unchanged
└── reporters/
    ├── text.py            # unchanged
    ├── json.py            # unchanged
    └── markdown.py        # unchanged

features/
└── 001-feature-coverage-plugin.feature.yaml   # + EXECUTION_COVERAGE component

tests/
├── unit/
│   ├── test_outcomes.py         # NEW: unit tests for OutcomeTracker
│   └── test_plugin.py           # + tests for _apply_outcome_filter, updated existing test
└── integration/
    └── test_execution_coverage.py   # NEW: pytester acceptance tests (FR-013)

docs/
├── decisions/
│   ├── 003-what-tested-means.md    # annotated with pointer to ADR-006 (already done)
│   └── 006-execution-aware-covering-test.md  # NEW (already drafted, Proposed)
└── features/
    └── 001-feature-coverage-plugin.md   # + EXECUTION_COVERAGE acceptance criteria section

README.md   # + short note on execution-aware coverage semantics
```

**Structure Decision**: Single-project pytest plugin library (existing layout). No new top-level directories. This feature extends the existing `001-feature-coverage-plugin` feature's YAML/doc rather than introducing an unrelated new feature area (see spec.md Assumptions).

## Complexity Tracking

*No violations — table intentionally omitted.*

______________________________________________________________________

## Agentic Workflow: Project Memory

### TTL Metadata

- **TTL**: short -- this plan is actively being worked; update each session.
- **Author(s)**: Copilot CLI agentic session, 2026-09-29.
- **Audience(s)**: Fresh agent sessions resuming work; humans tracking progress.

### Project Context

- `docs/plans/README.md` "Current Focus" updated to point to `docs/plans/002-execution-aware-coverage.md`.
- Motivating feature doc: `docs/features/001-feature-coverage-plugin.md` (updated in place, this feature is an extension of it, not a new feature doc).
- `docs/design/codebase-map.md`: no structural change to the map's boundaries (plugin activation guard, schema/plugin separation, reporter isolation, unit/integration test layering all still hold); the map's Feature-to-Code Mapping table gets a row update for the new module.

### Decision Capture Reminder

ADR-006 (execution-aware "covering test" definition, including the xpass policy) was captured during `/speckit.specify`, before implementation began, per the "document decisions inline" rule. No further hard-to-reverse decisions are anticipated during implementation; if one arises (e.g. a pytest-version-specific report attribute quirk), it will be captured via `/speckit.agentic.document-decisions` at that point.

### Quality Gate

Rubric evaluation against `docs/plans/RUBRIC.md` will be run via `/speckit.agentic.apply-rubric` as part of this workflow's Standard-path steps.
