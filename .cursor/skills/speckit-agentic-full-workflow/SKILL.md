---
name: speckit-agentic-full-workflow
description: Take a bug report or feature request through to an open, reviewable pull request
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: bayer-int
  source: agentic:commands/full-workflow.md
---

# Go To Work

Hand this command a bug report or feature request and a one-line goal. It runs the full lifecycle, test-driven implementation, review, and pull request creation, and stops with an open PR ready for a human to walk through. You do not need to invoke any other command yourself; this one sequences them.

## User Input

$ARGUMENTS

A path to a bug report or feature request file, plus an optional one-line goal if the file needs framing.

## Roles

You are the Team Leader for this task. You own it end to end: reading the input, running the lifecycle below, and reporting back with a PR link.

Delegate to a sub-agent only where independence is the actual value, not for specialization or parallelism on their own. Fan-out that is not earning its cost is a known failure mode. Default to doing steps yourself.

- Stays in your own loop: reading the input, `/speckit.agentic.start-work`, `/speckit.specify`, `/speckit.clarify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement` (including tests), inline `/speckit.agentic.document-decisions`, `/speckit.agentic.review-alignment`. These are cumulative, each step builds on context you already hold, and handing off would mean paying to re-derive it for no benefit.
- Delegate to a sub-agent: `/speckit.agentic.code-review`, `/speckit.agentic.apply-rubric`, and `/speckit.agentic.guided-pr-review`. These are second-opinion steps. You reviewing your own work is structurally worse at catching your own blind spots than a fresh, unbiased context is, and that independence is the entire point of these three.
- Delegate conditionally: broad exploratory research during specify or plan, when the work touches a part of the codebase you have not already loaded. A single grep does not need a sub-agent.
- If your environment has no sub-agent delegation available, run the delegated steps yourself as a distinct, fresh-context pass instead of skipping them. The isolation matters more than the mechanism.

## Steps

### Step 1: Orient

- Run `/speckit.agentic.start-work` to load the active plan, recent decisions, AGENTS.md rules, and any in-progress specs.
- Read the input file in full before doing anything else.
- Check what capabilities the target repo has adopted (a pytest-feature-coverage dependency, an adoption manifest if present, or similar) so you know which gates apply later. The exact detection mechanism is not settled; use your judgment and say what you checked.
- Decide the ceremony tier. Use these names and no others:
  - **Trivial**: obvious one-line or local fix, no new behavior, no new tests. This command is the wrong tool. Stop, say so, and tell the human to just fix, commit, and open a PR. Do not run specify, plan, or review commands.
  - **Light**: a clear reproduction against one well-understood file or function, no new acceptance criteria, no new interfaces.
  - **Standard**: new behavior, new acceptance criteria, or changes touching multiple modules or an interface other code depends on.
  - **Escalate**: architecture change or cross-cutting design decisions. Stop and ask a human rather than proceeding as light or standard.
  - When genuinely uncertain between light and standard, choose standard. The cost of unnecessary ceremony on a task that turns out simple is smaller than the cost of skipping a spec on a task that turns out to need one.
- State the tier you chose and why before proceeding. If the tier is trivial or escalate, stop after stating it.
- Every change gets its own branch. Never work directly on the default branch.

### Step 2: Light path (bugfix)

Skip this step if you chose the standard path.

- Read the bug report, write a failing test that reproduces it, implement the fix, watch the test pass. Prefer the smallest diff that makes the test pass over a broader refactor, unless the root cause genuinely requires one. If the fix turns out to be larger than expected mid-loop, stop and switch to the standard path rather than continuing to push scope through this lightweight one.
- Run `/speckit.agentic.document-decisions` only if a non-obvious tradeoff was made.
- Delegate: run `/speckit.agentic.code-review`.
- Delegate: run `/speckit.agentic.apply-rubric` against the changed source and test files, unconditionally.
- Continue to Step 4.

### Step 3: Standard path (feature)

Skip this step if you chose the light path.

