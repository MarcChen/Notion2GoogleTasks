# Notion2GoogleTasks

## Overview

**Notion2GoogleTasks** is a synchronization tool that bridges your Notion database and Google Tasks. With this tool, you can seamlessly sync tasks from your Notion database to Google Tasks, ensuring you stay on top of your to-do lists.

### Current Features (v1.0.0)
- **One-Way Sync**: Sync tasks from Notion to Google Tasks.
  - Tasks are retrieved from a specified Notion database based on a [filter](./services/notion/config/query_payload.json).
  - If a task already exists in Google Tasks, it is not duplicated.
  - New tasks are added to a task list named after the tag of the corresponding Notion page.

### Upcoming in v2.0
- **Two-Way Sync**:
  - New tasks created in Google Tasks will be uploaded to the specified Notion database.
  - Task status changes (e.g., marking as done) will be reflected in both Notion and Google Tasks.

## Main Features
1. **Efficient Syncing**:
   - Avoids duplication by checking existing tasks.
   - Tags on Notion pages are used to group tasks into corresponding Google Task lists.
2. **Customizable**:
   - Filters allow you to specify which Notion tasks should be synced.

## Missing Features
- Real-time updates are not currently supported; sync is manual or scheduled via cron jobs or workflows.
- Due to limitations of the Google Tasks API, only due dates can be applied to tasks, not specific times.


## Installation and Usage
For detailed steps, refer to the [Quickstart Guide](./Quickstart.md).

### Requirements
- **Notion**:
    - Notion database ID
    - Query [filter](./services/notion/config/query_payload.json)
    - API KEY 
- **Google API**:
    - OAuth2 client configuration
    - Access token retrieval


## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
