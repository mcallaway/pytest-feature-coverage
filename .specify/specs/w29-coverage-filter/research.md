# Research: w29 — `--feature-coverage-filter`

**Status**: Complete — no open questions.\
**Date**: 2026-07-18

All design decisions were resolved during specification in `tmp/w29-feature-coverage-filter.md`. This file records them for future reference.

______________________________________________________________________

## Decision Log

### D1 — Where to apply the filter

**Decision**: Apply the filter in `plugin.py :: _compute_and_store_report()`, by slicing the feature list _before_ passing it to `compute_coverage()`.

**Rationale**: `compute_coverage()` in `matrix.py` already accepts an arbitrary `features` list and produces a `CoverageReport` scoped to whatever is passed. No changes to `matrix.py`, reporters, or the schema are needed. The approach is a two-line insertion.

**Alternatives considered**:

- Filter at load time (`pytest_configure`): rejected — the full feature set must be kept for orphan `req()` detection throughout the session.
- Filter inside `compute_coverage()`: rejected — would require a new parameter on a stable internal function and would leak filter knowledge into `matrix.py`.
- Filter inside each reporter: rejected — would require three parallel changes and violate DRY; reporters already receive a pre-computed `CoverageReport`.

______________________________________________________________________

### D2 — `action='append'` for OR semantics

**Decision**: Register the option with `action='append'` so each `--feature-coverage-filter TEXT` call appends to a list. `None` when absent (not `[]`), so `or []` normalises the default.

**Rationale**: Standard pytest/argparse idiom for repeatable options. Produces OR semantics naturally: the list is iterated with `any(...)`.

**Alternatives considered**:

- Comma-separated single option: rejected — inconsistent with other pytest repeatable options and harder to shell-escape.

______________________________________________________________________

### D3 — Case-insensitive substring match

**Decision**: Lowercase both the filter text and `ff.feature.name` at filter time using `str.lower()`.

**Rationale**: Feature names are kebab-case (e.g. `jinja-template-adapter`). Developers are unlikely to remember exact casing when typing a filter. The cost is negligible (≤100 features, run once per session).

**Alternatives considered**:

- `re.search` with `re.IGNORECASE`: more powerful but adds regex escape concerns (feature names contain dashes) for no practical benefit.

______________________________________________________________________

### D4 — No INI option

**Decision**: `--feature-coverage-filter` is CLI-only; no corresponding INI option is added.

**Rationale**: The filter is a session-specific developer convenience, not a stable project configuration. An INI option would encourage committing filters that silently hide features in CI — the opposite of the intended use case.

______________________________________________________________________

### D5 — Orphan detection uses the full feature list

**Decision**: `_get_known_requirement_ids()` reads `state['features']` (the full unfiltered list) and is not changed. Only the local variable `features` in `_compute_and_store_report()` is filtered.

**Rationale**: A `req()` marker for a filtered-out feature is still _valid_; it should not be reported as an orphan simply because the feature is not shown in the report. Mutating `state['features']` would cause valid markers to appear as orphans in strict mode — an incorrect and confusing outcome.

______________________________________________________________________

## No Open Questions

All 9 acceptance criteria from `spec.md` map directly to the two `plugin.py` changes and the test plan. No spikes or prototypes are needed.
