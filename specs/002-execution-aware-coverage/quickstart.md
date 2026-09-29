# Quickstart: Validating Execution-Aware Feature Coverage

**Feature**: [spec.md](spec.md) | **Contract**: [contracts/coverage-semantics.md](contracts/coverage-semantics.md)

## Prerequisites

```shell
cd ~/git/pytest-feature-coverage
mise trust .
mise run dev:setup
```

## Automated Validation (primary path)

The acceptance criteria in this feature are validated end to end by `pytester`-based tests. These must fail against the pre-fix, collection-only implementation and pass after the fix:

```shell
mise run test:all
mise run test:coverage
mise run test:features
```

## Manual Validation (spot check)

To see the behavior directly, from repo root:

```shell
mkdir -p /tmp/coverage-check/features
cat > /tmp/coverage-check/features/app.feature.yaml <<'EOF'
feature:
  id: "001"
  name: app
components:
  CORE:
    name: Core
    requirements:
      1: A requirement covered only by a failing test
      2: A requirement covered by one passing and one failing test
EOF

cat > /tmp/coverage-check/pyproject.toml <<'EOF'
[tool.pytest.ini_options]
feature_yaml_paths = ["features"]
EOF

cat > /tmp/coverage-check/test_app.py <<'EOF'
import pytest

@pytest.mark.req("app.CORE.1")
def test_fails():
    assert False

@pytest.mark.req("app.CORE.2")
def test_passes():
    pass

@pytest.mark.req("app.CORE.2")
def test_also_fails():
    assert False
EOF

cd /tmp/coverage-check
uv run --project ~/git/pytest-feature-coverage pytest --feature-coverage
```

**Expected outcome**:

- `app.CORE.1` reports as uncovered (its only associated test failed).
- `app.CORE.2` reports as covered, with `test_app.py::test_passes` as the only covering node ID (not `test_also_fails`).
- Overall: `1/2` requirements covered (50.0%).

## Success Criteria Checklist

- [ ] SC-001: requirement backed only by a failing/skipped/xfailed/erroring test is uncovered.
- [ ] SC-002: requirement backed by a mix of outcomes, with at least one pass, is covered and identifies only the passing node ID(s).
- [ ] SC-003: `--feature-coverage-min=100` exits non-zero when execution-aware coverage is below 100%, even if collection-time association would have hit 100%.
- [ ] SC-004: text/JSON/Markdown reports agree on totals, percentage, and covering node IDs for the same run.
- [ ] SC-005: `mise run test:all`, `mise run test:coverage`, `mise run test:features` all pass with zero regressions to orphan detection, strict mode, or output format structure.
