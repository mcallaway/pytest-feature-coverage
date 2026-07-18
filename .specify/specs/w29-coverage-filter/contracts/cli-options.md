# Contract: CLI Options — w29

This document is the authoritative contract for CLI options added or modified by the `--feature-coverage-filter` feature (w29). It supplements the option definitions already documented for the core plugin.

______________________________________________________________________

## New Option: `--feature-coverage-filter`

| Property    | Value                                                                                                                                    |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Option name | `--feature-coverage-filter`                                                                                                              |
| Metavar     | `TEXT`                                                                                                                                   |
| `action`    | `append`                                                                                                                                 |
| `default`   | `None`                                                                                                                                   |
| Repeatable  | Yes — each flag appends one value to the list                                                                                            |
| Help text   | `Only show features whose name contains TEXT (case-insensitive). Repeatable; multiple values combine as OR. Default: show all features.` |

### Semantics

1. **Absent** (`config.getoption('--feature-coverage-filter')` returns `None`): all features are shown. No behavioural change from baseline.

1. **Single value** (`['jinja']`): only features whose `feature.name` contains `'jinja'` (case-insensitive) appear in the report.

1. **Multiple values** (`['jinja', 'bigquery']`): features whose `feature.name` contains _any_ of the values (OR) appear in the report.

1. **Empty string** (`['']`): every feature name contains the empty string, so all features are shown — equivalent to no filter.

1. **Zero matches**: `report.features` is empty; `Overall: 0/0 requirements covered (0.0%)`; exit code 0 unless threshold forces non-zero.

### Scope

The option affects **report output only**. It does not alter:

- Which tests pytest collects or runs
- Orphan `req()` detection (always uses the full feature set)
- `--feature-coverage-min` threshold semantics (evaluated against filtered Overall; see point 3 above re: `0/0 = 0.0%`)
- Any other `--feature-coverage-*` option

### Interaction with `--feature-coverage`

`--feature-coverage-filter` is silently accepted even when `--feature-coverage` is not passed; consistent with all other `--feature-coverage-*` options. The filter has no effect unless the plugin is active.

______________________________________________________________________

## Existing Options (unchanged)

| Option                      | Change                                                          |
| --------------------------- | --------------------------------------------------------------- |
| `--feature-coverage`        | None                                                            |
| `--feature-coverage-format` | None                                                            |
| `--feature-coverage-min`    | None — evaluated against filtered Overall when filter is active |

______________________________________________________________________

## Registration Location

`src/pytest_feature_coverage/plugin.py :: pytest_addoption()`
