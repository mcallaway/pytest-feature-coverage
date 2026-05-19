---
description: Detect drift between code and documented design — two-way staleness check
---

# Review Alignment

Check whether the code matches the documented design and whether the documented design matches the code. This is a two-way check.

## User Input

$ARGUMENTS

## Purpose

Design documents describe the system as it currently is. Code changes can make design docs stale, and design docs can describe things that no longer exist in code. Both directions of drift are defects. This command detects them.

## Steps

### Step 1: Load design documents

Read all files in `docs/design/`. If none exist, report that no design docs are available and suggest running `/speckit.agentic.scaffold` first.

### Step 2: Load codebase map

Read `docs/design/codebase-map.md` if it exists. This maps features and concepts to code locations.

### Step 3: Code → Design check

For each significant code change (use `git diff main...HEAD` or examine the current source tree if $ARGUMENTS specifies a scope):

- Does the code introduce concepts, modules, or patterns not described in any design doc?
- Have any interfaces, data models, or architectural boundaries changed?
- Are there new dependencies not documented?

### Step 4: Design → Code check

For each design document:

- Do the concepts, class names, and relationships described still exist in code?
- Are the described interfaces still accurate?
- Does the documented data flow match actual behavior?

### Step 5: Codebase map accuracy

If `codebase-map.md` exists:

- Are all listed code locations still valid?
- Are new features or modules missing from the map?
- Have any listed files been moved or deleted?

### Step 6: Report findings

Organize findings:

**Code changed, docs stale:**

- [file] — [what changed] — [which design doc needs updating]

**Docs describe something that no longer exists:**

- [design doc] — [what's described] — [what actually exists now]

**Codebase map gaps:**

- [missing entry] or [stale entry]

If everything is aligned, say so clearly.

### Step 7: Suggest fixes

For each finding, suggest the minimal edit to restore alignment. Prefer updating the docs to match reality (docs describe current state, not desired state).

## Notes

- This command owns the staleness check. Other commands (code-review, review-pr) defer design-doc staleness to this command.
- Design docs should describe what IS, not what SHOULD BE. If the code is correct, update the doc.
- If the code is wrong, that's a bug — file it separately, don't update the design doc to match the bug.
