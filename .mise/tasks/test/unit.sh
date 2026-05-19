#!/usr/bin/env bash
#MISE description="Run pytest on 'unit' tests."

source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
require_supported_os

set -o pipefail
set -o nounset
set -o errexit

uv run pytest -sv --log-cli-level=DEBUG tests/unit/
