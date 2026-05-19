#!/usr/bin/env bash
#MISE description="Build artifacts from the python package in this repo."

source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
require_supported_os

set -o pipefail
set -o nounset
set -o errexit

cd "$(git rev-parse --show-toplevel)"

ARTIFACTORY_HOST="artifactory.bayer.com"

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

# Check that a git tag exists for this version (strict tag-only check).
if ! git tag -l "$VERSION" | grep -q .; then
    echo "Error: No git tag found for version $VERSION"
    echo "Please create a release for version $VERSION before building."
    echo "Available tags:"
    git tag -l | tail -5
    exit 1
fi

echo "Building version $VERSION (tag verified)..."

# Verify ~/.netrc is set up for Artifactory before investing time in a build.
if [ ! -f ~/.netrc ]; then
    echo "Error: ~/.netrc not found."
    echo "See: https://docs.int.bayer.com/pbt-dsi/computing_environment_and_app_development/artifactory/artifactory/#storing-your-artifactory-token-in-netrc"
    exit 1
fi
if ! grep -q "machine ${ARTIFACTORY_HOST}" ~/.netrc; then
    echo "Error: ~/.netrc has no entry for ${ARTIFACTORY_HOST}"
    echo "See: https://docs.int.bayer.com/pbt-dsi/computing_environment_and_app_development/artifactory/artifactory/#storing-your-artifactory-token-in-netrc"
    exit 1
fi

# Clean existing dist directory to ensure fresh build.
if [ -d dist ]; then
    echo "Cleaning existing dist/ directory..."
    rm -rf dist/*
fi

uv build
