# Phase 0 Research: Execution-Aware Feature Coverage

**Feature**: [spec.md](spec.md)

## Decision: Where to hook into pytest's runtest protocol

**Decision**: Implement `pytest_runtest_makereport(item, call)` as a new-style hookwrapper (`@pytest.hookimpl(wrapper=True, tryfirst=True)`) in `plugin.py`, feeding each finalized `TestReport` into a new `OutcomeTracker` (in a new `outcomes.py` module) keyed by `report.nodeid`.

**Rationale**:

- `pytest_runtest_logreport(report)` only receives the `TestReport`, with no access to `config` (and therefore no access to this plugin's state dict, which is keyed off `config`). Reusing the established `config`-keyed state pattern (`_PLUGIN_STATE_ATTR`) that every other hook in this plugin already uses requires a hook that receives `item` (which carries `item.config`).
- `pytest_runtest_makereport(item, call)` receives `item`, giving access to `item.config`.
- The report's final `outcome` and `wasxfail` attributes are set by other plugins' implementations of this same hook (notably `_pytest.skipping`, which sets `rep.outcome = "skipped"` and `rep.wasxfail` for `xfail`, and `rep.outcome = "passed"` with `rep.wasxfail` set for a non-strict `xpass`). A **new-style hookwrapper** (`wrapper=True`) observes the fully resolved report only if it resumes after all inner wrappers and implementations have run. Registering with `tryfirst=True` makes this wrapper the outermost one in the call stack, so its `yield` point resumes last, after `_pytest.skipping`'s wrapper (and any other plugin's) has already finalized `report.outcome` / `report.wasxfail`. Without `tryfirst=True`, wrapper nesting order between plugins is registration-order dependent and would make the xfail/xpass detection unreliable.
- This matches the well-documented pytest "incremental testing" pattern (`item.rep_setup`, `item.rep_call`, `item.rep_teardown` via a `tryfirst=True` hookwrapper on `pytest_runtest_makereport`), just storing into plugin state instead of onto the item.
- **Implementation note**: `TestReport.wasxfail` is not a guaranteed attribute — `_pytest.skipping` only sets it on reports it actually handles (xfail/xpass cases). A plain passing or failing report never gets the attribute at all, so the wrapper must read it via `getattr(report, 'wasxfail', None)` rather than `report.wasxfail` directly.

**Alternatives considered**:

- `pytest_runtest_logreport(report)`: rejected, no `config`/`item` access.
- A non-wrapper `pytest_runtest_makereport` returning a new report: rejected, this hook is meant to construct/modify the report itself; a plain observer has no reliable ordering guarantee relative to `_pytest.skipping`'s wrapper and risks reading `report.outcome` before xfail handling has run.
- `pytest_runtest_protocol`: rejected, this is a much higher-level hook that would require re-implementing (or wrapping) the entire three-phase protocol just to observe reports; far more invasive than necessary.

## Decision: What counts as a "clean pass" per node ID

**Decision**: A node ID counts as a covering test if and only if:

1. Its `call` phase report has `outcome == "passed"` AND `wasxfail is None` (excludes xpass), AND
1. No phase (`setup`, `call`, or `teardown`) reported an `outcome` other than `"passed"` for that node ID.

**Rationale**: Directly implements the outcome semantics table in the feature request. Using `wasxfail is None` as the xpass exclusion works because `_pytest.skipping` sets `wasxfail` on the report whenever an `xfail`-marked test's call phase resolves to either the expected-failure case (`outcome = "skipped"`) or the unexpected-pass case (`outcome = "passed"`); a report with `outcome == "passed"` and no `wasxfail` is therefore never an xfail-marked test, only ever a genuine, unconditional pass.

**Implementation note (post-review correction)**: the initial implementation only disqualified a node on `outcome == "failed"`, missing the case where a **non-call phase reports `"skipped"`** -- concretely, a fixture finalizer calling `pytest.skip()` during teardown *after* an already-passing call phase. That node's `call` phase legitimately set `call_passed = True`, and since teardown's `"skipped"` outcome was never checked, `passing_nodeids()` still counted it as covering, even though pytest's own summary reports it as `1 passed, 1 skipped` for that node. `OutcomeTracker.record` now disqualifies on `outcome != "passed"` for any phase (not just `"failed"`), which fixes this while leaving every other documented scenario (plain skip, xfail, xpass, setup/teardown failure) unchanged, since those all already had a non-`"passed"` outcome on the relevant phase.

**Alternatives considered**:

- Checking `item.get_closest_marker("xfail")` directly: rejected, this would require passing `item` (not just `report`) through to the tracker and re-deriving strict/non-strict logic that `_pytest.skipping` already resolved onto the report; duplicating that logic risks drifting from pytest's own behavior across pytest versions.
- Treating any non-`"failed"` outcome as a pass: rejected, this is exactly the bug being fixed (skips and xfails are not failures, but they are also not passes).

## Decision: Threshold-failure exit status must not clobber pytest's own failure status

