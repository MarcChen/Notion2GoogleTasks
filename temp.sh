#!/bin/bash

# Replace these variables with your repository details
OWNER="MarcChen"
REPO="Notion2GoogleTasks"
WORKFLOW_FILE="sync_notion_to_google.yml"
# $GITHUB_TOKEN

# Get the last successful workflow run details using curl
last_successful_run=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/workflows/$WORKFLOW_FILE/runs?status=success&per_page=1")

# Parse and print the last successful run details
echo "Last successful run details:"
echo "$last_successful_run" | jq '.workflow_runs[0] | {id, name, run_number, event, status, conclusion, html_url, created_at, updated_at}'