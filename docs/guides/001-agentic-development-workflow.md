# Agentic Development Workflow Guide

Quick reference and lifecycle guide for the agentic development pattern. For the design rationale, see [the design doc](../design/001-agentic-development-pattern.md).

## How to Invoke Commands

Commands are installed as both `.agent.md` and `.prompt.md` files in `.github/`. They surface differently depending on your AI tool:

| Surface              | Agents (`.agent.md`)                                     | Prompts (`.prompt.md`)                          |
| -------------------- | -------------------------------------------------------- | ----------------------------------------------- |
| VS Code Copilot Chat | Select from the agent mode picker in the chat input      | Type `/command-name` as a slash command         |
| Copilot CLI          | `/agent command-name` or ask the agent to invoke by name | Not directly invokable -- use the agent instead |

## Feature Development Lifecycle

Commands in the order you would use them for a new feature:

| Phase         | Command                              | Purpose                                                        |
| ------------- | ------------------------------------ | -------------------------------------------------------------- |
| Every session | `speckit.agentic.start-work`         | Load active plan, design docs, and context                     |
| Specify       | `speckit.specify`                    | Write feature spec with user stories and acceptance criteria   |
| Specify       | `speckit.clarify`                    | Refine ambiguous requirements (optional)                       |
| Plan          | `speckit.plan`                       | Define architecture and phases                                 |
| Build         | `speckit.tasks`                      | Generate ordered, dependency-aware implementation tasks        |
| Build         | `speckit.implement`                  | Execute the tasks                                              |
| Build         | `speckit.agentic.document-decisions` | Capture trade-offs as ADRs during implementation               |
| Review        | `speckit.agentic.code-review`        | Review correctness, tests, and clarity (auto-offered via hook) |
| Review        | `speckit.agentic.review-alignment`   | Check for drift between code and design docs                   |
| Review        | `speckit.agentic.apply-rubric`       | Evaluate artifacts (design docs, ADRs, spec) against rubrics   |
| Finalize      | `speckit.agentic.close-plan`         | Update plan status, finalize ADRs, flag loose ends             |
| Finalize      | `speckit.agentic.review-pr`          | Pre-merge CI, diff scope, and docs check                       |
| Post-merge    | `speckit.agentic.extract-lessons`    | Surface reusable patterns from recent work (optional)          |

Other commands:

| Command                        | Purpose                                                                   |
| ------------------------------ | ------------------------------------------------------------------------- |
| `speckit.agentic.onboard`      | Walk a new team member (or yourself after time away) through the codebase |
| `speckit.agentic.codebase-map` | Refresh the feature-to-code mapping in `docs/design/codebase-map.md`      |

## Workflow Details

### Feature Development

Use this workflow for any new capability that merits a specification.

- **Specify**: Run `speckit.specify`. Creates a spec with user stories and acceptance criteria. Consider creating a project-level feature doc in `docs/features/` -- the spec in `.specify/specs/` is branch-scoped; the feature doc persists.
- **Clarify**: Run `speckit.clarify` to refine ambiguous requirements.
- **Plan**: Run `speckit.plan` to define architecture and phases. Update `docs/plans/README.md` to point to the active plan. The `after_plan` hook offers to evaluate the plan against the rubric.
- **Tasks**: Run `speckit.tasks` to generate ordered, dependency-aware tasks.
- **Implement**: Run `speckit.implement`. Run `speckit.agentic.document-decisions` whenever you make a trade-off that isn't obvious from the code.
- **Review**: Run `speckit.agentic.code-review`, then `speckit.agentic.review-alignment`, then `speckit.agentic.apply-rubric` on any artifacts created or changed (design docs, ADRs, spec). `apply-rubric` is most valuable post-implementation: design doc rubrics check "matches code" -- a criterion that can only be evaluated once the code exists.
- **Finalize**: Run `speckit.agentic.close-plan` to update plan status and confirm ADRs are written. Run `speckit.agentic.review-pr` as the final pre-merge check.

### Bug Fixes

For small, well-understood bugs, skip specify/plan/tasks/close-plan:

- `speckit.agentic.start-work` -- load project context
- Fix the bug
- `speckit.agentic.code-review` -- verify the fix
- `speckit.agentic.review-pr` -- pre-merge check

For bugs touching multiple components, consider `speckit.specify` and `speckit.plan` to capture scope first.

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
