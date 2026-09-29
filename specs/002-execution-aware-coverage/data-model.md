# Data Model: Execution-Aware Feature Coverage

**Feature**: [spec.md](spec.md)

This feature adds one new piece of runtime state. It does not change the shape of any existing entity (`FeatureFileModel`, `ComponentModel`, `CoverageEntry`, `CoverageReport`).

## New Entities

### NodeOutcome (internal, `outcomes.py`)

Accumulated setup/call/teardown verdict for one collected test node ID (a full pytest node ID, including any parametrize suffix, e.g. `tests/test_x.py::test_f[case-2]`).

| Field         | Type | Description                                                                                                                                                                                                 |
| ------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `call_passed` | bool | `True` once a `call`-phase report for this node ID has `outcome == "passed"` and no `wasxfail`.                                                                                                             |
| `errored`     | bool | `True` if any phase (`setup`, `call`, `teardown`) for this node ID reported an `outcome` other than `"passed"` (covers both `"failed"` and `"skipped"`, e.g. a fixture finalizer skipping during teardown). |

Not exposed outside `outcomes.py`; `OutcomeTracker` is the public surface.

### OutcomeTracker (internal, `outcomes.py`)

Owns a `dict[str, NodeOutcome]` keyed by node ID. Public surface:

- `record(nodeid: str, when: str | None, outcome: str, wasxfail: str | None) -> None` — folds one finalized `pytest.TestReport`'s relevant fields into the node's running verdict. Called once per `setup`/`call`/`teardown` phase report. `when` is typed `str | None` only to match `TestReport`'s base-class annotation; in practice it is always one of `"setup"`/`"call"`/`"teardown"`.
- `passing_nodeids() -> set[str]` — returns the node IDs where `call_passed is True and not errored`. This is the "clean pass" set described in the spec's Key Entities section (Node outcome).

One `OutcomeTracker` instance lives per pytest session, stored on the existing plugin state dict (`config._feature_coverage_state['outcomes']`), initialized in `pytest_configure` alongside `features`, following the same config-scoped state pattern already used for `req_map` and `orphans`.

## Existing Entities: How They're Used, Unchanged

- **`req_map: dict[str, list[str]]`** (built by `scanner.scan_requirements()` at collection time, unchanged): requirement ID -> list of node IDs *associated* with it via `req()`. This is collection-time truth (what was declared), not runtime truth (what passed).
- **`CoverageEntry.covering_tests`**: unchanged shape (`list[str]`). What changes is which node IDs plugin.py puts into this list before calling `compute_coverage()` — only node IDs present in `OutcomeTracker.passing_nodeids()`, narrowing `req_map` down from "associated" to "covering" per requirement, at report-compute time.
- **`CoverageReport`**: unchanged shape and unchanged computation (`matrix.compute_coverage()` is not modified).

## State Transition (per node ID, per test run)

```text
(no report yet)
     |
     v
setup report arrives -----> outcome!="passed" --> errored=True (terminal for this node)
     |
     v (setup passed)
call report arrives ------> outcome!="passed" (failed, plain skip, or xfail) --> errored=True; call_passed stays False
     |                 \--> outcome="passed", wasxfail set (xpass) --> call_passed stays False (not errored either)
     |                 \--> outcome="passed", wasxfail is None --> call_passed=True
     v
teardown report arrives ---> outcome!="passed" (failed, or skipped e.g. a finalizer calling
     |                       pytest.skip()) --> errored=True (overrides a prior call_passed=True)
     v
final verdict: covering iff call_passed and not errored
```

## Filtering Function (`plugin.py`)

```text
_apply_outcome_filter(req_map, passing_nodeids) -> dict[str, list[str]]

For each (requirement_id, node_ids) in req_map:
    keep only node_ids that are members of passing_nodeids, preserving order.
```

Pure function, no pytest coupling; unit-testable the same way `_get_known_requirement_ids` and `_get_threshold` already are.
