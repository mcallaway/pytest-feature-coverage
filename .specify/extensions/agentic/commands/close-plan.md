---
description: Pre-merge finalization — update plan status, finalize ADRs, flag loose ends
---

# Close Plan

Pre-merge finalization, run before `/speckit.agentic.review-pr`. Updates plan status, verifies documentation accuracy, finalizes ADRs, and flags loose ends.

## User Input

$ARGUMENTS

## Purpose

Before merging, ensure the project's documentation accurately reflects the work that was done. Plans are closed, ADRs are finalized, design docs are current, and no pending updates remain. This step produces the final documentation commit for the PR -- run `/speckit.agentic.review-pr` immediately afterward so its CI and diff review cover that final state (see ADR-010).

## Steps

### Step 1: Identify the active plan

Read `docs/plans/README.md` and identify the project-level plan in **Current Focus**. If `$ARGUMENTS` specifies a plan, use that instead.

If no active project-level plan is found, resolve the current feature's Spec Kit artifacts (via `.specify/feature.json`'s `feature_directory` key or `SPECIFY_FEATURE_DIRECTORY`, not a hardcoded path -- the current default location is top-level `specs/NNN/`; some existing features may still live at the legacy `.specify/specs/NNN/` path) and read those. Do not treat the absence of a `docs/plans/` entry as settled by this alone: judge whether this work's project-story significance warrants creating one now (see Step 5) before concluding there is nothing to close at the project-plan layer.

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

1. If a project-level `docs/plans/NNN.md` entry exists for this work (from Step 1, or created during `/speckit.plan`): update the status header to COMPLETE, and in `docs/plans/README.md`, move it from **Current Focus** to **Completed**, updating **Next Steps** if appropriate.
1. If no `docs/plans/NNN.md` entry exists yet and Step 1's judgment concluded this work does warrant one (a meaningful change in project direction, or a recurring class of issue worth tracking -- not every fix qualifies), create it now: `Status: COMPLETE` from the start, cross-referenced to this work's `specs/NNN/` (or `.specify/specs/NNN/`) artifacts, and add it directly to `docs/plans/README.md`'s **Completed** section. State the reasoning for creating it at close time rather than during planning.
1. If Step 1's judgment concluded no project-level entry is warranted, state that conclusion explicitly rather than leaving it ambiguous whether the omission was a decision or an oversight.

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

- Run this BEFORE `/speckit.agentic.review-pr`. This step's commit needs to be part of what review-pr and CI evaluate; running it after review-pr's "Ready to merge" verdict makes that verdict stale the moment this step pushes a new commit (see ADR-010).
- After `/speckit.agentic.review-pr` passes following this step, the only remaining action is a human merging the PR. Do not plan or run further commits against this branch after that -- new work is a new branch.
- If working with Spec Kit features, also verify the spec's acceptance criteria are met
