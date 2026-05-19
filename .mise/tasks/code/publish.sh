#!/usr/bin/env bash
#MISE description="Publish this code to Artifactory."
#MISE depends=["code:build"]

source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
require_supported_os

set -o pipefail
set -o nounset
set -o errexit

cd "$(git rev-parse --show-toplevel)"

ARTIFACTORY_HOST="artifactory.bayer.com"
ARTIFACTORY_REPO="shared-python-prod-shared"

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

# Check that a git tag exists for this version.
if ! git tag -l "$VERSION" | grep -q .; then
    echo "Error: No git tag found for version $VERSION"
    echo "Available tags:"
    git tag -l | tail -5
    exit 1
fi

# Verify dist files exist for this version.
if ! ls dist/*-"${VERSION}"-py3-none-any.whl >/dev/null 2>&1; then
    echo "Error: Expected wheel file not found: dist/*-${VERSION}-py3-none-any.whl"
    echo "Run 'mise run code:build' first."
    exit 1
fi

echo "Publishing version $VERSION (tag verified, artifacts present)..."

# Verify Artifactory is configured in pyproject.toml.
if ! grep -q '\[\[tool\.uv\.index\]\]' pyproject.toml; then
    echo "Error: [[tool.uv.index]] section not found in pyproject.toml"
    exit 1
fi
if ! grep -q "name = \"${ARTIFACTORY_REPO}\"" pyproject.toml; then
    echo "Error: name = \"${ARTIFACTORY_REPO}\" not found in pyproject.toml"
    exit 1
fi

# Ensure ~/.netrc has credentials for Artifactory.
if ! grep -q "machine ${ARTIFACTORY_HOST}" ~/.netrc 2>/dev/null; then
    echo "Error: ~/.netrc does not have a machine stanza for ${ARTIFACTORY_HOST}"
    echo "See: https://docs.int.bayer.com/pbt-dsi/computing_environment_and_app_development/artifactory/artifactory/#storing-your-artifactory-token-in-netrc"
    exit 1
fi

# uv publish reads credentials from ~/.netrc automatically.
uv publish --index ${ARTIFACTORY_REPO}
