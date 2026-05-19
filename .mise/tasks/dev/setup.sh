#!/usr/bin/env bash
#MISE description="Install all dev dependencies."

source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
require_supported_os

set -o pipefail
set -o nounset
set -o errexit

SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"

# Ensure mise is installed and shell integration is active.
source "${SCRIPT_DIR}/install-mise.sh"

# Install tools defined in mise.toml (Python, uv, pre-commit, gitleaks, markdownlint-cli2, mdformat, etc.)
mise install

# Install project dependencies into .venv
uv sync

# Install pre-commit git hooks
pre-commit install

echo ""
echo "Setup complete. Run 'mise run dev:check' to verify."
