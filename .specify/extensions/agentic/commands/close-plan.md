---
description: Pre-merge finalization — update plan status, finalize ADRs, flag loose ends
---

# Close Plan

Pre-merge finalization after `/speckit.agentic.review-pr` passes. Updates plan status, verifies documentation accuracy, finalizes ADRs, and flags loose ends.

## User Input

$ARGUMENTS

## Purpose

Before merging, ensure the project's documentation accurately reflects the work that was done. Plans are closed, ADRs are finalized, design docs are current, and no pending updates remain.

## Steps

### Step 1: Identify the active plan

Read `docs/plans/README.md` and identify the plan in **Current Focus**. If `$ARGUMENTS` specifies a plan, use that instead.

If no active plan is found, check `.specify/specs/` for the current feature's artifacts and work with those.

### Step 2: Verify plan completion

Read the plan document. For each phase and deliverable:

- Is the deliverable present and functional?
- Are any phases incomplete? If so, should they be deferred to a follow-up plan?

Report any gaps.

### Step 3: Finalize ADRs

Check `docs/decisions/` for any ADRs in **Proposed** status that were created during this work. For each:

- Is the decision still correct given the implementation?
- Update status from Proposed to Accepted (with today's date)
- Verify context and consequences are accurate

### Step 4: Check design doc pending updates

Read design docs in `docs/design/`. Look for any "Pending Updates" sections or TODO markers that reference this plan or feature. Apply those updates now or flag them explicitly.

### Step 5: Update plan status

1. In the plan document, update the status header to COMPLETE
1. In `docs/plans/README.md`:
   - Move the plan from **Current Focus** to **Completed**
   - Update **Next Steps** if appropriate

### Step 6: Final commit

Stage all documentation changes and commit:

```bash
git add docs/
git commit -m "docs: close plan NNN -- [plan title]"
```

### Step 7: Flag loose ends

Report any items that need follow-up:

- Deferred phases that need a new plan
- Open questions that were not resolved
- Design docs that need deeper updates beyond what was done here
- New features or bugs discovered during implementation

## Notes

- Run this AFTER `/speckit.agentic.review-pr` confirms the PR is ready
- This is the last step before merge
- If working with Spec Kit features, also verify the spec's acceptance criteria are met
