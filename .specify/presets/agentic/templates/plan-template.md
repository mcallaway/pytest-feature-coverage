______________________________________________________________________

## Agentic Workflow: Project Memory

> This section is added by the agentic-workflow preset. It connects plans to the project-level knowledge in `docs/`.

### TTL Metadata

- **TTL**: short -- this plan is actively being worked; update each session.
- **Author(s)**: [who created this plan]
- **Audience(s)**: Fresh agent sessions resuming work; humans tracking progress.

### Project Context

Before finalizing phases, check:

- `docs/plans/README.md` -- update the "Current Focus" section to point to this plan.
- `docs/features/` -- does the motivating feature doc exist? Link to it in the Summary section above.
- `docs/design/` -- will this plan change the system's architecture? If so, note which design docs will need updating.

### Decision Capture Reminder

During implementation, watch for decisions that should become ADRs:

- Technology choices that are hard to reverse
- Trade-offs between competing approaches
- Constraints discovered during research

Use `/speckit.agentic.document-decisions` to capture these as they arise.

### Quality Gate

The `after_plan` hook will offer to evaluate this plan against `docs/plans/RUBRIC.md`. You can also run it manually: `/speckit.agentic.apply-rubric docs/plans/RUBRIC.md`
