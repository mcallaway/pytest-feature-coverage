#!/usr/bin/env bash
#MISE description="Verify dev environment is ready."

source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
require_supported_os

set -o pipefail
set -o nounset
set -o errexit

errors=0

for tool in git python uv pre-commit gitleaks mdformat markdownlint-cli2; do
    if command -v "$tool" > /dev/null 2>&1; then
        echo "✓ $tool: $(command -v "$tool")"
    else
        echo "✗ $tool: not found"
        errors=1
    fi
done

if [[ ! -f pyproject.toml ]]; then
    echo "✗ pyproject.toml not found"
    errors=1
else
    echo "✓ pyproject.toml"
fi

if [[ ! -d .venv ]]; then
    echo "✗ .venv not found (run 'mise run dev:setup')"
    errors=1
else
    echo "✓ .venv"
fi

if [[ -f .git/hooks/pre-commit ]] && grep -q 'pre-commit' .git/hooks/pre-commit 2>/dev/null; then
    echo "✓ pre-commit hooks installed"
else
    echo "✗ pre-commit hooks not installed (run 'pre-commit install')"
    errors=1
fi

if [[ "$errors" -ne 0 ]]; then
    echo ""
    echo "Environment check failed."
    exit 1
fi

echo ""
echo "Environment is ready."
