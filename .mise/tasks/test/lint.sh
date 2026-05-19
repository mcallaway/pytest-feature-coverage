#!/usr/bin/env bash
#MISE description="Run all linters (ruff + markdown)."

source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
require_supported_os

set -o pipefail
set -o nounset
set -o errexit

cd "$(git rev-parse --show-toplevel)"

echo "Running ruff check..."
uv run ruff check src tests

echo "Running ruff format check..."
uv run ruff format --check src tests

# Delegate markdown linting to its own task.
mise run test:lint-markdown
