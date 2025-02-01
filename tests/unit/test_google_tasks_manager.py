from unittest.mock import MagicMock, patch

import pytest

from services.google_task.src.retrieve_tasks import GoogleTasksManager


@pytest.fixture
def mock_manager():
    """
    Fixture to create a mock instance of GoogleTasksManager with mocked credentials and service.
    """
    with patch(
        "services.google_task.src.retrieve_tasks.GoogleTasksManager._get_credentials"
    ) as mock_creds:
        # Mock credentials with expected universe_domain
        mock_creds.return_value = MagicMock(universe_domain="googleapis.com")
        with patch(
            "services.google_task.src.retrieve_tasks.build"
        ) as mock_build:
            # Mock the Google Tasks service
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            manager = GoogleTasksManager(token_path="dummy_token_path")
            yield manager


def test_list_task_lists(mock_manager):
    """
    Test listing all task lists.
    """
    mock_manager.service.tasklists().list().execute.return_value = {
        "items": [
            {"title": "Task List 1", "id": "1"},
            {"title": "Task List 2", "id": "2"},
        ]
    }
    result = mock_manager.list_task_lists()
    assert result == {"Task List 1": "1", "Task List 2": "2"}


def test_create_task_list(mock_manager):
    """
    Test creating a new task list.
    """
    mock_manager.service.tasklists().insert().execute.return_value = {
        "title": "New Task List",
        "id": "12345",
    }
    result = mock_manager.create_task_list(task_list_name="New Task List")
    assert result == {"title": "New Task List", "id": "12345"}


def test_list_tasks_in_tasklist(mock_manager):
    """
    Test listing tasks in a specific task list.
    """
    mock_manager.service.tasks().list().execute.return_value = {
        "items": [
            {"title": "Task 1", "id": "1", "status": "needsAction"},
            {"title": "Task 2", "id": "2", "status": "completed"},
        ]
    }
    result = mock_manager.list_tasks_in_tasklist(
        tasklist_id="1", include_completed=True
    )
    assert result == {
        "Task 1": {"id": "1", "status": "needsAction", "completed": None},
        "Task 2": {"id": "2", "status": "completed", "completed": None},
    }


def test_create_task(mock_manager):
    """
    Test creating a new task.
    """
    mock_manager.service.tasks().insert().execute.return_value = {
        "title": "New Task",
        "id": "1",
    }
    result = mock_manager.create_task(
        tasklist_id="1",
        task_title="New Task",
        task_notes="Details",
        due_date=None,
    )
    assert result == {"title": "New Task", "id": "1"}


def test_create_subtask(mock_manager):
    """
    Test creating a subtask.
    """
    mock_manager.service.tasks().insert().execute.return_value = {
        "id": "2",
        "title": "Subtask",
    }
    mock_manager.service.tasks().move().execute.return_value = {
        "id": "2",
        "parent": "1",
    }
    result = mock_manager.create_subtask(
        tasklist_id="1", parent_task_id="1", subtask_title="Subtask"
    )
    assert result["parent"] == "1"
    assert result["id"] == "2"


def test_get_created_tasks_since(mock_manager):
    """
    Test retrieving tasks created since the last check.
    """
    from datetime import datetime

    last_checked = datetime.utcnow()
    tasklist_id = "test_tasklist"

    # Mock the API response
    mock_manager.service.tasks().list().execute.return_value = {
        "items": [
            {
                "title": "Task 1",
                "id": "1",
                "status": "needsAction",
                "completed": None,
                "updated": "2023-11-05T12:00:00Z",
            },
            {
                "title": "Task 2",
                "id": "2",
                "status": "completed",
                "completed": "2023-11-06T12:00:00Z",
                "updated": "2023-11-06T12:00:00Z",
            },
            {
                "title": "Task 3",
                "id": "3",
                "status": "needsAction",
                "completed": None,
                "updated": "2023-11-07T12:00:00Z",
            },
        ]
    }

    # Test without filtering by needsAction
    result_all = mock_manager.get_created_tasks_since(
        tasklist_id, last_checked, only_needs_action=False
    )
    assert result_all == {
        "Task 1": {
            "id": "1",
            "status": "needsAction",
            "completed": None,
            "updated": "2023-11-05T12:00:00Z",
        },
        "Task 2": {
            "id": "2",
            "status": "completed",
            "completed": "2023-11-06T12:00:00Z",
            "updated": "2023-11-06T12:00:00Z",
        },
        "Task 3": {
            "id": "3",
            "status": "needsAction",
            "completed": None,
            "updated": "2023-11-07T12:00:00Z",
        },
    }

    # Test filtering by needsAction
    result_filtered = mock_manager.get_created_tasks_since(
        tasklist_id, last_checked, only_needs_action=True
    )
    assert result_filtered == {
        "Task 1": {
            "id": "1",
            "status": "needsAction",
            "completed": None,
            "updated": "2023-11-05T12:00:00Z",
        },
        "Task 3": {
            "id": "3",
            "status": "needsAction",
            "completed": None,
            "updated": "2023-11-07T12:00:00Z",
        },
    }
