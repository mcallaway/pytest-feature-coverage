#!/usr/bin/env bash
#MISE description="Install mise if missing; check version and shell activation."

source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
require_supported_os

install_mise() {
    # Use the official installer (not brew) so `mise self-update` works later.
    /bin/bash -c "$(curl -fsSL https://mise.run)"
}

check_mise_shell() {
    local USER_SHELL
    USER_SHELL=$(basename "$SHELL")
    echo "Checking mise activation in $USER_SHELL..."
    if command "$USER_SHELL" -i -c 'type mise 2>/dev/null | grep -q "mise is a.*function"'; then
        echo "✓ Mise shell integration is active."
    else
        echo "✗ Mise shell integration is NOT active."
        echo "  Add to ~/.${USER_SHELL}rc:"
        echo "    eval \"\$(mise activate $USER_SHELL)\""
        echo "  See https://mise.jdx.dev/getting-started.html#activate-mise"
    fi
}

if command -v mise >/dev/null 2>&1; then
    echo "✓ Mise is already installed: $(mise --version)"
else
    echo "Installing mise..."
    install_mise
    echo "Note: mise installation may require a shell restart."
fi

check_mise_shell
