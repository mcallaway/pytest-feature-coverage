# Source Code Conventions

## Code Quality

- Simple, clean, and maintainable beats clever or complex.
- Best code is no code -- YAGNI. Smallest reasonable changes to achieve the outcome.
- Reduce duplication even if refactoring takes effort.
- Commit work frequently, even if the high-level task isn't done.

## Naming

Names describe what things ARE, not implementation or history.

- Good: `Registry`, `Tool`, `execute()`
- Bad: `MCPToolWrapper`, `executeToolWithValidation()`, anything with "New", "Legacy", "Enhanced"

## Comments

- Classes and functions should have correct, clear, and concise docstrings.
- Explain WHAT code does or WHY it exists.
- Never reference what it used to be or how it changed.
- No temporal context ("recently refactored", "moved from").

## Style

- Python source lives in `./src/`.
- Match surrounding code style -- consistency within a file matters more than external standards.
- Use `ruff` for linting and formatting. Never accept linting errors.
- Use `ty` for type checking. Fix type errors before committing.

## Git

- Commit frequently with clear, concise messages.
- Use [Conventional Commits](https://www.conventionalcommits.org/) for PR titles (release-please uses these).
- Never skip pre-commit hooks.
- If you make an architectural decision, propose an ADR in `docs/decisions/`.

## Testing

- Strive for test-driven-development (TDD): write the test, see it fail, then write the code and re-run the test to see it pass.
- See additional instructions about testing in `./tests/AGENTS.md` when applicable.

## Workflow

- Use `/speckit.agentic.start-work` at the beginning of a session to load context.
- Use `/speckit.agentic.code-review` after implementation for quality review.
- Use `/speckit.agentic.document-decisions` to capture trade-offs as ADRs.
