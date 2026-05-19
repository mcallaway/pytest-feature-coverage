---
description: Load context for a coding session — active plan, design docs, AGENTS.md, pre-flight checks
---

# Start Work

Load context and run pre-flight checks before beginning an implementation session.

## User Input

$ARGUMENTS

## Purpose

Before writing code, load the relevant context so you understand what to work on, what constraints apply, and what the current state of the project is. This prevents context loss between sessions and ensures continuity.

## Steps

### Step 1: Read instruction files

Read the following files (skip any that don't exist):

1. `AGENTS.md` (project root)
1. `AGENTS.local.md` (if present)
1. `src/AGENTS.md`
1. `tests/AGENTS.md`
1. `docs/AGENTS.md`

Acknowledge the guiding principles silently — do not recite them back.

### Step 2: Identify the active plan

Read `docs/plans/README.md`. Identify the **Current Focus** section. If a plan is listed there, read the full plan document. Report:

- Plan title and status
- Current phase
- What the next deliverable is

If no active plan exists, check if a Spec Kit feature is in-progress by looking at `.specify/specs/` for any active spec/plan/tasks. Report what you find.

### Step 3: Load design context

Read the following (skip any that don't exist):

1. `docs/design/codebase-map.md` — to understand feature-to-code mapping
1. Any design docs referenced by the active plan
1. The active spec (`.specify/specs/*/spec.md`) if working on a Spec Kit feature

### Step 4: Pre-flight checks

Report the following:

- **Branch**: Current git branch name
- **Uncommitted changes**: Any modified/untracked files (warn if present)
- **Active plan**: Title and phase, or "none"
- **Active spec**: Feature name, or "none"

### Step 5: Summarize and await direction

Present a concise summary:

```text
Ready to work.
  Plan:   [plan title] — Phase [N]: [phase name]
  Spec:   [spec name] or "none"
  Branch: [branch name]
  ⚠️     [any warnings about uncommitted changes]
```

Then ask: "What would you like to work on?"

## Notes

- This command is the recommended way to start every coding session
- It replaces the need to manually read multiple files at session start
- If the user provides $ARGUMENTS describing what they want to work on, skip the final question and proceed
