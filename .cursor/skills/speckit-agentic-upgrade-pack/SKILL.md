---
name: speckit-agentic-upgrade-pack
description: Automate upgrading the agentic extension and preset so every installed integration reaches the new version
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: bayer-int
  source: agentic:commands/upgrade-pack.md
---

# Upgrade Pack

Upgrade this pack's extension and preset to the latest (or a specified) release, across every integration installed in this repository, without the manual, order-sensitive ceremony that upgrading by hand currently requires. Reports real drift before making any change, and never commits on your behalf.

## User Input

$ARGUMENTS

An optional target version (e.g. `0.5.0`). Defaults to this pack's latest published GitHub release.

## Purpose

Upgrading this pack's extension and preset by hand in a consumer repo has four sharp edges, discovered the hard way during a real manual upgrade:

1. `specify extension update`/`specify preset` silently no-op for `--from`-installed packages and report a misleading "up to date," instead of the real version drift.
1. The extension and preset can silently drift out of lockstep, with nothing cross-checking them.
1. `specify extension add --force` only materializes skill files for the currently active integration -- so upgrading a second, then third, integration leaves them on the old version unless each is explicitly brought up to date afterward. (Plain `specify integration use <integration>` cycling, not a backup/restore dance, is what actually brings them up to date -- see Step 5 and ADR-012.)
1. Copilot's commands-to-skills layout migration must run before the preset is touched, or the preset step can be rejected outright.

This command automates the correct sequence so none of these four sharp edges have to be rediscovered or manually worked around every time this pack is upgraded.

## Steps

### Step 1: Pre-flight report

Gather the real current state before changing anything:

```bash
specify extension info agentic
specify preset info agentic
specify integration list
specify integration status
git status --short
```

Resolve the target version: if the user supplied one in `$ARGUMENTS`, use it; otherwise resolve this pack's latest published GitHub release (`gh release view --repo bayer-int/speckit-agentic-workflow --json tagName` or the equivalent API call).

Report, before doing anything else:

