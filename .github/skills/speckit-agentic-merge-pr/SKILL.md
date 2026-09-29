---
name: speckit-agentic-merge-pr
description: Merge the pull request and sync local state — human-invoked terminal
  action after review-pr passes
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: bayer-int
  source: extension:agentic
---

# Agentic Merge Pr Skill

# Merge PR

Merge the pull request that `/speckit.agentic.review-pr` confirmed is ready, then sync local state: switch to the default branch, pull, and prune branches already merged. This command performs an actual merge -- it must only run because a human explicitly invoked it, never as an automatic continuation of `/speckit.agentic.full-workflow` or any other command (see ADR-011).

## User Input

$ARGUMENTS

An optional PR number. If omitted, operate on the PR for the current branch.

## Purpose

`/speckit.agentic.review-pr`'s "Ready to merge" verdict names merging as the only remaining action but does not perform it -- a human still decides when to merge (after any required external approvals, branch protection checks, or team process) and issues the command themselves. This command exists to make that human-issued action reliable and consistent: verify the PR is genuinely mergeable, merge it, then handle the housekeeping (switch to the default branch, pull, delete merged branches) that is otherwise easy to forget or get wrong. Running this command is itself the human decision to merge; it is never triggered on the agent's own initiative.

## Steps

### Step 1: Verify merge readiness

Do not proceed on assumption alone. Check the live state:

```bash
gh pr checks
gh pr view --json mergeable,mergeStateStatus,reviewDecision
```

- If any CI check is failing, `mergeable` is not `MERGEABLE`, or `mergeStateStatus` is not `CLEAN`: stop and report exactly what is blocking, the same way `/speckit.agentic.review-pr` would. Do not merge.
- If a review is required by branch protection and `reviewDecision` shows it is outstanding, stop and report that too.

### Step 2: Merge

Merge using the repository's established convention. Unless project documentation says otherwise, check recent history for the convention in use (`git log --oneline --merges -10`, or `gh pr list --state merged --limit 5`) -- a single commit per PR titled after the PR indicates squash merges:

```bash
gh pr merge --squash --delete-branch
```

Never force a merge past a failing check or a conflicted state to satisfy this command; Step 1 should already have stopped you before this point if something is blocking.

### Step 3: Sync local state

```bash
git checkout main   # or the repository's actual default branch
git pull
```

### Step 4: Prune merged local branches

List local branches already merged into the default branch (never the default branch itself):

```bash
git branch --merged main | grep -v '^\*\|main$'
```

Delete each with `git branch -d <branch>` (not `-D`). If it refuses because of unmerged commits, report that rather than forcing it.

### Step 5: Report

State:

- The PR that was merged and its merge commit
- That local state now matches the merged default branch, and which local branches were pruned
- If the repository uses release-please: a release PR is expected to appear or update shortly, driven by the conventional-commit types in the merged history. Merging that PR later is a separate, later invocation of this same command.

## Notes

- This command performs an irreversible action on shared history. It must only run because a human explicitly typed `/speckit.agentic.merge-pr` (or equivalent) -- never as an automatic continuation of `/speckit.agentic.full-workflow`, `/speckit.agentic.review-pr`, or any other command (see ADR-011).
- `/speckit.agentic.full-workflow`'s hand-off step (`/speckit.agentic.guided-pr-review`) remains its own terminal step; it names this command as the expected next human action but does not invoke it.
- If the repository's branch protection requires specific approvals or a different merge method, defer to those over this command's defaults.
