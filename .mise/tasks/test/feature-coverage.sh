#!/usr/bin/env bash
#MISE description="Run pytest feature coverage report."

source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
require_supported_os

set -o pipefail
set -o nounset
set -o errexit

cd "$(git rev-parse --show-toplevel)"

uv run pytest --feature-coverage "$@"
