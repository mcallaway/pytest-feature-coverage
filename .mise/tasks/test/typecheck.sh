#!/usr/bin/env bash
#MISE description="Run type checker (ty)."

source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
require_supported_os

set -o pipefail
set -o nounset
set -o errexit

uv run ty check src
