# pytest-feature-coverage

A pytest plugin that connects tests to requirements defined in YAML feature files and produces deterministic coverage reports

## Project Status

- [ ] The GitHub repo uses branch protection on `main`.
- [ ] There is more than one owner/admin.
- [ ] There is more than one contributor.
- [ ] There are non-trivial tests in `./tests`.
- [ ] There is an acceptable level of test coverage.
- [ ] CI/CD workflows pass on every PR.

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

```python
import pytest_feature_coverage
```

### Running Tests

```shell
mise run test:unit          # Unit tests only
mise run test:acceptance    # Acceptance tests only
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
