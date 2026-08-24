#!/usr/bin/env bash
#MISE description="Run integration tests (pytester-based end-to-end plugin tests)."

source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
require_supported_os

set -o pipefail
set -o nounset
set -o errexit

# Default capture keeps nested pytester session output off the console
# (those runs intentionally print FAILED coverage lines). Pass -s to debug.
uv run pytest -v tests/integration/