**Decision**: `pytest_sessionfinish` only escalates `session.exitstatus` when it is currently `0` (i.e. pytest's protocol itself considered the run clean). If pytest already set a non-zero `exitstatus` (e.g. `TESTS_FAILED` from a failing test), the coverage-threshold check leaves it untouched.

**Rationale**: FR-009 and the corresponding US3 acceptance scenario require that a suite with failing tests "remains a non-zero exit regardless of whether the feature-coverage threshold itself would have passed or failed" and that "the underlying pytest failure exit status is not hidden or overwritten." The pre-existing code (predating this feature) unconditionally set `session.exitstatus = 2` whenever the threshold failed, which silently replaced pytest's own `TESTS_FAILED` (`1`) with `INTERRUPTED` (`2`) -- numerically still non-zero, so CI would still fail the build either way, but not the literal guarantee this feature's own spec makes, and `INTERRUPTED` is semantically pytest's code for "the run was interrupted" (e.g. Ctrl-C), not "a check failed." Reproduced with a `pytester` run: a single failing `req()`-marked test plus `--feature-coverage-min=100` exited `2` before this fix, `1` (`pytest.ExitCode.TESTS_FAILED`) after.

**Alternatives considered**:

- Leave as `session.exitstatus = 2` unconditionally: rejected once verified against this feature's own explicit acceptance criterion; it directly contradicts wording this PR itself introduced.
- Use a bitwise-OR/max approach instead of an `if exitstatus == 0` guard: equivalent in outcome for pytest's actual `ExitCode` value range (0-5); the explicit `== 0` guard was chosen for readability over cleverness.

## Decision: Where to apply the outcome filter

**Decision**: Keep `matrix.compute_coverage()` and all three reporters completely unchanged. Add a new pure helper, `_apply_outcome_filter(req_map, passing_nodeids)`, in `plugin.py`, that narrows each requirement's covering-test list down to node IDs present in `passing_nodeids` before the (already-filtered-by-`--feature-coverage-filter`) `req_map` is passed to `compute_coverage()`.

**Rationale**: `matrix.compute_coverage()`'s existing contract is "given a map of requirement ID to covering node IDs, compute totals and percentages" — it has never cared *why* a node ID counts as covering. That contract does not need to change; only what plugin.py decides belongs in the map before calling it changes. This is the smallest possible diff: `matrix.py`, `scanner.py`, and all three `reporters/*.py` modules require zero changes, and every existing unit test for those modules remains valid as a specification of "given genuinely-covering node IDs, render/compute this." `scan_requirements()` in `scanner.py` already scans per-collected-item, so parametrized test cases already produce one `req_map` entry per parametrized node ID; no scanner change is needed for FR-006 (parametrized case granularity).

**Alternatives considered**:

- Passing `passing_nodeids` into `compute_coverage()` as a new parameter: rejected, this couples a pure computation module to a pytest-runtime concept (which node IDs "ran") that it does not otherwise need to know about, and forces every existing `test_matrix.py` test to be rewritten to pass a matching `passing_nodeids` set even though those tests are about matrix arithmetic, not about outcome tracking.
- Filtering inside each reporter: rejected, would triple the change surface (three reporters) for no benefit, and would risk the three formats disagreeing (FR-007 / SC-004) if one reporter's filter logic drifted from another's.

## Decision: xpass (unexpected pass) policy

**Decision**: Documented in [ADR-006](../../docs/decisions/006-execution-aware-covering-test.md). `xpass` does not count as coverage.

**Implementation note (guided-review follow-up)**: the xpass policy was originally verified only at the unit level (`tests/unit/test_outcomes.py::test_unexpected_xpass_is_not_covering`), which hand-constructs a `wasxfail` value passed directly to `OutcomeTracker.record`. FR-013 requires FR-001 through FR-010 (which includes FR-004, the xpass rule) to be verified end-to-end with real `pytester` runs, not only unit tests of internal state. Added `test_requirement_with_only_an_unexpected_xpass_test_is_uncovered` (a real `@pytest.mark.xfail(strict=False)` test whose body passes) to `tests/integration/test_execution_coverage.py`; confirmed it fails against the pre-fix collection-only implementation (reports `1/1 covered`) and passes against the fix.

**Minor cleanup (guided-review follow-up)**: removed an unreachable `OutcomeTracker()` default in `_compute_and_store_report`'s `state.get('outcomes', OutcomeTracker())` (no production or test path ever exercised the fallback; `pytest_configure` always populates `state['outcomes']`) in favor of a plain `state['outcomes']` lookup, and added a docstring to `OutcomeTracker` stating it is constructed once per pytest session and is not designed for reuse or reset across sessions.

## Non-goals confirmed from the spec

- No changes to `req()` marker syntax, feature YAML schema, or any CLI/INI option surface.
- No changes to orphan detection or `feature_coverage_strict` (collection-time, unaffected).
- No changes to `--feature-coverage-filter` (report-time feature-name filtering, orthogonal to which node IDs count as covering).
