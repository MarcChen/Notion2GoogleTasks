#!/bin/bash

# Source this script to export environment variables in the current shell
# Usage: source utilis/source_env.sh
# or: . utilis/source_env.sh

# Script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"
RETRIEVE_SCRIPT="$SCRIPT_DIR/retrieve_last_sucessfull_run.sh"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found at $ENV_FILE" >&2
    return 1
fi

# Export variables from .env file
echo "Loading environment variables from .env..."
set -a  # automatically export all variables
source "$ENV_FILE"
set +a  # stop automatically exporting

# Get last successful sync time if possible
if [ -f "$RETRIEVE_SCRIPT" ] && [ -n "$GITHUB_TOKEN" ]; then
    echo "Retrieving last successful sync time..."
    chmod +x "$RETRIEVE_SCRIPT"
    LAST_SUCCESSFUL_SYNC=$("$RETRIEVE_SCRIPT" 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$LAST_SUCCESSFUL_SYNC" ]; then
        export LAST_SUCCESSFUL_SYNC
        echo "✓ LAST_SUCCESSFUL_SYNC: $LAST_SUCCESSFUL_SYNC"
    else
        export LAST_SUCCESSFUL_SYNC="2020-01-01T00:00:00Z"
        echo "⚠ Using default LAST_SUCCESSFUL_SYNC: $LAST_SUCCESSFUL_SYNC"
    fi
else
    export LAST_SUCCESSFUL_SYNC="2020-01-01T00:00:00Z"
    echo "⚠ GITHUB_TOKEN not set or retrieve script not found. Using default LAST_SUCCESSFUL_SYNC: $LAST_SUCCESSFUL_SYNC"
fi

echo "✓ Environment variables loaded successfully!"

# Optional: show loaded variables
if [[ "$1" == "-v" ]] || [[ "$1" == "--verbose" ]]; then
    echo ""
    echo "Loaded variables:"
    env | grep -E "^(PROJECT_ROOT|TOKEN_PATH|GOOGLE_|NOTION_|DATABASE_ID|FREE_MOBILE_|LAST_SUCCESSFUL_SYNC)=" | sort
fi
