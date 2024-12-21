import os
import pytest
from services.google_task.src.retrieve_tasks import GoogleTasksManager


@pytest.fixture(scope="module")
def google_tasks_manager():
    """
    Fixture to initialize GoogleTasksManager with a real token path.
    """
    token_path = os.getenv("TOKEN_PATH")
    if not token_path:
        pytest.fail("TOKEN_PATH environment variable is not set.")
    return GoogleTasksManager(token_path=token_path)


@pytest.fixture(scope="module")
def integration_task_list(google_tasks_manager):
    """
    Fixture to create a new task list for integration testing.
    Deletes all tasks in the task list before deleting the task list itself.
    """
    task_list_name = "Integration Test"
    result = google_tasks_manager.create_task_list(task_list_name=task_list_name)
    yield result  # Provide the created task list to the tests
    
    # Cleanup: Delete all tasks in the task list
    tasklist_id = result["id"]
    tasks = google_tasks_manager.list_tasks_in_tasklist(tasklist_id=tasklist_id)
    for task_title, task_details in tasks.items():
        google_tasks_manager.delete_task(tasklist_id=tasklist_id, task_id=task_details["id"])
    
    # Cleanup: Delete the task list
    google_tasks_manager.service.tasklists().delete(tasklist=tasklist_id).execute()


def test_list_task_lists(google_tasks_manager):
    """
    Integration test: Lists all task lists from the real Google API.
    """
    task_lists = google_tasks_manager.list_task_lists()
    assert isinstance(task_lists, dict)
    print("Task Lists:", task_lists)


def test_create_task(google_tasks_manager, integration_task_list):
    """
    Integration test: Creates a new task in the integration test task list.
    """
    tasklist_id = integration_task_list["id"]
    task_title = "Test Task"
    result = google_tasks_manager.create_task(
        tasklist_id=tasklist_id,
        task_title=task_title,
        task_notes="This is a test task",
        due_date=None,
    )
    assert result["title"] == task_title
    print("Created Task:", result)


def test_create_subtask(google_tasks_manager, integration_task_list):
    """
    Integration test: Creates a subtask under a parent task in the integration test task list.
    """
    tasklist_id = integration_task_list["id"]

    # Create a parent task
    parent_task_title = "Parent Task"
    parent_task = google_tasks_manager.create_task(
        tasklist_id=tasklist_id,
        task_title=parent_task_title,
        task_notes="This is the parent task"
    )
    parent_task_id = parent_task["id"]

    # Create a subtask under the parent task
    subtask_title = "Subtask"
    subtask = google_tasks_manager.create_subtask(
        tasklist_id=tasklist_id,
        parent_task_id=parent_task_id,
        subtask_title=subtask_title,
        subtask_notes="This is a subtask"
    )
    assert subtask["parent"] == parent_task_id
    assert subtask["title"] == subtask_title
    print("Created Subtask:", subtask)


def test_list_tasks_in_tasklist(google_tasks_manager, integration_task_list):
    """
    Integration test: Lists tasks in the integration test task list.
    """
    tasklist_id = integration_task_list["id"]
    tasks = google_tasks_manager.list_tasks_in_tasklist(tasklist_id=tasklist_id)
    assert isinstance(tasks, dict)
    print("Tasks in Task List:", tasks)


def test_get_task_details(google_tasks_manager, integration_task_list):
    """
    Integration test: Retrieves details of a specific task.
    """
    tasklist_id = integration_task_list["id"]
    task_title = "Detailed Task"
    task = google_tasks_manager.create_task(
        tasklist_id=tasklist_id,
        task_title=task_title,
        task_notes="Task for testing details retrieval",
    )
    task_id = task["id"]

    # Get task details
    task_details = google_tasks_manager.get_task_details(tasklist_id=tasklist_id, task_id=task_id)
    assert task_details["title"] == task_title
    print("Task Details:", task_details)


def test_mark_task_completed(google_tasks_manager, integration_task_list):
    """
    Integration test: Marks a task as completed.
    """
    tasklist_id = integration_task_list["id"]
    task_title = "Complete Me"
    task = google_tasks_manager.create_task(
        tasklist_id=tasklist_id,
        task_title=task_title,
    )
    task_id = task["id"]

    # Mark task as completed
    completed_task = google_tasks_manager.mark_task_completed(tasklist_id=tasklist_id, task_id=task_id)
    assert completed_task["status"] == "completed"
    print("Completed Task:", completed_task)


def test_delete_task(google_tasks_manager, integration_task_list):
    """
    Integration test: Deletes a task.
    """
    tasklist_id = integration_task_list["id"]
    task_title = "Delete Me"
    task = google_tasks_manager.create_task(
        tasklist_id=tasklist_id,
        task_title=task_title,
    )
    task_id = task["id"]

    # Delete task
    result = google_tasks_manager.delete_task(tasklist_id=tasklist_id, task_id=task_id)
    assert result is True
    print("Task Deleted Successfully")
