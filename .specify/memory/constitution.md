<!--
Sync Impact Report:
- Version change: 0.0.0 → 1.0.0
- Added principles: Honest Technical Judgment, Investigate Before Acting,
  Durable Shared Understanding
- Added sections: Development Standards, Quality Gates
- Templates requiring updates: ✅ plan-template.md (no changes needed),
  ✅ spec-template.md (no changes needed), ✅ tasks-template.md (no changes needed)
- Follow-up TODOs: none
-->

# pytest-feature-coverage Constitution

## Core Principles

### I. Honest Technical Judgment Over Politeness

- Say "I don't know" when you don't know
- Push back when you disagree, providing your reasoning
- Never be agreeable just to be nice
- Complexity MUST be justified; default to the simplest approach

### II. Investigate Before Acting

- Stop and ask when multiple valid approaches exist
- Read error messages completely -- they often contain the solution
- Find and understand working examples before implementing patterns
- Test one hypothesis at a time
- Check `docs/decisions/` when making architectural choices

### III. Strive For Durable Shared Understanding

- Consider whether what is being asked is well formulated and clear
- Ask clarifying questions if needed
- Once you believe you understand, restate what you think the shared intent is
- Read `./docs` and consider if what is being asked is additive or a change
- Update plans and create ADRs before committing significant changes

## Development Standards

- Simple, clean, and maintainable beats clever or complex (YAGNI)
- Reduce duplication even if refactoring takes effort
- Names describe what things ARE, not implementation or history
- Python source lives in `./src/`; use `ruff` for linting/formatting; use `ty` for type checking
- No runtime dependencies beyond pytest, pydantic, and PyYAML
- Use Conventional Commits for PR titles (release-please manages releases)
- Never skip pre-commit hooks

## Quality Gates

- TDD mandatory: write failing test, confirm failure, implement, verify pass
- Separate unit tests (`tests/unit/`) from acceptance tests (`tests/acceptance/`)
- All test failures are your responsibility (Broken Windows theory)
- Never hide failing features with trivial tests
- Never delete a failing test -- raise the issue instead
- Test output MUST be pristine; capture and validate expected errors
- No mocks in acceptance tests; use real data
- Strive for >75% coverage without building unwieldy tests for 100%

## Governance

This constitution supersedes conflicting guidance. Amendments require:

1. A documented rationale (ADR in `docs/decisions/`)
2. Version bump following semver (MAJOR: principle removal/redefinition,
   MINOR: new principle/section, PATCH: wording/clarification)
3. Propagation check across templates and AGENTS.md files

All PRs MUST verify compliance with these principles. The layered AGENTS.md
files (`AGENTS.md`, `src/AGENTS.md`, `tests/AGENTS.md`) provide operational
detail but do not override this constitution.

**Version**: 1.0.0 | **Ratified**: 2025-05-19 | **Last Amended**: 2025-05-19
