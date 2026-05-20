---
description: Capture trade-offs and non-obvious choices as ADR drafts during implementation
---

<!-- Extension: agentic -->

<!-- Config: .specify/extensions/agentic/ -->

# Document Decisions

Capture trade-offs and non-obvious choices made during implementation as Architecture Decision Records.

## User Input

$ARGUMENTS

## Purpose

During implementation, decisions are made that are hard to reverse and worth recording: choosing one library over another, picking a data model shape, selecting an API style. This command captures those decisions while the context is fresh, routing them to the right artifact.

## Steps

### Step 1: Identify the decision

If `$ARGUMENTS` describes a decision, use that. Otherwise, ask:

- What decision was made?
- What alternatives were considered?
- Why was this option chosen?

### Step 2: Classify the decision

Route the output based on what kind of decision it is:

**Hard-to-reverse → ADR draft** Decisions about architecture, data models, dependencies, or interfaces that would be costly to change later.

**Design change → Design doc update** Changes to how the system works that should be reflected in `docs/design/`. Append to a "Pending Updates" section in the relevant design doc.

**Implementation note → Commit message** Tactical choices (algorithm selection, error handling approach) that are worth documenting but don't need a standalone record. Suggest commit message content.

### Step 3: Create the artifact

**For ADRs**, create a new file in `docs/decisions/`:

Filename: `NNN-short-description.md` (next sequential number)

```markdown
# NNN. [Decision Title in Imperative Mood]

- **Status**: Proposed
- **Date**: [today's date, ISO 8601]
- **Deciders**: [who was involved]

## Context

[What prompted this decision. What constraints applied.]

## Decision

[What was decided. Imperative mood: "Use X" not "We decided to use X"]

## Alternatives Considered

### [Alternative 1]
[Why it was rejected]

### [Alternative 2]
[Why it was rejected]

## Consequences

### Positive
- [benefit]

### Negative
- [cost or risk]
```

Update `docs/decisions/README.md` index with the new entry.

**For design doc updates**, append to the relevant design doc:

```markdown
## Pending Updates

- [date]: [description of what changed and why] (from [plan/feature reference])
```

**For commit messages**, suggest the content but do not commit automatically.

### Step 4: Confirm

Report what was created and where. If an ADR, remind the user that it will be finalized during `/speckit.agentic.close-plan`.

## Notes

- This command is lightweight by design. Run it whenever a decision is made — don't batch decisions.
- ADRs start as Proposed. They become Accepted during close-plan.
- The ADR format follows Michael Nygard's original template with minor additions.
