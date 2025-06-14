#!/bin/bash

# Export environment variables from .env file and retrieve last successful sync time

# Script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"
RETRIEVE_SCRIPT="$SCRIPT_DIR/retrieve_last_sucessfull_run.sh"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found at $ENV_FILE" >&2
    exit 1
fi

# Check if retrieve_last_sucessfull_run.sh exists
if [ ! -f "$RETRIEVE_SCRIPT" ]; then
    echo "Error: retrieve_last_sucessfull_run.sh not found at $RETRIEVE_SCRIPT" >&2
    exit 1
fi

# Function to export variables from .env file
export_env_vars() {
    echo "# Exporting environment variables from .env file..."
    
    # Read .env file and export variables (skip comments and empty lines)
    while IFS= read -r line || [ -n "$line" ]; do
        # Skip comments and empty lines
        if [[ "$line" =~ ^[[:space:]]*# ]] || [[ -z "${line// }" ]]; then
            continue
        fi
        
        # Extract variable name and value
        if [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*=[[:space:]]*(.*)$ ]]; then
            var_name="${BASH_REMATCH[1]}"
            var_value="${BASH_REMATCH[2]}"
            
            # Remove surrounding quotes if present
            if [[ "$var_value" =~ ^[\"\'](.*)[\"\']$ ]]; then
                var_value="${BASH_REMATCH[1]}"
            fi
            
            # Export the variable
            export "$var_name=$var_value"
            echo "Exported: $var_name"
        fi
    done < "$ENV_FILE"
}

# Function to get last successful sync time
get_last_sync() {
    echo "# Retrieving last successful sync time..."
    
    # Make the retrieve script executable if it isn't already
    chmod +x "$RETRIEVE_SCRIPT"
    
    # Get the last successful run time
    LAST_SUCCESSFUL_SYNC=$("$RETRIEVE_SCRIPT")
    
    if [ $? -eq 0 ]; then
        export LAST_SUCCESSFUL_SYNC="$LAST_SUCCESSFUL_SYNC"
        echo "Exported: LAST_SUCCESSFUL_SYNC=$LAST_SUCCESSFUL_SYNC"
    else
        echo "Warning: Failed to retrieve last successful sync time" >&2
        export LAST_SUCCESSFUL_SYNC="2020-01-01T00:00:00Z"
        echo "Using default: LAST_SUCCESSFUL_SYNC=$LAST_SUCCESSFUL_SYNC"
    fi
}

# Main execution
main() {
    echo "========================================="
    echo "Environment Setup Script"
    echo "========================================="
    
    # Export environment variables from .env
    export_env_vars
    echo ""
    
    # Get and export last successful sync time
    get_last_sync
    echo ""
    
    echo "========================================="
    echo "All environment variables have been exported!"
    echo "========================================="
    
    # Optional: Show all exported variables
    if [[ "$1" == "--show-vars" ]] || [[ "$1" == "-v" ]]; then
        echo ""
        echo "Current environment variables:"
        echo "------------------------------"
        env | grep -E "^(PROJECT_ROOT|TOKEN_PATH|GOOGLE_|NOTION_|DATABASE_ID|FREE_MOBILE_|LAST_SUCCESSFUL_SYNC)=" | sort
    fi
}

# Show usage information
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "This script exports all environment variables from .env file and retrieves"
    echo "the last successful GitHub Actions workflow run time."
    echo ""
    echo "Options:"
    echo "  -v, --show-vars    Show all exported variables after setup"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Environment variables that will be exported:"
    echo "  - All variables from .env file"
    echo "  - LAST_SUCCESSFUL_SYNC (from GitHub Actions API)"
    echo ""
    echo "Note: Requires GITHUB_TOKEN to be set for retrieving last sync time."
}

# Handle command line arguments
case "$1" in
    -h|--help)
        usage
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
