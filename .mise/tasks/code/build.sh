#!/usr/bin/env bash
#MISE description="Build artifacts from the python package in this repo."

source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
require_supported_os

set -o pipefail
set -o nounset
set -o errexit

cd "$(git rev-parse --show-toplevel)"

# Read version from pyproject.toml [project] section.
VERSION=$(python3 -c "
import tomllib, pathlib
data = tomllib.loads(pathlib.Path('pyproject.toml').read_text())
print(data['project']['version'])
")
if [[ -z "${VERSION}" ]]; then
    echo "Error: Cannot determine version from pyproject.toml."
    exit 1
fi

echo "Building version $VERSION..."

# Clean existing dist directory to ensure fresh build.
rm -rf dist

uv build

echo "Built: $(ls dist/)"
