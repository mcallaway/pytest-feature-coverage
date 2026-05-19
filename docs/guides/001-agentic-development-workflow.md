# Agentic Development Workflow Guide

How to follow the agentic development workflow pattern. For the design rationale, see [the design doc](../design/001-agentic-development-pattern.md).

## Implementing This Pattern

### For a new project

1. Run `/speckit.agentic.scaffold` to create the docs/ tree and AGENTS.md layering
1. Create the codebase map early with `/speckit.agentic.codebase-map`
1. Start using the feature lifecycle (below) for your first piece of work

### For an existing project

1. Run `/speckit.agentic.scaffold` -- it will skip files that already exist
1. Restructure any existing conventions into AGENTS.md files (preserve substance, change delivery)
1. Run `/speckit.agentic.codebase-map` to document what already exists
1. Adopt the lifecycle incrementally, starting with code-review and document-decisions

## Feature Lifecycle

The key rhythm: plan in one session, implement in another, review in a third. Fresh sessions prevent context bleed.

**Step 1: Define the feature** *(fresh session)* -- `/speckit.specify`

- Start a session in planning mode to refine the idea
- Spec Kit creates a spec in `.specify/specs/NNN/spec.md`
- The spec is the durable artifact, not the conversation

**Step 2: Create a plan** *(fresh session)* -- `/speckit.plan`

- Start a new session. Plan references the spec and existing design docs
- The `after_plan` hook offers to evaluate the plan against `docs/plans/RUBRIC.md`
- Update `docs/plans/README.md` to reflect the new current focus

**Step 3: Implement** *(fresh session per work chunk)* -- `/speckit.implement`

- Run `/speckit.agentic.start-work` to load context
- Write code. Commit frequently
- When making trade-offs, run `/speckit.agentic.document-decisions` to capture them as ADRs
- The `after_implement` hook offers a code review

**Step 4: Review** *(fresh session)* -- `/speckit.agentic.code-review`

- Review changed files for correctness, clarity, and testing
- Run `/speckit.agentic.review-alignment` to check for drift between code and design docs

**Step 5: Create and review PR** *(fresh session)* -- `/speckit.agentic.review-pr`

- Push the branch and create a PR
- Run the pre-merge checklist: CI status, diff scope, documentation

**Step 6: Close out and merge** -- `/speckit.agentic.close-plan`

- Finalize docs/ updates before merge
- Move plan to completed in `docs/plans/README.md`
- Finalize any ADR drafts

### Periodic: Reflect and maintain

- Run `/speckit.agentic.extract-lessons` to surface patterns from recent work
- Run `/speckit.agentic.codebase-map` to keep `docs/design/codebase-map.md` current
- Run `/speckit.agentic.onboard` for new team members or re-familiarization

## Command Cadence

- **Every feature cycle**: specify -> plan -> start-work -> implement -> code-review -> review-alignment -> review-pr -> close-plan
- **Periodic**: extract-lessons, codebase-map, onboard
- **As needed**: document-decisions (during implementation), apply-rubric (any time)

## What to Avoid

- **Don't create parallel memory systems.** Commands read from and write to docs/; don't create separate output directories
- **Don't over-engineer.** Three focused commands used regularly beat ten gathering dust
- **Don't let the codebase map go stale.** A stale map is worse than no map
- **Don't restructure and change substance simultaneously.** When decomposing existing conventions into AGENTS.md files, do it as a pure restructuring first
