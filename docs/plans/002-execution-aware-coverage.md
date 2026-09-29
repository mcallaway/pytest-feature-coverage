# 002: Execution-Aware Feature Coverage

**Status**: COMPLETE | **Branch**: `fix/collection-vs-execution-coverage` | **Started**: 2026-09-29 | **Closed**: 2026-09-29\
**Spec Kit plan**: [specs/002-execution-aware-coverage/plan.md](../../specs/002-execution-aware-coverage/plan.md)

## Motivation

`pytest --feature-coverage` currently grants coverage credit at collection time: any collected test carrying a matching `req()` marker counts as covering its requirement, regardless of whether that test passes, fails, skips, xfails, or errors. This makes the coverage percentage and the `--feature-coverage-min` CI gate unreliable: a requirement can show as covered even though no test ever successfully verified it. See `tmp/collection-vs-execution-feature-request.md` for the original request, `specs/002-execution-aware-coverage/spec.md` for the full specification, and [ADR-006](../decisions/006-execution-aware-covering-test.md) for the "covering test" definition.

## Non-Goals

- No changes to the `req()` marker syntax, the `feature.yaml` schema, or existing CLI/ini option names.
- No new reporters or reporter output formats; text/JSON/Markdown keep their existing shapes, just execution-aware values.
- No change to orphan-marker detection, which is collection-based by design and unaffected by execution outcomes.
- No retry/flaky-test handling beyond pytest's own `call` phase outcome for a given run.

## Phases

### Phase 1: Spec, plan, and design artifacts

- **Deliverable**: `specs/002-execution-aware-coverage/{spec.md,plan.md,research.md,data-model.md,quickstart.md,contracts/coverage-semantics.md}`, `docs/decisions/006-execution-aware-covering-test.md` (Proposed), ADR-003 annotated with a pointer.
- **Status**: DONE

### Phase 2: Failing acceptance tests (TDD, pre-fix)

- **Deliverable**: `tests/integration/test_execution_coverage.py` and `tests/unit/test_outcomes.py` written and confirmed to fail against the collection-only implementation (4/5 US1 pytester scenarios red pre-fix).
- **Status**: DONE

### Phase 3: Implementation

- **Deliverable**: `src/pytest_feature_coverage/outcomes.py` (new), `plugin.py` updated with the `pytest_runtest_makereport` hookwrapper and `_apply_outcome_filter` helper; all new tests pass; `mise run test:all`, `test:coverage`, `test:features` all green.
- **Status**: DONE

### Phase 4: Documentation and dogfood updates

- **Deliverable**: `features/001-feature-coverage-plugin.feature.yaml` `EXECUTION_COVERAGE` component, `docs/features/001-feature-coverage-plugin.md` updated, `README.md` short note, `docs/design/codebase-map.md` row update.
- **Status**: DONE

### Phase 5: Review and PR

- **Deliverable**: rubric pass, code review pass, open PR.
- **Status**: DONE — `/speckit.agentic.apply-rubric` and `/speckit.agentic.code-review` both ran with no remaining blocking findings; PR [#29](https://github.com/bayer-int/pytest-feature-coverage/pull/29) opened against `main`, not merged.

## Close-out Criteria

- [x] All three verification commands from the feature request pass: `mise run test:all`, `mise run test:coverage`, `mise run test:features`.
- [x] New pytester acceptance tests demonstrably failed pre-fix and pass post-fix.
- [x] ADR-006 moved from Proposed to Accepted.
- [x] PR open, reviewable, not merged. -> [#29](https://github.com/bayer-int/pytest-feature-coverage/pull/29)
