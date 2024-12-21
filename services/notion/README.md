# Notion Client Integration

This service provides a Python client for interacting with a Notion database via the Notion API. It enables filtered and controlled access to database content, helping manage tasks or items without syncing the entire database.

## Configuration

### `.env` File

To configure the service, create a `.env` file in the root project. For this service the file should include at least :

```
NOTION_API_KEY=<your-notion-api-key>
DATABASE_ID=<your-database-id>
```

- **`NOTION_API_KEY`**: The API key from your Notion Integration.
- **`DATABASE_ID`**: The ID of the Notion database you want to interact with.

### Query Filter (`query_payload.json`)

To control which data is fetched, use a `query_payload.json` file located at `services/notion/config/query_payload.json`. This file defines the filter and sorting rules for querying the database. Example:

```json
{
    "filter": {
        "and": [
            {
                "property": "Status",
                "select": {
                    "equals": "In Progress"
                }
            },
            {
                "property": "Due Date",
                "date": {
                    "on_or_after": "2024-01-01"
                }
            }
        ]
    },
    "sorts": [
        {
            "property": "Due Date",
            "direction": "ascending"
        }
    ]
}
```

This configuration ensures only relevant data is fetched, avoiding the need to sync the entire database.

## What This Service Does

The `NotionClient` class provides the following functionality:

1. **Filtered Database Queries**: Fetch and filter database content using the query rules defined in `query_payload.json`.
2. **Parent Page Information**: Retrieve and map parent page names to their respective page IDs.
3. **Update Status**: Mark a Notion page as "Done" by updating its `Status` property.
4. **Create New Pages**: Add new pages to the database with specific default properties (e.g., a checkbox marked "Today").
5. **Parse Responses**: Extract relevant fields from Notion API responses into a clean, structured format for easier use.

By using this service, you can streamline interaction with a Notion database while focusing only on the data you need.

