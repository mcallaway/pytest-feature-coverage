# Agentic Development Workflow Guide

Quick reference and lifecycle guide for the agentic development pattern. For the design rationale, see [the design doc](../design/001-agentic-development-pattern.md).

## Ceremony Tiers

Use these four names. Do not invent others.

| Tier         | When                                                                                                     | What to run                                                                                                                                |
| ------------ | -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **Trivial**  | Obvious one-line or local fix. No new behavior, no new tests.                                            | Fix, commit, open a PR. Do not run Spec Kit or agentic commands.                                                                           |
| **Light**    | Contained bug with a reproduction in one well-understood unit. No new acceptance criteria or interfaces. | `/speckit.agentic.full-workflow` (light path): TDD, code-review, apply-rubric, close-plan (lightweight), review-pr. No specify/plan/tasks. |
| **Standard** | New behavior, new acceptance criteria, or a change across modules or a shared interface.                 | `/speckit.agentic.full-workflow` (standard path): specify through close-plan and review-pr, plus a `docs/features/` entry.                 |
| **Escalate** | Architecture or cross-cutting design.                                                                    | Stop. A human decides. Do not pick light or standard to keep moving.                                                                       |

When uncertain between light and standard, choose standard.

## How to Invoke Commands

Commands install as `SKILL.md` files. Invoke them as slash commands (`/speckit.specify`, `/speckit.agentic.full-workflow`, and so on).

| Agent          | Skill tree        | Init key       |
| -------------- | ----------------- | -------------- |
| GitHub Copilot | `.github/skills/` | `copilot`      |
| Claude Code    | `.claude/skills/` | `claude`       |
| Cursor         | `.cursor/skills/` | `cursor-agent` |

A project can keep more than one tree installed. Copilot is not multi-install safe, so adding Claude or Cursor after Copilot needs `specify integration install <key> --force`. `specify integration status` then reports `ERROR` / `unsafe-multi-install: copilot`; that is expected, and the skills still work.

## Feature Development Lifecycle

Commands in the order you would use them for a new feature:

| Phase         | Command                              | Purpose                                                        |
| ------------- | ------------------------------------ | -------------------------------------------------------------- |
| Every session | `speckit.agentic.start-work`         | Load active plan, design docs, and context                     |
| Specify       | `speckit.specify`                    | Write feature spec with user stories and acceptance criteria   |
| Specify       | `speckit.clarify`                    | Refine ambiguous requirements (optional)                       |
| Plan          | `speckit.plan`                       | Define architecture and phases                                 |
| Plan          | `speckit.tasks`                      | Generate ordered, dependency-aware implementation tasks        |
| Build         | `speckit.implement`                  | Execute the tasks                                              |
| Build         | `speckit.agentic.document-decisions` | Capture trade-offs as ADRs during implementation               |
| Review        | `speckit.agentic.review-alignment`   | Check for drift between code and design docs                   |
| Review        | `speckit.agentic.apply-rubric`       | Evaluate artifacts (design docs, ADRs, spec) against rubrics   |
| Review        | `speckit.agentic.code-review`        | Review correctness, tests, and clarity (auto-offered via hook) |
| Review        | `speckit.agentic.extract-lessons`    | Surface reusable patterns from recent work (optional)          |
| Finalize      | `speckit.agentic.close-plan`         | Update plan status, finalize ADRs, flag loose ends             |
| Finalize      | `speckit.agentic.review-pr`          | Pre-merge CI, diff scope, and docs check                       |
| Merge         | `speckit.agentic.merge-pr`           | Human-invoked: merge the PR, sync local state (see ADR-011)    |

Other commands:

| Command                        | Purpose                                                                   |
| ------------------------------ | ------------------------------------------------------------------------- |
| `speckit.agentic.onboard`      | Walk a new team member (or yourself after time away) through the codebase |
| `speckit.agentic.codebase-map` | Refresh the feature-to-code mapping in `docs/design/codebase-map.md`      |

## Workflow Details

### Feature Development

Use this workflow for any new capability that merits a specification.

