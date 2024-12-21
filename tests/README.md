# Notion2GoogleTasks Tests

## Overview

This directory contains tests for the Notion2GoogleTasks project. The tests are divided into two main categories:

1. **Unit Tests**: These tests mock the responses from the Notion API and test the functionality of the `NotionClient` class methods.
2. **Integration Tests**: These tests interact with the actual Notion API and require valid API keys and database IDs.

## Warning

**WARNING**: The integration tests are designed to work with a specific Notion database structure. If you want to use these tests with your own Notion database, you will need to adapt the tests to match your database properties. The tests assume the following properties exist in your Notion database:

- `Tags` (multi_select)
- `Importance` (select)
- `ID` (unique_id)
- `Due Date` (date)
- `Name` (title)
- `Text` (rich_text)
- `URL` (rich_text with link)
- `Parent item` (relation)
- `Today` (checkbox)
- `Status` (status)

## Unit Tests

The unit tests are located in `test_notion_client.py` and include the following:

- `test_get_filtered_sorted_database`: Tests the `get_filtered_sorted_database` method.
- `test_fetch_parent_page_names`: Tests the `fetch_parent_page_names` method.
- `test_mark_page_as_completed`: Tests the `mark_page_as_completed` method.
- `test_parse_notion_response`: Tests the `parse_notion_response` method.

## Integration Tests

The integration tests are located in `test_notion_client_integration.py` and include the following:

- `test_create_new_page_integration`: Tests creating a new page in the Notion database.
- `test_mark_page_as_completed_integration`: Tests marking a page as completed.
- `test_fetch_parent_page_names_integration`: Tests fetching parent page names.
- `test_get_filtered_sorted_database_integration`: Tests fetching filtered and sorted database entries.

## Running the Tests

To run the unit tests, use the following command:
```sh
pytest test_notion_client.py
```

To run the integration tests, ensure you have the necessary environment variables set (NOTION_API, DATABASE_ID, PROJECT_ROOT) and use the following command:

```sh
pytest test_notion_client_integration.py
```

## Environment Variables
The integration tests require the following environment variables:

- NOTION_API: Your Notion API key.
- DATABASE_ID: The ID of your Notion database.
- PROJECT_ROOT: The root directory of your project.

**Make sure these variables are set before running the integration tests**

## Adapting the Tests
If you need to adapt the tests for your own Notion database, you will need to modify the property names and structures in the test files to match your database. Pay special attention to the properties used in the mock responses and assertions.
