#!/usr/bin/env bash
#MISE description="Scan for secrets with gitleaks."

source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
require_supported_os

set -o pipefail
set -o nounset
set -o errexit

cd "$(git rev-parse --show-toplevel)"

echo "Running gitleaks..."
gitleaks detect --config=.gitleaks.toml --source=. --verbose