- **Specify**: Run `speckit.specify`. Creates a spec with user stories and acceptance criteria. Consider creating a project-level feature doc in `docs/features/` -- the spec (`specs/NNN/spec.md` by default, or `.specify/specs/NNN/spec.md` for a legacy-path feature) is branch-scoped; the feature doc persists.
- **Clarify**: Run `speckit.clarify` to refine ambiguous requirements.
- **Plan**: Run `speckit.plan` to define architecture and phases. It also creates or updates a paired `docs/plans/NNN.md` project-level entry, cross-referenced to the new plan; update `docs/plans/README.md` to point to it. The `after_plan` hook offers to evaluate both against the rubric.
- **Tasks**: Run `speckit.tasks` to generate ordered, dependency-aware tasks.
- **Implement**: Run `speckit.implement`. Run `speckit.agentic.document-decisions` whenever you make a trade-off that isn't obvious from the code.
- **Review**: Run `speckit.agentic.review-alignment` first to catch drift between the change and existing design docs. Run `speckit.agentic.apply-rubric` on any artifacts created or changed (design docs, ADRs, spec) once alignment is fixed -- `apply-rubric` is most valuable post-implementation: design doc rubrics check "matches code", a criterion that can only be evaluated once the code exists and drift is resolved. Run `speckit.agentic.code-review` last among these three, so it reviews the settled diff rather than a version about to change again. Optionally run `speckit.agentic.extract-lessons` to surface reusable patterns before they get buried -- it can also identify implicit decisions worth capturing as ADRs, which `close-plan` then finalizes.
- **Finalize**: Run `speckit.agentic.close-plan` first -- it updates plan status, finalizes ADRs, and produces the final documentation commit. Push that commit, then run `speckit.agentic.review-pr` so its CI check and diff review cover the true final state. Its "Ready to merge" verdict is the last checkpoint (see ADR-010).
- **Merge**: Once satisfied (including after `speckit.agentic.guided-pr-review`, if used), invoke `speckit.agentic.merge-pr` yourself: it verifies the PR is genuinely mergeable, merges it, and syncs local state (default branch, pull, prune merged branches). It only ever runs because a human explicitly invoked it -- never as an automatic continuation of another command (see ADR-011). This ends the unit of work for this branch -- no further commits should be added to it. Anything discovered afterward (a missed doc update, a follow-on idea) is new work: start a new branch, and a new spec/plan if warranted.

### Bug Fixes

Match the ceremony table above.

- **Trivial**: just fix it, commit, open a PR.
- **Light**: skip specify/plan/tasks. Start-work, TDD the fix, code-review, apply-rubric, close-plan (lightweight), review-pr, then merge. Or run `/speckit.agentic.full-workflow`.
- Larger bugs (new acceptance criteria or multiple components) are **standard**, not light.

### Refactors and Maintenance

- `speckit.agentic.start-work` -- load project context
- `speckit.agentic.review-alignment` -- understand what design docs say about the area first
- Make the changes
- `speckit.agentic.document-decisions` -- capture architectural choices made
- Update `docs/design/` if the system's architecture changed
- `speckit.agentic.code-review` -- review the result

### Session Discipline

Start every session with `speckit.agentic.start-work`. It loads the current plan, recent decisions, `AGENTS.md` rules, and any in-progress specs.

End every session with:

- `speckit.agentic.code-review` if you made code changes
- An update to `docs/plans/README.md` if priorities shifted

## Adopting This Pattern

### For a new project

- Run `speckit.agentic.scaffold` to create the docs/ tree and AGENTS.md layering
- Create the codebase map early with `speckit.agentic.codebase-map`
- Start using the feature lifecycle above for your first piece of work

### For an existing project

- Run `speckit.agentic.scaffold` -- it skips files that already exist
- Restructure any existing conventions into AGENTS.md files (preserve substance, change delivery)
- Run `speckit.agentic.codebase-map` to document what already exists
- Adopt the lifecycle incrementally, starting with code-review and document-decisions

## What to Avoid

- **Don't create parallel memory systems.** Commands read from and write to docs/; don't create separate output directories.
- **Don't over-engineer.** Three focused commands used regularly beat ten gathering dust.
- **Don't let the codebase map go stale.** A stale map is worse than no map.
- **Don't restructure and change substance simultaneously.** When decomposing existing conventions into AGENTS.md files, do it as a pure restructuring first.
