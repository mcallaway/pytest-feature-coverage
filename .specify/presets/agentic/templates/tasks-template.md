______________________________________________________________________

## Agentic Workflow: Post-Implementation Checklist

> This section is added by the agentic-workflow preset. It prompts for review and documentation steps after the tasks are complete.

### After All Tasks Complete

1. **Code Review**: Run `/speckit.agentic.code-review` to evaluate the implementation against the spec's acceptance criteria.

1. **Design Alignment**: If architectural changes were made, run `/speckit.agentic.review-alignment` to check for drift between `docs/design/` and the actual implementation.

1. **Decision Capture**: If any trade-offs or technology choices were made during implementation, run `/speckit.agentic.document-decisions` to capture them as ADRs in `docs/decisions/`.

1. **Plan Close-out**: Run `/speckit.agentic.close-plan` to finalize the plan and move it to the completed section of `docs/plans/README.md`.

1. **Lesson Extraction**: If reusable patterns emerged, run `/speckit.agentic.extract-lessons` to promote them to `docs/guides/` or `docs/design/`.
