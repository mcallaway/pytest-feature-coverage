#!/usr/bin/env bash
#MISE description="Format markdown files in place with mdformat."

source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
require_supported_os

set -o pipefail
set -o nounset
set -o errexit

cd "$(git rev-parse --show-toplevel)"

# CHANGELOG.md is excluded: release-please regenerates it and its output
# is not guaranteed to be mdformat-compliant.
# .github/ is excluded: spec-kit auto-generates agent and prompt files there.
# .specify/ is excluded: vendor files overwritten on updates, not ours to fix.
git ls-files -z '*.md' ':!CHANGELOG.md' ':!.github/**' ':!.specify/**' | xargs -0 mdformat
