from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from .authentification import load_credentials, refresh_access_token, print_token_ttl

def list_uncompleted_tasks(token_path):
    """
    Lists all uncompleted tasks across all task lists.

    Args:
        token_path (str): Path to the token file.

    Returns:
        dict: A dictionary with task list names as keys and a list of uncompleted tasks as values.
    """
    try:
        credentials = load_credentials(token_path)
        credentials = refresh_access_token(credentials, token_path)
        print_token_ttl(credentials)

        service = build('tasks', 'v1', credentials=credentials)
        uncompleted_tasks = {}

        tasklists = service.tasklists().list().execute()
        for tasklist in tasklists.get('items', []):
            tasklist_title = tasklist['title']
            tasklist_id = tasklist['id']
            uncompleted_tasks[tasklist_title] = []

            tasks = service.tasks().list(tasklist=tasklist_id).execute()
            for task in tasks.get('items', []):
                if task.get('status') != 'completed':
                    uncompleted_tasks[tasklist_title].append({
                        "title": task.get('title', 'No Title'),
                        "id": task['id']
                    })

        return uncompleted_tasks
    except Exception as e:
        raise Exception(f"Error listing uncompleted tasks: {e}")


def create_task_list(token_path, task_list_name):
    """
    Creates a new task list.

    Args:
        token_path (str): Path to the token file.
        task_list_name (str): Name of the new task list.

    Returns:
        dict: Details of the created task list.
    """
    try:
        credentials = load_credentials(token_path)
        credentials = refresh_access_token(credentials, token_path)
        service = build('tasks', 'v1', credentials=credentials)

        tasklist = {"title": task_list_name}
        created_tasklist = service.tasklists().insert(body=tasklist).execute()

        return {"title": created_tasklist['title'], "id": created_tasklist['id']}
    except Exception as e:
        raise Exception(f"Error creating task list: {e}")


def list_tasks_in_tasklist(token_path, tasklist_id, include_completed=True):
    """
    Lists all tasks in a specified task list.

    Args:
        token_path (str): Path to the token file.
        tasklist_id (str): ID of the task list.
        include_completed (bool): Whether to include completed tasks.

    Returns:
        dict: A dictionary with task titles as keys and task details as values.
    """
    try:
        credentials = load_credentials(token_path)
        credentials = refresh_access_token(credentials, token_path)
        service = build('tasks', 'v1', credentials=credentials)

        tasks = service.tasks().list(
            tasklist=tasklist_id,
            showCompleted=include_completed,
            showHidden=include_completed
        ).execute()

        task_dict = {}
        for task in tasks.get('items', []):
            task_dict[task.get('title', 'No Title')] = {
                "id": task['id'],
                "status": task.get('status'),
                "completed": task.get('completed')
            }

        return task_dict
    except Exception as e:
        raise Exception(f"Error listing tasks in task list: {e}")


def create_task(token_path, tasklist_id, task_title, task_notes=None, due_date=None):
    """
    Creates a new task in a specified task list.

    Args:
        token_path (str): Path to the token file.
        tasklist_id (str): ID of the task list.
        task_title (str): Title of the new task.
        task_notes (str): Notes for the task (optional).
        due_date (str): Due date in RFC 3339 format (optional).

    Returns:
        dict: Details of the created task.
    """
    try:
        credentials = load_credentials(token_path)
        credentials = refresh_access_token(credentials, token_path)
        service = build('tasks', 'v1', credentials=credentials)

        task_body = {"title": task_title, "notes": task_notes, "due": due_date}
        created_task = service.tasks().insert(tasklist=tasklist_id, body=task_body).execute()

        return created_task
    except Exception as e:
        raise Exception(f"Error creating task: {e}")


def get_task_details(token_path, tasklist_id, task_id):
    """
    Fetches details of a specific task.

    Args:
        token_path (str): Path to the token file.
        tasklist_id (str): ID of the task list.
        task_id (str): ID of the task.

    Returns:
        dict: Details of the task.
    """
    try:
        credentials = load_credentials(token_path)
        credentials = refresh_access_token(credentials, token_path)
        service = build('tasks', 'v1', credentials=credentials)

        task = service.tasks().get(tasklist=tasklist_id, task=task_id).execute()

        return {
            "title": task.get("title", "No Title"),
            "notes": task.get("notes", ""),
            "due": task.get("due", ""),
            "status": task.get("status", ""),
            "completed": task.get("completed", ""),
            "updated": task.get("updated", ""),
        }
    except Exception as e:
        raise Exception(f"Error fetching task details: {e}")


