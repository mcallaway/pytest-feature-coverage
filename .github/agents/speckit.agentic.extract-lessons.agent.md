---
description: Analyze recent commits for patterns and lessons, promote to durable docs
---


<!-- Extension: agentic -->
<!-- Config: .specify/extensions/agentic/ -->
# Extract Lessons

Analyze recent commits to surface patterns, implicit decisions, debugging insights, and lessons learned. Recommend promotion to durable documentation.

## User Input

$ARGUMENTS

## Purpose

Valuable knowledge is created during implementation but often stays buried in commit messages and code comments. This command extracts that knowledge and recommends where to promote it so it persists across sessions.

## Steps

### Step 1: Identify the commit range

If `$ARGUMENTS` specifies a range, use that. Otherwise, use the commits on the current branch since it diverged from main:

```bash
git log main..HEAD --oneline
```

If no branch divergence, use the last 20 commits.

### Step 2: Analyze commits

For each commit, examine:

- The commit message (especially any "why" explanations)
- The diff (look for patterns, not just changes)
- Comments added in the code

Look for these categories:

**Recurring patterns** Solutions that were applied multiple times. These may warrant a guide or convention in AGENTS.md.

**Implicit decisions** Choices that were made without being explicitly recorded. These may need ADRs.

**Debugging insights** Problems that were hard to diagnose. The diagnosis approach may help future developers.

**Convention emergence** Consistent approaches that suggest an unwritten convention. These may belong in AGENTS.md or a guide.

### Step 3: Skip noise

Do NOT report:

- Routine bug fixes with obvious causes
- Generated code changes (lockfiles, auto-formatting)
- Merge commits
- Version bumps

### Step 4: Report findings

For each finding:

```text
### [Category]: [Brief title]

**Evidence**: [commit SHAs or file references]
**Insight**: [What was learned]
**Promote to**: [suggested destination]
  - `docs/guides/` — if it's a reusable how-to
  - `docs/decisions/` — if it's an implicit decision worth recording
  - `AGENTS.md` or `src/AGENTS.md` — if it's a convention
  - `docs/design/` — if it reveals architectural understanding
  - Skip — if it's interesting but not worth promoting
```

### Step 5: Act on promotions (if requested)

If the user confirms, create the suggested artifacts:

- Draft guide files in `docs/guides/` following the format in `docs/guides/README.md`
- Draft ADRs via `/speckit.agentic.document-decisions`
- Draft design docs in `docs/design/` following the format in `docs/design/README.md`
- Propose additions to AGENTS.md files

## Notes

- This command works best after a feature is complete but before the branch is merged
- It complements `/speckit.agentic.close-plan` — run this first to catch implicit knowledge
- Not every finding needs promotion. The goal is surfacing, not bureaucracy.