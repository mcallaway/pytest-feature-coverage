# Quickstart: `--feature-coverage-filter`

Narrows the feature coverage report to features whose name contains a given substring (case-insensitive). The option is repeatable; multiple values combine as OR.

______________________________________________________________________

## Basic usage

```bash
# Show coverage only for features whose name contains "jinja"
pytest --feature-coverage --feature-coverage-filter jinja tests/

# Case-insensitive — same result as above
pytest --feature-coverage --feature-coverage-filter JINJA tests/

# Substring — matches "bigquery-domain-view" and "bigquery-export" etc.
pytest --feature-coverage --feature-coverage-filter bigquery tests/
```

______________________________________________________________________

## Multiple filters (OR)

```bash
# Show features matching "jinja" OR "bigquery"
pytest --feature-coverage \
  --feature-coverage-filter jinja \
  --feature-coverage-filter bigquery \
  tests/
```

______________________________________________________________________

## Combined with `-k` (narrow both tests and report)

```bash
# Run only jinja-related tests AND show only the jinja feature in the report
pytest --feature-coverage --feature-coverage-filter jinja -k jinja tests/
```

The two options are orthogonal: `--feature-coverage-filter` scopes the _report_; `-k` scopes which _tests run_. Using both gives the most focused view.

______________________________________________________________________

## Threshold under a filter

`--feature-coverage-min` is evaluated against the _filtered_ Overall percentage:

```bash
# Fail if jinja feature coverage is below 80%
pytest --feature-coverage --feature-coverage-filter jinja --feature-coverage-min 80 tests/
```

______________________________________________________________________

## No matching features

When the filter matches nothing, the report shows an empty result and exits zero (unless `--feature-coverage-min` forces a non-zero exit):

```text
=== Feature Coverage ===
Overall: 0/0 requirements covered (0.0%)
```

______________________________________________________________________

## Unfiltered baseline (no option passed)

Omitting `--feature-coverage-filter` is identical to the current behaviour — all loaded features are shown. No configuration change is needed for existing workflows.

______________________________________________________________________

## `pytest --help` entry

```text
--feature-coverage-filter=TEXT
    Only show features whose name contains TEXT (case-insensitive).
    Repeatable; multiple values combine as OR. Default: show all features.
```