def delete_task(token_path, tasklist_id, task_id):
    """
    Deletes a specific task.

    Args:
        token_path (str): Path to the token file.
        tasklist_id (str): ID of the task list.
        task_id (str): ID of the task.

    Returns:
        bool: True if the task was successfully deleted.
    """
    try:
        credentials = load_credentials(token_path)
        credentials = refresh_access_token(credentials, token_path)
        service = build('tasks', 'v1', credentials=credentials)

        service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()
        return True
    except Exception as e:
        raise Exception(f"Error deleting task: {e}")

def list_task_lists(token_path):
    """
    Lists all task lists.

    Args:
        token_path (str): Path to the token file.

    Returns:
        dict: A dictionary with task list titles as keys and their IDs as values.
    """
    try:
        credentials = load_credentials(token_path)
        credentials = refresh_access_token(credentials, token_path)
        print_token_ttl(credentials)

        service = build('tasks', 'v1', credentials=credentials)
        tasklist_dict = {}

        tasklists = service.tasklists().list().execute()
        for tasklist in tasklists.get('items', []):
            tasklist_title = tasklist['title']
            tasklist_id = tasklist['id']
            tasklist_dict[tasklist_title] = tasklist_id

        return tasklist_dict
    except Exception as e:
        raise Exception(f"Error listing task lists: {e}")

def create_task_list(token_path, task_list_name):
    """
    Creates a new task list.

    Args:
        token_path (str): Path to the token file.
        task_list_name (str): Name of the new task list.

    Returns:
        dict: Details of the created task list.
    """
    try:
        credentials = load_credentials(token_path)
        credentials = refresh_access_token(credentials, token_path)
        service = build('tasks', 'v1', credentials=credentials)

        tasklist = {"title": task_list_name}
        created_tasklist = service.tasklists().insert(body=tasklist).execute()

        return {"title": created_tasklist['title'], "id": created_tasklist['id']}
    except Exception as e:
        raise Exception(f"Error creating task list: {e}")


def mark_task_completed(token_path, tasklist_id, task_id):
    """
    Marks a specific task as completed.

    Args:
        token_path (str): Path to the token file.
        tasklist_id (str): ID of the task list.
        task_id (str): ID of the task.

    Returns:
        dict: Details of the updated task.
    """
    try:
        credentials = load_credentials(token_path)
        credentials = refresh_access_token(credentials, token_path)
        service = build('tasks', 'v1', credentials=credentials)

        updated_task = service.tasks().patch(
            tasklist=tasklist_id, task=task_id, body={"status": "completed"}
        ).execute()

        return updated_task
    except Exception as e:
        raise Exception(f"Error marking task as completed: {e}")


def create_subtask(token_path, tasklist_id, parent_task_id, subtask_title, subtask_notes=None, due_date=None):
    """
    Creates a subtask under a specified parent task.

    Args:
        token_path (str): Path to the token file.
        tasklist_id (str): ID of the task list.
        parent_task_id (str): ID of the parent task.
        subtask_title (str): Title of the subtask.
        subtask_notes (str): Notes for the subtask (optional).
        due_date (str): Due date in RFC 3339 format (optional).

    Returns:
        dict: Details of the created subtask.
    """
    try:
        credentials = load_credentials(token_path)
        credentials = refresh_access_token(credentials, token_path)
        service = build('tasks', 'v1', credentials=credentials)

        subtask_body = {"title": subtask_title, "notes": subtask_notes, "due": due_date}
        created_task = service.tasks().insert(tasklist=tasklist_id, body=subtask_body).execute()

        moved_task = service.tasks().move(
            tasklist=tasklist_id, task=created_task['id'], parent=parent_task_id
        ).execute()

        return moved_task
    except Exception as e:
        raise Exception(f"Error creating subtask: {e}")
