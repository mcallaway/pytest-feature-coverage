# ADR-004: Apply the `--feature-coverage-filter` at Report Time, Not Load Time

- **Status**: Accepted
- **Date**: 2026-07-18

## Context

`--feature-coverage-filter` was added in `feat/w29-coverage-filter` to let a developer narrow the coverage report to a subset of features (e.g. `--feature-coverage-filter auth`) without re-running the full suite. The question during implementation was: **at what point in the pytest lifecycle should the filter be applied?**

Two natural candidates existed:

1. **Load time** — strip non-matching features from `state['features']` inside `pytest_configure`, so the rest of the plugin never sees them.
1. **Report time** — keep `state['features']` intact throughout the session and slice the list locally inside `_compute_and_store_report()` just before calling `compute_coverage()`.

The choice is hard to reverse because `state['features']` is the single shared source of truth for both orphan detection and report generation. Whichever scope the filter is given early in the design propagates through both paths.

A second related decision arose: whether to expose the filter as an INI option in addition to the CLI flag.

## Decision

**Apply the filter locally inside `_compute_and_store_report()`, never mutating `state['features']`.** Do not add a corresponding INI option.

The implementation slices the feature list into a local variable immediately before calling `compute_coverage()`:

```python
features = state['features']  # full list; never mutated (needed for orphan checking)

filters = config.getoption('--feature-coverage-filter') or []
if filters:
    lower_filters = [f.lower() for f in filters]
    features = [
        ff
        for ff in features
        if any(f in ff.feature.name.lower() for f in lower_filters)
    ]

report = compute_coverage(features, req_map)
```

`state['features']` is never written to after this point.

## Alternatives Considered

### Filter at load time in `pytest_configure`

The filter would be applied once, early, and every downstream consumer would see only the matching features — cleaner in principle.

**Rejected** because `_get_known_requirement_ids()` reads `state['features']` to build the complete set of valid composite requirement IDs (`feature.component.N`) used for orphan detection. If a feature is stripped at load time, any `req()` marker referencing one of its requirements has no matching ID in the known-ID set and is reported as an orphan. This is incorrect: the marker is valid — it just references a feature the developer chose not to display. Orphan warnings for filtered-out features would be confusing and wrong.

### Filter inside `compute_coverage()` in `matrix.py`

Pass the filter value as a new parameter to `compute_coverage()` and apply it there.

**Rejected** because it leaks UI-layer knowledge (`--feature-coverage-filter` is a display selector) into a pure data-transformation function. `matrix.py` already accepts an arbitrary `features` list and is agnostic to where that list comes from; adding filter logic there would couple a stable, independently testable module to a CLI option.

### Filter inside each reporter

Apply the filter in `TextReporter`, `JsonReporter`, and `MarkdownReporter` individually.

**Rejected** for two reasons: it requires three parallel changes to reporters that already receive a pre-computed `CoverageReport`, and it violates DRY — the filter semantics would need to be duplicated or abstracted across all three paths. Reporters are output formatters, not data selectors.

### Add an INI option (`feature_coverage_filter`)

Expose the filter in `pyproject.toml` / `pytest.ini` so it can be set once per project.

**Rejected** because the filter is a session-specific developer convenience, not stable project configuration. An INI option would encourage committing filter values that silently hide features from the coverage report in CI, which is the opposite of the intended use case. A committed filter is indistinguishable from a misconfiguration that masks requirement gaps.

## Consequences

### Positive

- `req()` markers for filtered-out features are never reported as orphans; they remain valid throughout the session.
- No changes to `matrix.py`, the three reporters, or the `CoverageReport` schema are needed — the filter is a two-line insertion in a single function.
- The filter is explicitly a *view selector*: it does not change which features the project tracks, only which subset is displayed in one report run.
- Omitting the INI option keeps CI reports complete by default; hiding features requires a deliberate per-session flag that does not persist.

### Negative

- A developer who expects `--feature-coverage-filter` to also suppress orphan warnings for filtered-out features will be surprised: orphan detection is deliberately unaffected. This may require a note in documentation or the `--help` text.
- Filtering at report time means `compute_coverage()` still runs on the full feature list during orphan checking; there is no early-exit performance benefit for sessions with many features (acceptable given the typical scale of ≤100 features).
