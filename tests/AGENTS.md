# Testing Conventions

## Framework

- Use `pytest`, not `unittest`.
- Avoid the use of mocking except where demonstrably valuable. Prefer `types.SimpleNamespace` with plain callables over `MagicMock` — it makes test intent explicit and avoids hidden magic.
- Strive for reasonable test coverage, above 75%, but do not build complex or unwieldy tests just to dogmatically achieve 100% test coverage. We want tests to be as correct, clear, concise, and maintainable as our code.

## What "Tested" Means

Coverage percentage is a floor, not a goal. See [ADR-003](../docs/decisions/003-what-tested-means.md) for the full definition. In short:

1. **Execution coverage** (`mise run test:coverage`) — every source line and branch runs. Necessary but not sufficient.
1. **Feature coverage** (`mise run test:features`) — every declared requirement has a covering test. *Read the output table*, not just pass/fail. A requirement showing 0 covering tests is a finding even when overall coverage is 100%.
1. **Structural review** (`speckit.agentic.code-review`) — test class structure, marker correctness, and assertion resilience cannot be verified by metrics. Run after every non-trivial implementation.

## Workflow

- Write a failing test, confirm it fails, make it pass, refactor.

## Rules

- Separate "unit" (`./tests/unit`) from "integration" tests (`./tests/integration`).
- All test failures are your responsibility (Broken Windows theory).
- Never hide failing features with a trivial test (e.g., "assert true").
- Never delete a failing test -- raise the issue instead.
- Test output must be pristine. If errors are expected, capture and validate them.
- Never test mocked behavior -- test real logic.
- No mocks in integration tests. Use real pytester fixtures and real test data.
- Never ignore test warnings.
- Treat `conftest.py` and test helpers as production code — they deserve the same review discipline as `src/`.

## Running Tests

```shell
mise run test:unit          # Unit tests only
mise run test:integration   # Integration tests only
mise run test:coverage      # Unit tests with branch coverage report
mise run test:features      # Feature/requirement coverage report
mise run test:all           # All tests + lint + typecheck
mise run test:lint          # Ruff linter
mise run test:typecheck     # ty type checker
```

## Quality Review

- Use `/speckit.agentic.code-review` after implementation for automated quality review.
- Use `/speckit.agentic.review-pr` for pre-merge PR review.
- Human reviewers: see [Guide 003](../docs/guides/003-reviewing-tests-and-reading-reports.md) for a checklist and worked examples of common test structure problems.
