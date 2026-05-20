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

# Fetch tags and verify a git tag exists for this version.
git fetch --tags --quiet
if ! git tag -l "$VERSION" | grep -q .; then
    echo "Error: No git tag found for version $VERSION"
    echo "A GitHub release must exist before publishing."
    echo "Available tags:"
    git tag -l | tail -5
    exit 1
fi

# Verify build artifacts exist.
if ! ls dist/*.tar.gz >/dev/null 2>&1 || ! ls dist/*.whl >/dev/null 2>&1; then
    echo "Error: Expected sdist (.tar.gz) and wheel (.whl) not found in dist/"
    echo "Run 'mise code:build' first."
    exit 1
fi

# Extract credentials from ~/.netrc for Artifactory.
# xref: https://docs.int.bayer.com/pbt-dsi/computing_environment_and_app_development/artifactory/artifactory/#storing-your-artifactory-token-in-netrc
LOGIN=$(awk "/machine ${ARTIFACTORY_HOST}/{found=1} found && /login/{print \$2; exit}" ~/.netrc 2>/dev/null)
PASSWORD=$(awk "/machine ${ARTIFACTORY_HOST}/{found=1} found && /password/{print \$2; exit}" ~/.netrc 2>/dev/null)
if [[ -z "${LOGIN}" || -z "${PASSWORD}" ]]; then
    echo "Error: ~/.netrc does not have login and password for ${ARTIFACTORY_HOST}"
    echo "See: https://docs.int.bayer.com/pbt-dsi/computing_environment_and_app_development/artifactory/artifactory/#storing-your-artifactory-token-in-netrc"
    exit 1
fi

# Verify Artifactory is configured in pyproject.toml.
if ! grep -q '\[\[tool\.uv\.index\]\]' pyproject.toml; then
    echo "Error: [[tool.uv.index]] section not found in pyproject.toml"
    exit 1
fi
if ! grep -q "name = \"${ARTIFACTORY_REPO}\"" pyproject.toml; then
    echo "Error: name = \"${ARTIFACTORY_REPO}\" not found in pyproject.toml"
    exit 1
fi

echo "Publishing version $VERSION..."

uv publish --index "${ARTIFACTORY_REPO}" --username "${LOGIN}" --password "${PASSWORD}"
