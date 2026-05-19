# Testing Conventions

## Framework

- Use `pytest`, not `unittest`.
- Avoid the use of mocking except where demonstrably valuable.
- Strive for reasonable test coverage, above 75%, but do not build complex or unwieldy tests just to dogmatically achieve 100% test coverage. We want tests to be as correct, clear, concise, and maintainable as our code.

## Workflow

- Write a failing test, confirm it fails, make it pass, refactor.

## Rules

- Separate "unit" (`./tests/unit`) from "acceptance" tests (`./tests/acceptance`).
- All test failures are your responsibility (Broken Windows theory).
- Never hide failing features with a trivial test (e.g., "assert true").
- Never delete a failing test -- raise the issue instead.
- Test output must be pristine. If errors are expected, capture and validate them.
- Never test mocked behavior -- test real logic.
- No mocks in end-to-end acceptance tests. Use real data and APIs in acceptance tests.
- Never ignore test warnings.

## Running Tests

```shell
mise run test:unit          # Unit tests only
mise run test:acceptance    # Acceptance tests only
mise run test:all           # All tests + lint + typecheck
mise run test:lint          # Ruff linter
mise run test:typecheck     # ty type checker
```

## Quality Review

- Use `/speckit.agentic.code-review` after implementation for automated quality review.
- Use `/speckit.agentic.review-pr` for pre-merge PR review.
