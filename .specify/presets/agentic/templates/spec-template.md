______________________________________________________________________

## Agentic Workflow: Project Memory

> This section is added by the agentic-workflow preset. It connects per-feature specs to the project-level knowledge in `docs/`.

### TTL Metadata

- **TTL**: short -- this spec is actively being refined; archive or promote to `docs/features/` once the feature is implemented and stable.
- **Author(s)**: [who wrote this spec]
- **Audience(s)**: Agents implementing the feature; humans reviewing scope.

### Project Context

Before writing acceptance scenarios, check:

- `docs/features/` -- does a project-level feature doc already exist for this? If so, this spec should refine it, not duplicate it.
- `docs/decisions/` -- are there ADRs that constrain how this feature can be built? Reference them in the Technical Context section.
- `docs/design/` -- does the current design documentation describe components this feature will modify?

### Quality Gate

After completing this spec, evaluate it against `docs/features/RUBRIC.md`:

- [ ] All three parts of the user story are present and distinct
- [ ] Each acceptance criterion is independently falsifiable
- [ ] Criteria describe user-observable behavior, not implementation steps
- [ ] Edge cases and failure modes are represented
