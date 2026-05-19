#!/usr/bin/env bash
#MISE description="Lint markdown files (mdformat + markdownlint-cli2)"

source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
require_supported_os

set -o pipefail
set -o nounset
set -o errexit

cd "$(git rev-parse --show-toplevel)"

# Scope to tracked .md files so ignored paths (.venv, tmp, build output) are skipped.
# CHANGELOG.md is excluded: release-please regenerates it and its output is not
# guaranteed to be mdformat-compliant.
# .github/ is excluded: spec-kit auto-generates agent and prompt files there.
# .specify/ is excluded: vendor files overwritten on updates, not ours to fix.
git ls-files -z '*.md' ':!CHANGELOG.md' ':!.github/**' ':!.specify/**' | xargs -0 mdformat --check

markdownlint-cli2 "**/*.md"
