#!/bin/bash

# Retrieve last successful GitHub Actions workflow run time

# Default values
OWNER="MarcChen"
REPO="Notion2GoogleTasks"
WORKFLOW_FILE="sync_notion_to_google.yml"

# Allow overriding defaults through command line arguments
if [ $# -ge 1 ]; then
    WORKFLOW_FILE="$1"
fi
if [ $# -ge 2 ]; then
    OWNER="$2"
fi
if [ $# -ge 3 ]; then
    REPO="$3"
fi

# Check if GITHUB_TOKEN is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is not set" >&2
    echo "Please export your GitHub token: export GITHUB_TOKEN=your_token_here" >&2
    exit 1
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed. Please install it to parse JSON responses." >&2
    exit 1
fi

# Fetch last successful run details
last_successful_run=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$OWNER/$REPO/actions/workflows/$WORKFLOW_FILE/runs?status=success&per_page=1")

# Extract created_at timestamp
created_at=$(echo "$last_successful_run" | jq -r '.workflow_runs[0].created_at')

# Set default if no previous successful run
if [[ "$created_at" == "null" || -z "$created_at" ]]; then
    created_at="2020-01-01T00:00:00Z"
fi

# Output the timestamp
echo "$created_at"