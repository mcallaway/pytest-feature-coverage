# pytest-feature-coverage

A pytest plugin that connects tests to requirements defined in YAML feature files and produces deterministic coverage reports

## Project Status

- [x] There are non-trivial tests in `./tests`.
- [x] There is an acceptable level of test coverage.
- [x] CI/CD workflows pass on every PR.
- [x] The GitHub repo uses branch protection on `main`.
- [x] There is more than one owner/admin.
- [ ] There is more than one contributor.

## Developer Setup

Prerequisites: [mise](https://mise.jdx.dev/getting-started.html)

Install mise:

```shell
curl https://mise.run | sh
```

Add mise activation to your shell rc file (e.g., `~/.zshrc`, `~/.bashrc`):

```shell
eval "$( mise activate zsh )"  # use bash, fish, etc. as appropriate
```

Restart your shell, then:

```shell
mise trust .
mise run dev:setup
mise run dev:check
```

### Usage

Add feature YAML files defining your requirements:

```yaml
# features/my-feature.feature.yaml
feature:
  id: "001"
  name: my-feature

components:
  CORE:
    name: Core logic
    requirements:
      1: Handles valid input
      2: Rejects invalid input
```

Configure pytest (in `pyproject.toml`):

```toml
[tool.pytest.ini_options]
feature_yaml_paths = ["features"]
# feature_coverage_format = "text"  # text, json, or markdown
# feature_coverage_min = 80         # fail if below 80%
# feature_coverage_strict = true    # treat orphan markers as errors
```

Annotate tests with `req()` markers:

```python
import pytest

@pytest.mark.req("my-feature.CORE.1")
def test_handles_valid_input():
    ...

@pytest.mark.req("my-feature.CORE.1", "my-feature.CORE.2")
def test_multiple_reqs():
    ...
```

Run with coverage reporting:

```shell
pytest --feature-coverage
pytest --feature-coverage --feature-coverage-format=json
pytest --feature-coverage --feature-coverage-min=80
```

### Execution-Aware Coverage

A requirement is covered only when at least one of its associated tests achieves a **clean pass**, not merely when a `req()` marker was collected. Coverage is computed at the end of the run from real pytest outcomes:

| Outcome                                     | Counts as coverage? |
| ------------------------------------------- | ------------------- |
| Passed                                      | Yes                 |
| Failed (assertion, exception, etc.)         | No                  |
| Skipped                                     | No                  |
| `xfail` (expected failure)                  | No                  |
| `xpass` (unexpected pass, non-strict xfail) | No (see note below) |
| Setup or teardown error                     | No                  |
| Deselected / never run                      | No                  |

When several tests reference the same requirement, one clean pass is enough: the requirement is covered and the report lists only the passing node ID(s) as evidence, even if other tests for the same requirement fail, skip, or xfail. Parametrized test cases are tracked independently by their own node ID.

**Why `xpass` doesn't count**: an `xfail` marker is a declared expectation that the test will fail. A test unexpectedly passing signals the marker is stale or the underlying behavior changed, not that the requirement was genuinely verified as intended. This is a deliberate policy decision, documented in [ADR-006](docs/decisions/006-execution-aware-covering-test.md).

### Running Tests

```shell
mise run test:unit          # Unit tests only
mise run test:integration   # Integration tests only
mise run test:all           # All tests
mise run test:lint          # Ruff linter
mise run test:typecheck     # ty type checker
```

### Creating Releases

Releases are managed by [release-please](https://github.com/googleapis/release-please). Use [Conventional Commits](https://www.conventionalcommits.org/) in your PR titles and release-please will automatically create release PRs with version bumps and changelog updates.

### Publishing to Artifactory

```shell
mise run code:build
mise run code:publish
```
