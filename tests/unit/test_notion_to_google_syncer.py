from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from services.sync_notion_google_task.main import NotionToGoogleTaskSyncer


@pytest.fixture
def mock_syncer():
    with patch(
        "services.sync_notion_google_task.main.NotionClient"
    ) as MockNotionClient, patch(
        "services.sync_notion_google_task.main.GoogleTasksManager"
    ) as MockGoogleTasksManager:
        # Mock the dependencies
        mock_notion_client = MockNotionClient.return_value
        mock_google_tasks_manager = MockGoogleTasksManager.return_value

        # Return the class under test with mocked dependencies
        syncer = NotionToGoogleTaskSyncer(
            "mock_notion_api_key",
            "mock_database_id",
            "mock_project_root",
            "mock_token_path",
            "mock_sms_user",
            "mock_sms_password",
        )
        return syncer, mock_notion_client, mock_google_tasks_manager


def test_build_task_description(mock_syncer):
    syncer, _, _ = mock_syncer

    # Test case: All fields provided
    importance = "High"
    text = "Complete the report"
    urls = ["http://example.com", "http://example.org"]
    due_date = (
        datetime.utcnow() + timedelta(days=7)
    ).isoformat()  # Adjusted to a string type

    description = syncer.build_task_description(
        importance, text, urls, due_date
    )

    assert "Importance: High" in description
    assert "Details: Complete the report" in description
    assert "Links:" in description
    assert " - http://example.com" in description
    assert " - http://example.org" in description
    assert (
        f"Due Date: {datetime.fromisoformat(due_date).strftime('%d-%m-%y')}"
        in description
    )

    # Test case: Missing fields
    description = syncer.build_task_description(None, None, None, None)
    assert description == ""  # Should handle missing data gracefully

    # Test case: Empty URLs list
    description = syncer.build_task_description(
        "Medium", "Some text", [], due_date
    )
    assert "Importance: Medium" in description
    assert "Details: Some text" in description
    assert "Links:" not in description  # No links should be added

    # Test case: Very long text
    long_text = "A" * 1000  # Simulating a very long task description
    description = syncer.build_task_description(
        "Low", long_text, urls, due_date
    )
    assert long_text in description  # Ensure the full text is included


def test_compute_due_date(mock_syncer):
    syncer, _, _ = mock_syncer

    # Test case: due_date is None
    due_date = syncer.compute_due_date(None)
    assert due_date.date() == datetime.utcnow().date()

    # Test case: due_date exceeds 14 days
    future_date = (datetime.utcnow() + timedelta(days=20)).isoformat()
    adjusted_date = syncer.compute_due_date(future_date)
    assert adjusted_date.date() == datetime.utcnow().date()

    # Test case: due_date within 14 days
    valid_date = (datetime.utcnow() + timedelta(days=10)).isoformat()
    computed_date = syncer.compute_due_date(valid_date)
    assert (
        computed_date.date() == (datetime.utcnow() + timedelta(days=10)).date()
    )

    # Test case: Invalid date string
    with pytest.raises(ValueError):
        syncer.compute_due_date("invalid-date")

    # Test case: Past date
    past_date = (datetime.utcnow() - timedelta(days=5)).isoformat()
    computed_date = syncer.compute_due_date(past_date)
    assert (
        computed_date.date() == (datetime.utcnow() - timedelta(days=5)).date()
    )

    # Test case: Exact 14 days
    exact_14_days = (datetime.utcnow() + timedelta(days=14)).isoformat()
    computed_date = syncer.compute_due_date(exact_14_days)
    assert (
        computed_date.date() == (datetime.utcnow() + timedelta(days=14)).date()
    )


def test_task_exists(mock_syncer):
    syncer, _, google_tasks_manager = mock_syncer

    # Mock task list data
    google_tasks_manager.list_tasks_in_tasklist.side_effect = (
        lambda tasklist_id: (
            [
                "Task 1 | (1)",
                "Task 2 | (2)",
            ]
            if tasklist_id == "existing_tasklist_id"
            else []
        )
    )

    # Test case: Task exists
    google_task_lists = {"Work": "existing_tasklist_id"}
    assert syncer.task_exists(google_task_lists, "1") is True

    # Test case: Task does not exist
    assert syncer.task_exists(google_task_lists, "3") is False

    # Test case: Empty task list
    google_task_lists = {"Personal": "empty_tasklist_id"}
    assert syncer.task_exists(google_task_lists, "1") is False


def test_ensure_tasklist_exists(mock_syncer):
    syncer, _, google_tasks_manager = mock_syncer

    # Mock creating a task list
    google_tasks_manager.create_task_list.return_value = {
        "id": "new_tasklist_id"
    }

    # Test case: Task list already exists
    google_task_lists = {"Work": "existing_tasklist_id"}
    assert (
        syncer.ensure_tasklist_exists("Work", google_task_lists)
        == "existing_tasklist_id"
    )

    # Test case: Task list does not exist, create new
    google_task_lists = {}
    tasklist_id = syncer.ensure_tasklist_exists("Personal", google_task_lists)
    assert tasklist_id == "new_tasklist_id"
    assert google_task_lists["Personal"] == "new_tasklist_id"

    # Test case: Tag is None, uses "NoTag"
    tasklist_id = syncer.ensure_tasklist_exists(None, google_task_lists)
    assert tasklist_id == "new_tasklist_id"
    assert google_task_lists["NoTag"] == "new_tasklist_id"


def test_extract_page_id_from_task_title(mock_syncer):
    syncer, _, _ = mock_syncer

    # Test case: Valid task title with ID
    assert syncer.extract_page_id_from_task_title("Task Name (123)") == 123

    # Test case: Task title with non-numeric ID
    assert syncer.extract_page_id_from_task_title("Task Name (ABC)") is None

    # Test case: Task title without parentheses
    assert syncer.extract_page_id_from_task_title("Task Name 123") is None

    # Test case: Task title with misplaced parentheses
    assert syncer.extract_page_id_from_task_title("Task Name (123") is None

    # Test case: Empty task title
    assert syncer.extract_page_id_from_task_title("") is None

    # Test case: Task title with multiple parentheses
    assert (
        syncer.extract_page_id_from_task_title("Task (456) Name (123)") == 123
    )

    # Test case: Task title with only parentheses
    assert syncer.extract_page_id_from_task_title("()") is None