- Current extension version and current preset version (do not trust `specify extension update`'s "up to date" message -- it is a silent no-op for `--from`-installed packages, not a real drift check; read the versions directly from `info` instead).
- The resolved target version.
- Every installed integration (from `specify integration list`/`specify integration status`).
- Whether Copilot is on the commands layout or the skills layout.
- The git status output above.

**Stop and ask for confirmation** if the working tree has uncommitted changes unrelated to this upgrade, rather than proceeding into a multi-step sequence against a dirty tree.

**Treat "no version drift, no pending layout migration, and every installed integration already materialized at that version" as a true no-op.** If the extension and preset versions already match the resolved target, Copilot is already on the skills layout, and every installed integration's copy of this command's own skill file is byte-identical (e.g. `shasum .github/skills/speckit-agentic-upgrade-pack/SKILL.md .claude/skills/speckit-agentic-upgrade-pack/SKILL.md .cursor/skills/speckit-agentic-upgrade-pack/SKILL.md`, for whichever are installed, and the hashes all match), report exactly that and stop here. Do not proceed to Step 2. This is the behavior the misleading `specify extension update` message should have given you, and does not.

A byte-identical-content check, not merely a skill-directory count, matters because the extension's own reported version is a single, repo-wide value -- it does not, by itself, confirm every installed integration's skill tree was actually cycled onto it, and a directory count alone would not catch a release that changed a command's content without changing the total number of commands. Comparing this command's own file specifically works because every run of this skill regenerates it for every integration it touches, so a hash mismatch is a direct, reliable signal that an integration was left on stale content. This makes the no-op check safe to rely on even if a previous run of this command was interrupted after Step 5 upgraded the default integration but before it finished cycling the rest: a version-only or count-only check would see "no drift" and stop, silently leaving those other integrations stranded on the old skill set.

Otherwise, continue to Step 2.

### Step 2: Fetch release assets once

Fetch the target extension and preset release zips a single time, to a local temp directory, and reuse those local paths for every install step below instead of re-fetching per integration:

```bash
tmpdir="$(mktemp -d)"
gh release download "${target_version}" \
  --repo bayer-int/speckit-agentic-workflow \
  --pattern "agentic-workflow.zip" --pattern "agentic-preset.zip" \
  --dir "${tmpdir}"
```

(`specify extension add --from`/`specify preset add --from` also work directly against this repo's own `github.com/.../releases/download/...` URLs even though it is private -- the bug that previously broke that path is fixed upstream, see Notes below. Fetching once to a local path here is about avoiding redundant network round-trips across every integration in Step 4, not working around a bug that no longer exists.)

### Step 3: Layout migration, before the preset is touched

If Copilot is still on the commands layout (per Step 1's report), migrate it now, before Step 4 touches the preset:

```bash
specify integration upgrade copilot --integration-options="--skills" --force
```

If Copilot is already on the skills layout, skip this step entirely.

**This must happen before Step 4.** Running the preset upgrade first risks the documented rejection ("a layout change... while presets are registered can be rejected"), forcing a backtrack.

### Step 4: Upgrade the preset

```bash
echo "y" | specify preset remove agentic
specify preset add agentic --from "${tmpdir}/agentic-preset.zip"
```

### Step 5: Upgrade the extension for the default integration, then cycle the rest onto it

Follow this exact sequence -- it is a single pass, not a backup/restore loop (see ADR-012 for why a fixed-point backup/restore approach was considered and rejected after testing showed it was unnecessary and riskier than this).

1. Record the originally-active default integration (from Step 1's `specify integration status`).

1. Upgrade the extension once, for the currently-active default integration only:

   ```bash
   echo "y" | specify extension remove agentic
   specify extension add agentic --force --from "${tmpdir}/agentic-workflow.zip"
   ```

1. For every *other* installed integration (in the order `specify integration status` reports them): `specify integration use <integration>`. Nothing else -- no `extension remove`, no re-running `extension add`, no file backup or restore. This alone regenerates that integration's `speckit-agentic-*` skill tree from the version just installed in step 2, without touching any other integration's tree.

1. After every installed integration has been processed once, restore the originally-active default integration: `specify integration use <original default>`.

If only one integration is installed, step 3 has nothing to do: there are no other integrations to cycle through.

### Step 6: Verify and report

Confirm, and report:

- Both `specify extension info agentic` and `specify preset info agentic` now report the target version.
- No leftover legacy `.github/agents`/`.github/prompts` command stubs remain.
- No `speckit-agentic-*` skill files are symlinks (materialize any that are, per the maintainer guide's documented procedure).
- Every installed integration's `speckit-agentic-full-workflow/SKILL.md` exists and is a regular file.
- `specify integration status` reports `OK`, or the expected `unsafe-multi-install: copilot` when Copilot is intentionally kept installed alongside other, multi-install-safe integrations.

**Flag downstream markdown-lint ignore gaps.** If this run newly introduced a `.claude/skills/**` or `.cursor/skills/**` tree (i.e. that integration was not previously installed), check whether this repo's own markdown-lint ignore configuration (`.markdownlint-cli2.jsonc` or equivalent) already excludes it. If it does not, name the gap explicitly and suggest the specific ignore-list addition needed, rather than leaving the next `mise run lint:markdown`/pre-commit run to fail on freshly generated vendor content with no explanation.

**Clean up the temp directory.** Remove `${tmpdir}` from Step 2 (`rm -rf "${tmpdir}"`) now that every install step that needed it is done, whether this run succeeded or stopped early on a failed step -- don't leave fetched release zips accumulating in temp storage across repeated runs.

**Do not commit anything.** Report a summary of what changed and stop here. Committing these changes is left to the operator (e.g. via `/speckit.agentic.document-decisions` first if the upgrade surfaced anything non-obvious, then a normal commit).

## Notes

- This command upgrades this pack itself in a *consumer* repo. It is unrelated to `/speckit.agentic.full-workflow`, which runs a feature/bugfix lifecycle within a repo that already has this pack installed.
- The private-repo release-asset install bug that previously forced a `gh release download` + local-file-install workaround for `--from` URLs is fixed upstream (confirmed in `github/spec-kit`'s default branch): `--from` now resolves a browser-style `github.com/OWNER/REPO/releases/download/...` URL to its GitHub API asset URL and attaches the `Accept: application/octet-stream` header automatically, even for private repositories. This command's own maintainer repository keeps a standalone, CI-wired regression check for this exact behavior (`.mise/tasks/check/private-repo-release-install.sh`) precisely so a future upstream regression is caught automatically rather than rediscovered manually the next time this command is run.
- The Step 5 cycling approach works around a `specify-cli` limitation (single-target skill materialization on `extension add --force`) outside this pack's control. See ADR-012 for the full rationale, including why a backup/restore loop was initially assumed necessary, tested, and found both unnecessary and the actual cause of a separate registry-corruption problem.
- This command does not make `specify extension update`/`specify preset` itself report accurate drift for `--from`-installed packages; Step 1 works around that limitation by reading `info` output directly instead of trusting `update`'s own no-op message.