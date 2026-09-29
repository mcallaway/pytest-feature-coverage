---
name: speckit-agentic-review-pr
description: Comprehensive pre-merge PR review — CI status, code, docs, staleness
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: bayer-int
  source: agentic:commands/review-pr.md
---

# Review Pull Request

Comprehensive pre-merge review covering CI status, code quality, documentation completeness, and merge readiness. Run this after `/speckit.agentic.close-plan` so it evaluates the final commit set, including close-plan's documentation commit.

## User Input

$ARGUMENTS

## Purpose

Before merging a PR, verify that everything is in order: CI is green, code is reviewed, documentation is current, and no loose ends remain. This is the final gatekeeper before merge -- the only action that should follow a passing "Ready to merge" verdict from this command is a human merging the PR (see ADR-010). If more work is discovered after this point, it belongs on a new branch, not another commit here.

## Steps

### Step 1: Check local state

- Verify you're on the feature branch (not main)
- Check for uncommitted changes (warn if present)
- Verify the branch is pushed to remote

### Step 2: Check PR status

If `gh` CLI is available:

```bash
gh pr status
gh pr checks
```

Report:

- PR title and number
- CI check status (pass/fail/pending)
- Review status (approved/changes requested/pending)
- Merge conflicts (yes/no)

If `gh` is not available, skip this step and note it.

### Step 3: Code review

Perform the same review as `/speckit.agentic.code-review` on the PR diff:

```bash
git diff main...HEAD
```

### Step 4: Documentation check

Verify documentation completeness:

1. **Plan**: Does `docs/plans/README.md` reference the active project plan? Is its cross-referenced implementation-level plan (`specs/NNN/plan.md`, or `.specify/specs/NNN/plan.md` for a legacy-path feature) current?
1. **Feature**: If this implements a feature, does `docs/features/` have a spec?
1. **ADRs**: Were any architectural decisions made? Are they captured in `docs/decisions/`?
1. **Design**: Do any design docs need updating based on these changes?
1. **Spec Kit artifacts**: If working with a feature's specs directory (resolved via `.specify/feature.json`/`SPECIFY_FEATURE_DIRECTORY`, not a hardcoded path), are spec/plan/tasks complete?

### Step 5: Final assessment

Report one of:

- **Ready to merge** — all checks pass, code reviewed, docs current. Say explicitly that the only next action is a human merging the PR; nothing else should be committed to this branch afterward.
- **Blocked** — list what needs to be resolved before merge
- **Needs discussion** — list open questions that require human judgment

## Notes

- If CI checks are failing, report the failures clearly and suggest fixes
- Design-doc staleness is flagged here but detailed analysis belongs in `/speckit.agentic.review-alignment`
- This command runs after `/speckit.agentic.close-plan`, evaluating the final commit set that includes close-plan's documentation commit (see ADR-010). It is the last step before a human merges the PR.