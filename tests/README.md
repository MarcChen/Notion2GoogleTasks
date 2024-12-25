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

The unit tests are located in the following files:

- `test_notion_client.py`: Tests the `NotionClient` class methods.
  - `test_get_filtered_sorted_database`: Tests the `get_filtered_sorted_database` method.
  - `test_fetch_parent_page_names`: Tests the `fetch_parent_page_names` method.
  - `test_mark_page_as_completed`: Tests the `mark_page_as_completed` method.
  - `test_parse_notion_response`: Tests the `parse_notion_response` method.

- `test_google_tasks_manager.py`: Tests the `GoogleTasksManager` class methods.
  - `test_list_task_lists`: Tests the `list_task_lists` method.
  - `test_create_task_list`: Tests the `create_task_list` method.
  - `test_list_tasks_in_tasklist`: Tests the `list_tasks_in_tasklist` method.
  - `test_create_task`: Tests the `create_task` method.
  - `test_create_subtask`: Tests the `create_subtask` method.

- `test_alert_sms_free.py`: Tests the `SMSAPI` class methods.
  - `test_send_sms_success`: Tests the `send_sms` method for successful SMS sending.
  - `test_send_sms_error_400`: Tests the `send_sms` method for handling HTTP 400 errors.

- `test_notion_to_google_syncer.py`: Tests the `NotionToGoogleTaskSyncer` class methods.
  - `test_build_task_description`: Tests the `build_task_description` method.
  - `test_compute_due_date`: Tests the `compute_due_date` method.
  - `test_task_exists`: Tests the `task_exists` method.
  - `test_ensure_tasklist_exists`: Tests the `ensure_tasklist_exists` method.

## Integration Tests

The integration tests are located in the following files:

- `test_notion_client_integration.py`: Tests the `NotionClient` class methods with real API interactions.
  - `test_create_new_page_integration`: Tests creating a new page in the Notion database.
  - `test_mark_page_as_completed_integration`: Tests marking a page as completed.
  - `test_fetch_parent_page_names_integration`: Tests fetching parent page names.
  - `test_get_filtered_sorted_database_integration`: Tests fetching filtered and sorted database entries.

- `test_google_tasks_manager_integration.py`: Tests the `GoogleTasksManager` class methods with real API interactions.
  - `test_list_task_lists`: Tests listing all task lists.
  - `test_create_task`: Tests creating a new task.
  - `test_create_subtask`: Tests creating a subtask.
  - `test_list_tasks_in_tasklist`: Tests listing tasks in a specific task list.
  - `test_get_task_details`: Tests retrieving details of a specific task.
  - `test_mark_task_completed`: Tests marking a task as completed.
  - `test_delete_task`: Tests deleting a task.

- `test_alert_sms_integration.py`: Tests the `SMSAPI` class methods with real API interactions.
  - `test_send_sms_real`: Tests sending an SMS with real credentials.

- `test_notion_to_google_syncer_integration.py`: Tests the `NotionToGoogleTaskSyncer` class methods with real API interactions.
  - `test_real_integration_sync_pages_to_google_tasks`: Tests syncing pages from Notion to Google Tasks.

## Running the Tests

To run the unit tests, use the following command:
```sh
pytest test_notion_client.py test_google_tasks_manager.py test_alert_sms_free.py test_notion_to_google_syncer.py