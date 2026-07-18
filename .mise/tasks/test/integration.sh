#!/usr/bin/env bash
#MISE description="Run integration tests (pytester-based end-to-end plugin tests)."

source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
require_supported_os

set -o pipefail
set -o nounset
set -o errexit

uv run pytest -sv --log-cli-level=DEBUG tests/integration/
