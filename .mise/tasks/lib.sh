# Shared helpers for mise tasks.
# Source this file; do not execute directly.
#MISE hide=true

require_supported_os() {
    case "$OSTYPE" in
        darwin*|linux-gnu*)
            # macOS or Linux (including WSL2) -- supported.
            ;;
        msys*|cygwin*|win32*)
            echo "Native Windows is not supported."
            echo ""
            echo "  This project requires a Unix-like environment."
            echo "  Use WSL2: https://learn.microsoft.com/en-us/windows/wsl/install"
            echo ""
            exit 1
            ;;
        *)
            echo "Unknown OS: $OSTYPE -- proceeding, but things may break."
            ;;
    esac
}