- Run `/speckit.specify` for a spec with acceptance criteria. Also write a persistent, durable feature doc under `docs/features/`, not just a branch-scoped spec, since this is a real feature.
- Run `/speckit.clarify`, only if genuine ambiguity remains after reading the request.
- Run `/speckit.plan`. It produces the branch-scoped `specs/NNN/plan.md` (or `.specify/specs/NNN/plan.md`, for repos still on the legacy Spec Kit location -- see `docs/decisions/009-docs-plans-pairing-and-specs-location.md`). In the same step, create or update the paired project-level entry in `docs/plans/`:
  - If no `docs/plans/MMM.md` project plan exists yet for this feature, create one (attempting `MMM` = `NNN` when nothing prevents it, e.g. a fresh project with no pre-existing `docs/plans/` numbering) with a Status/Phases/Close-out structure, and an explicit cross-reference link to `specs/NNN/plan.md`. Update `docs/plans/README.md`'s Current Focus to reference the new entry.
  - If an existing `docs/plans/MMM.md` project plan already covers a multi-phase initiative that this `specs/NNN/` effort is one phase of, update that existing entry (add the new phase, add the new cross-reference) instead of creating a duplicate.
  - The cross-reference link, not matching `MMM`/`NNN` numbers, is what pairs the two documents; repos with pre-existing, independent `docs/plans/` numbering are not expected to renumber anything.
- Run `/speckit.tasks` followed by `/speckit.implement`, test-first. Strongly prefer writing the failing test before the implementation; allow judgment when strict ordering does not fit the change.
- Run `/speckit.agentic.document-decisions` inline, whenever a non-obvious tradeoff is made, not saved up for the end.
- Run `/speckit.agentic.review-alignment` yourself, checking the change against the project's existing design docs for drift. You already hold the context needed for this; do not delegate it.
- Delegate: run `/speckit.agentic.apply-rubric` against the changed source and test files, and any design docs, architecture decisions, or specs that changed, once alignment is fixed.
- Delegate: run `/speckit.agentic.code-review` last, so it reviews the settled diff rather than a version about to change again.
- Continue to Step 4.

### Step 4: Open the pull request

Confirm the done gate before opening anything:

- Tests pass.
- Feature coverage is defined and met, where a coverage plugin is adopted.
- Coverage thresholds and other programmatic rules pass.
- Docs are updated appropriately for the tier: a feature doc only for real features, never for bugfixes.
- Rubric evaluation has passed.
- Code review is green.

If any of these are not satisfied, stop and report what is missing rather than opening a PR against a red state.

Push the branch and open the pull request. Never merge, force-push, or delete anything; that stays a human action. Reference the relevant plan, spec, or decision records in the PR description. Report the PR link. Continue to Step 5.

### Step 5: Finalize

Run `/speckit.agentic.close-plan` yourself, against the now-open PR:

- Standard path: update plan status, confirm decision records are written, resolve anything flagged as deferred.
- Light path: a lightweight close. Judge whether this bugfix changes the project's story or represents a recurring class of issue worth tracking:
  - If it is a pure, scoped defect fix with no project-story impact, no new `docs/plans/` entry is needed -- state that judgment explicitly rather than silently skipping it.
  - If the fix reflects a meaningful change in direction or a recurring issue worth tracking, create a short `docs/plans/NNN.md` entry (`Status: COMPLETE` from the start, cross-referenced to this branch's `specs/` work) even though this is the light path.

Push whatever commit close-plan produced. Then run `/speckit.agentic.review-pr` yourself: CI status, diff scope, documentation completeness -- evaluated against that final commit, not an earlier one (see ADR-010).

Report review-pr's verdict. If it is "Ready to merge," say explicitly that the only remaining action is a human merging the PR, and that this workflow does not resume on this branch afterward -- any further work is a new branch.

### Step 6: Hand off for human review

Delegate: run `/speckit.agentic.guided-pr-review`. It reads the design docs and plan first, then surveys commits, then walks the diff file by file, explaining concepts as they arise, then returns to the acceptance criteria and confirms each one, then gives a closing summary with a suggested verdict. This is the terminal step for this command. Do not proceed past it -- in particular, do not run `/speckit.agentic.merge-pr` yourself as a continuation of this sequence.

Tell the human that once they are satisfied with the guided review, `/speckit.agentic.merge-pr` is the expected next command: it merges the PR and syncs local state, but only runs because a human explicitly invokes it (see ADR-011). Once merged, do not propose or make further commits against this branch.

## Notes

- Two of the steps above, the light-path TDD entry and pull request creation, are described inline here rather than as separately named commands. If this prompt is later split into smaller composable commands, those two are the natural seams.
- Sub-agent delegation assumes an environment with real sub-agent tooling. On surfaces without it, run the delegated steps as a distinct pass with fresh context instead of skipping them.