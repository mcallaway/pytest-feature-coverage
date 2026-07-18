# Data Model: w29 — `--feature-coverage-filter`

No new persistent entities are introduced by this feature. The filter is a transient operation within a single function call.

______________________________________________________________________

## Existing Entities Involved

### `FeatureFile` (`schema.py`)

Loaded by `load_all_features()` during `pytest_configure`. One instance per `.feature.yaml` file. Stored in `state['features']` (a `list[FeatureFile]`).

Relevant field used by the filter:

```python
feature_file.feature.name  # str, e.g. "jinja-template-adapter"
```

The filter performs: `filter_text.lower() in feature_file.feature.name.lower()`

`state['features']` is **read-only** with respect to this feature. The filter creates a local shallow slice; the list in `state` is never mutated.

______________________________________________________________________

### `CoverageReport` (`matrix.py`)

Returned by `compute_coverage(features, req_map)`. When `features` is a filtered slice:

- `report.features` contains only the filtered `FeatureFile` entries
- `report.total_requirements` counts requirements across the filtered set only
- `report.covered_requirements` counts covered requirements across the filtered set only
- `report.coverage_percentage` = `covered / total * 100` (or `0.0` if `total == 0`)
- `report.orphan_markers` is set after the call to the full orphan list (unfiltered)

No changes to `CoverageReport` or `compute_coverage()`.

______________________________________________________________________

## State Lifecycle Under Filter

```text
pytest_configure
  └─ load_all_features()       → state['features'] = [F1, F2, F3, ...]   (full)

pytest_collection_modifyitems
  └─ _get_known_requirement_ids() reads state['features']                 (full)
  └─ find_orphans()            → state['orphans'] = [...]                 (full)

_compute_and_store_report()
  ├─ features = state['features']                                          (full)
  ├─ if filters: features = [f for f in features if matches]              (filtered local)
  ├─ report = compute_coverage(features, req_map)                         (filtered)
  └─ state['report'] = report
```

`state['features']` (full) is never overwritten. The filtered `features` local variable is used only within `_compute_and_store_report()` and discarded after.

______________________________________________________________________

## Validation Rules

No new validation rules. The filter silently returns an empty list when nothing matches (`report.features == []`). This is the specified behaviour for COVERAGE_FILTER.9; it is not an error.
