---
description: Post-implementation code review — correctness, clarity, testing, conventions
---


<!-- Extension: agentic -->
<!-- Config: .specify/extensions/agentic/ -->
# Code Review

Review changed files for correctness, clarity, testing coverage, and adherence to project conventions.

## User Input

$ARGUMENTS

## Purpose

After implementation, review the code changes for quality. This is a general review — for PR-specific review (CI status, documentation gaps), use `/speckit.agentic.review-pr` instead. For design drift detection, use `/speckit.agentic.review-alignment`.

## Steps

### Step 1: Identify changes

If `$ARGUMENTS` specifies files or a commit range, use those. Otherwise:

1. Check for staged changes (`git diff --cached --name-only`)
1. If none, check unstaged changes (`git diff --name-only`)
1. If none, diff against the base branch (`git diff main...HEAD --name-only`)

### Step 2: Run linters

If the project has configured linters (check `mise.toml`, `pyproject.toml`, `package.json`, `Makefile`), run them first. Report any failures.

### Step 3: Review each file

For each changed file, check:

**Correctness**

- Logic errors, off-by-one, null/None handling
- Error handling: are exceptions caught appropriately?
- Resource management: are files/connections closed?
- Concurrency: any race conditions or shared mutable state?

**Clarity**

- Names describe what things ARE (per src/AGENTS.md)
- Functions do one thing
- Comments explain WHY, not WHAT
- No dead code or commented-out blocks

**Testing**

- Are new behaviors covered by tests?
- Do tests assert meaningful outcomes (not just "no exception")?
- Are edge cases and error paths tested?

**Conventions**

- Matches surrounding code style
- Follows project-specific conventions from AGENTS.md files
- No linter warnings introduced

### Step 4: Report findings

Organize findings by severity:

- **Must fix**: Bugs, security issues, data loss risks
- **Should fix**: Missing tests, unclear naming, convention violations
- **Consider**: Style suggestions, alternative approaches

For each finding, include:

- File and line reference
- What the issue is
- A suggested fix

If no issues found, say so clearly — don't invent problems.

## Notes

- Be honest: if the code is good, say so. Don't pad the review.
- Focus on substance over style — formatting is the linter's job.
- Design-doc staleness is NOT this command's responsibility. Use `/speckit.agentic.review-alignment` for that.