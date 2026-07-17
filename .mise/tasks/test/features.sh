#!/usr/bin/env bash
#MISE description="Run pytest feature coverage report."

source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
require_supported_os

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

if [[ ! -d "tests" ]]; then
    echo "No tests directory found, skipping feature coverage."
    exit 0
fi

# Examples:
#   mise run test:features
#   mise run test:features -- --feature-coverage-min=80
#   mise run test:features -- -k "auth"
uv run pytest --feature-coverage -q tests/ "$@"
