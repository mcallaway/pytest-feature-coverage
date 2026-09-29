---
description: Task list for Execution-Aware Feature Coverage
---

# Tasks: Execution-Aware Feature Coverage

**Input**: Design documents from `/specs/002-execution-aware-coverage/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/coverage-semantics.md, quickstart.md

**Tests**: Explicitly requested by the feature request and mandatory per this project's TDD convention (`tests/AGENTS.md`, constitution "Quality Gates"). The feature request additionally requires the new pytester acceptance tests to demonstrably fail against the current collection-only implementation before the fix, then pass after.

**Organization**: Tasks are grouped by user story (spec.md priorities P1-P3) to enable independent verification of each story. User Story 1 (P1) delivers the entire underlying mechanism; User Stories 2-4 are, by design (see `research.md`'s "Where to apply the outcome filter" decision), already satisfied once User Story 1's mechanism exists — their phases add acceptance-test coverage only, with no new production code expected. This is called out explicitly per task, not left implicit.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)

## Phase 1: Setup

**Purpose**: Confirm a clean starting point before any change.

- [x] T001 Run `mise run test:unit` and `mise run test:integration` from repo root and confirm the existing suite is green before making any changes (no files modified by this task).

______________________________________________________________________

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build and unit-test the pure runtime-outcome-tracking mechanism that every user story depends on. This phase deliberately stops short of wiring it into `plugin.py`, so User Story 1's acceptance tests (Phase 3) still observe the pre-fix, collection-only behavior and fail correctly before Phase 3's implementation tasks run.

**⚠️ CRITICAL**: No user story acceptance test can pass until Phase 3 wires this mechanism in.

- [x] T002 [P] Write `tests/unit/test_outcomes.py` with unit tests for `OutcomeTracker` / `_NodeOutcome` per `data-model.md`'s state-transition table: a node ID with only a passing `call` phase (plus passed `setup`/`teardown`) is in `passing_nodeids()`; a node ID whose `call` phase is `"failed"` is not; a node ID whose `call` phase is `"skipped"` (plain skip or xfail) is not; a node ID whose `call` phase is `"passed"` with `wasxfail` set (xpass) is not; a node ID whose `setup` phase is `"failed"` (no `call` report) is not; a node ID whose `teardown` phase is `"failed"` after a passing `call` phase is not; two independent node IDs are tracked independently. Run `uv run pytest tests/unit/test_outcomes.py` and confirm it FAILS (the `pytest_feature_coverage.outcomes` module does not exist yet).
- [x] T003 Implement `src/pytest_feature_coverage/outcomes.py` (`OutcomeTracker.record(nodeid,     when, outcome, wasxfail)` and `OutcomeTracker.passing_nodeids() -> set[str]`, plus the internal `_NodeOutcome` dataclass) per `data-model.md`, to make T002 pass. Run `uv run pytest tests/unit/test_outcomes.py` and confirm it PASSES.

**Checkpoint**: The pure outcome-tracking mechanism exists and is unit-tested, but is not yet reachable from `pytest --feature-coverage` (plugin.py is unmodified). Foundation ready.

______________________________________________________________________

## Phase 3: User Story 1 - Coverage Reflects Verified Requirements, Not Declared Ones (Priority: P1) 🎯 MVP

**Goal**: A requirement is covered only when at least one associated test achieves a clean pass; failing, skipped, xfailed, and setup/teardown-errored tests do not grant coverage.

**Independent Test**: Run a single `req()`-annotated test that fails, confirm its requirement is uncovered; flip it to pass, confirm it becomes covered.

### Tests for User Story 1 (write first, confirm FAIL against current plugin.py)

- [x] T004 [US1] Write `tests/integration/test_execution_coverage.py` (new file) with `pytester` acceptance test classes covering spec.md User Story 1's five acceptance scenarios: a requirement referenced only by a passing test is covered; only by a failing test is uncovered; only by a skipped test is uncovered; only by an `xfail`-marked test (expected failure) is uncovered; referenced by a test whose fixture setup raises is uncovered. Run `uv run pytest -v tests/integration/test_execution_coverage.py` and confirm these new tests FAIL against the current, unmodified `plugin.py` (collection-time association still grants coverage regardless of outcome) — capture the failure output as the required red-state evidence before implementing the fix.
- [x] T005 [P] [US1] Add test cases to `tests/unit/test_plugin.py` for a new `_apply_outcome_filter(req_map, passing_nodeids)` helper: narrows each requirement's covering-test list to only node IDs present in `passing_nodeids`, preserving order; a requirement ID whose node IDs are all filtered out ends up with an empty list (not removed from the dict); an empty `req_map` returns an empty dict. Run `uv run pytest tests/unit/test_plugin.py` and confirm these new cases FAIL (the function does not exist yet).

### Implementation for User Story 1

- [x] T006 [US1] In `src/pytest_feature_coverage/plugin.py`: add the `_apply_outcome_filter` helper function (making T005 pass); add a `pytest_runtest_makereport` hookwrapper (`@pytest.hookimpl(wrapper=True, tryfirst=True)`, per `research.md`) that records each finalized report's `(nodeid, when, outcome, wasxfail)` into the session's `OutcomeTracker`; initialize `state['outcomes'] = OutcomeTracker()` in `pytest_configure` alongside `'features'`; call `_apply_outcome_filter` on `req_map` in `_compute_and_store_report` before passing it to `compute_coverage()`, using `state.get('outcomes', OutcomeTracker())` as a defensive default. Depends on: T003, T005.
- [x] T007 [US1] Update `TestComputeAndStoreReport.test_computes_and_stores_report` in `tests/unit/test_plugin.py` (existing test) to include an `'outcomes'` entry in its hand-built `state` dict (an `OutcomeTracker` with the covering node ID recorded as a clean pass), since `_compute_and_store_report` now reads that key. Depends on: T006.
- [x] T008 [US1] Re-run `uv run pytest -v tests/integration/test_execution_coverage.py` (T004) and `uv run pytest tests/unit/test_plugin.py` (T005/T007) and confirm all now PASS. Depends on: T006, T007.

**Checkpoint**: User Story 1 is fully functional and independently testable — execution-aware coverage works end to end through `pytest --feature-coverage`.

______________________________________________________________________

## Phase 4: User Story 2 - One Passing Test Is Enough When Several Reference the Same Requirement (Priority: P2)

**Goal**: A requirement covered by a mix of outcomes (one pass among failures/skips, or one passing parametrized case among failing ones) is covered, and only the passing node ID(s) appear as evidence.

**Independent Test**: Annotate two tests with the same requirement ID, one passing and one failing; confirm the requirement is covered and only the passing node ID is listed.

- [x] T009 [US2] Add test classes to `tests/integration/test_execution_coverage.py` covering spec.md User Story 2's four acceptance scenarios: one passing + one failing test on the same requirement is covered, listing only the passing node ID; one passing + one skipped test is covered, listing only the passing node ID; a parametrized test with at least one passing case covers the requirement and reports that case's specific node ID (not the failing case's); a parametrized test with zero passing cases is uncovered. Run `uv run pytest -v tests/integration/test_execution_coverage.py` and confirm these PASS immediately — `_apply_outcome_filter` (T006) already treats each requirement's node IDs independently and each parametrized case as its own node ID, so no new production code is expected here. If any scenario fails, that is a genuine gap in T006/T003 to fix before proceeding, not something to work around in the test.

**Checkpoint**: User Story 2 verified; Users Stories 1 and 2 both work independently.

______________________________________________________________________

## Phase 5: User Story 3 - The CI Threshold Gate Reflects Execution-Aware Coverage (Priority: P2)

**Goal**: `--feature-coverage-min` is evaluated against execution-aware coverage, and applying it never hides pytest's own failure exit status.

**Independent Test**: Set `--feature-coverage-min=100` against a suite whose only test for a requirement fails; confirm the process exits non-zero.

- [x] T010 [US3] Add test classes to `tests/integration/test_execution_coverage.py` covering spec.md User Story 3's two acceptance scenarios: a requirement covered only by a failing test with `--feature-coverage-min=100` exits non-zero (and the run's own test failure is still visible/reported, not masked); an all-passing suite with `--feature-coverage-min=100` exits zero. Run and confirm these PASS immediately — `pytest_sessionfinish` already calls the (now execution-aware) `_compute_and_store_report`, so no new production code is expected.

**Checkpoint**: User Story 3 verified.

______________________________________________________________________

## Phase 6: User Story 4 - Reports Agree Across Formats and Distinguish Verified Evidence (Priority: P3)

**Goal**: Text, JSON, and Markdown reports agree on totals, percentages, and covering node IDs.

**Independent Test**: Run the same mixed-outcome suite three times with each `--feature-coverage-format` value and diff totals/percentages/covering IDs across outputs.

- [x] T011 [US4] Add a test class to `tests/integration/test_execution_coverage.py` that runs a mixed suite (passing, failing, skipped tests referencing several requirements) three times with `--feature-coverage-format=text`, `=json`, and `=markdown`, and asserts all three agree on total requirement count, covered count, percentage, and the set of covering node IDs per requirement. Run and confirm PASS immediately — all three reporters already read from the same `CoverageReport` built by `_compute_and_store_report`, so no new production code is expected.

**Checkpoint**: All four user stories independently functional and verified.

______________________________________________________________________

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, dogfooding, and full verification per the feature request's own Verification section.

- [x] T012 [P] Add an `EXECUTION_COVERAGE` component with numbered requirements to `features/001-feature-coverage-plugin.feature.yaml`, one requirement per FR-001 through FR-013 in spec.md (dogfooding: this plugin's own coverage report must track this feature).
- [x] T013 [P] Update `docs/features/001-feature-coverage-plugin.md`: add an `EXECUTION_COVERAGE` acceptance-criteria section mirroring T012's YAML requirement IDs, and a User Story entry cross-referencing `specs/002-execution-aware-coverage/spec.md`.
- [x] T014 [P] Add a short "Execution-aware coverage" section to `README.md` documenting the outcome table (pass/fail/skip/xfail/error/xpass) and the explicit xpass policy, satisfying FR-004's user-facing documentation requirement.
- [x] T015 [P] Update `docs/design/codebase-map.md`: add `outcomes.py` to the Source Packages table and add/update the Feature-to-Code Mapping row for coverage computation to mention execution-aware filtering.
- [x] T016 Run `mise run test:all`, `mise run test:coverage`, and `mise run test:features` from repo root; confirm all three pass with zero regressions to orphan detection, strict mode, or output format structure (per spec.md SC-005 and the feature request's Verification section).
- [x] T017 [P] Run `mise run test:lint-markdown` and fix any warnings in the new/changed markdown files (spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/coverage-semantics.md, ADR-003, ADR-006, docs/features/001-...md, docs/plans/002-....md, docs/plans/README.md, README.md).
- [x] T018 Manually run the `quickstart.md` validation scenario once and confirm the documented expected output matches actual output.

______________________________________________________________________

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup. BLOCKS Phase 3's implementation tasks (T006-T008), but not Phase 3's test-writing task (T004), which is written and run first specifically to observe the pre-fix red state.
- **User Story 1 (Phase 3)**: Depends on Foundational (T003) for T006. Delivers the entire mechanism; T004's tests must go red before T006 and green after.
- **User Stories 2-4 (Phases 4-6)**: Depend on User Story 1 (Phase 3) being complete. Each adds acceptance-test coverage only; no cross-phase production-code dependencies among Phases 4-6 themselves, so they can proceed in any order or in parallel.
- **Polish (Phase 7)**: Depends on Phases 3-6 being complete (needs the final requirement set to document, and needs the full suite green to verify).

### Within Phase 3

T004 and T005 (tests) before T006 (implementation) before T007 (existing-test update) before T008 (re-run and confirm green).

### Parallel Opportunities

- T002 (Foundational test) has no other same-phase task to parallelize with in practice (T003 depends on it), but is marked `[P]` because it touches a different file than any Setup task.
- T004 and T005 can be written in parallel (different files: `tests/integration/...` vs `tests/unit/test_plugin.py`).
- T009, T010, T011 (Phases 4-6) touch the same file (`tests/integration/test_execution_coverage.py`) as different test classes; treat as sequential edits to avoid merge conflicts within one session, even though they are logically independent.
- T012-T015 and T017 (Polish, different files) can run in parallel.

______________________________________________________________________

## Parallel Example: Phase 3 (User Story 1)

```bash
# T004 and T005 touch different files and can be written in parallel:
Task: "Write tests/integration/test_execution_coverage.py acceptance tests for US1"
Task: "Add _apply_outcome_filter unit tests to tests/unit/test_plugin.py"
```

______________________________________________________________________

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
1. Complete Phase 2: Foundational (`outcomes.py`, unit-tested).
1. Complete Phase 3: User Story 1 (write acceptance tests red, wire the mechanism into `plugin.py`, confirm green).
1. **STOP and VALIDATE**: `mise run test:integration` and `mise run test:unit` both green; the quickstart.md manual scenario behaves as documented.

### Incremental Delivery

1. Setup + Foundational -> mechanism exists and is unit-tested.
1. User Story 1 -> mechanism wired in, acceptance-tested end to end (MVP).
1. User Stories 2-4 -> acceptance-test coverage confirming the same mechanism already satisfies each story's criteria, with no further production-code changes expected.
1. Polish -> dogfood YAML/docs updated, full verification suite green, PR-ready.

______________________________________________________________________

## Notes

- [P] tasks = different files, no dependencies.
- [Story] label maps task to specific user story for traceability.
- Verify tests fail before implementing (T004, T005 explicitly call this out).
- Commit after each task or logical group, per `src/AGENTS.md` ("Commit frequently").
- Avoid: vague tasks, same-file conflicts, cross-story production-code dependencies that would break independence.

______________________________________________________________________

## Agentic Workflow: Post-Implementation Checklist

> This section is added by the agentic-workflow preset. It prompts for review and documentation steps after the tasks are complete.

### After All Tasks Complete

1. **Code Review**: Run `/speckit.agentic.code-review` to evaluate the implementation against the spec's acceptance criteria.
1. **Design Alignment**: Run `/speckit.agentic.review-alignment` to check for drift between `docs/design/` and the actual implementation.
1. **Decision Capture**: ADR-006 was already captured during `/speckit.specify`; watch for any further trade-offs during implementation (e.g. pytest-version-specific report attribute behavior) and capture them if they arise.
1. **Plan Close-out**: Run `/speckit.agentic.close-plan` to finalize the plan and update `docs/plans/README.md`.
1. **Final PR Review**: Push the close-out commit, then run `/speckit.agentic.review-pr` against that final commit.
1. **Merge**: Human-invoked only, out of scope for this workflow run.
