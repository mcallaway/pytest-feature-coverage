#!/usr/bin/env bash
#MISE description="Run all tests, linting, and type checking."

source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
require_supported_os

set -o pipefail
set -o nounset
set -o errexit

mise run test:lint
mise run test:typecheck
mise run test:unit
mise run test:acceptance
mise run test:secrets
