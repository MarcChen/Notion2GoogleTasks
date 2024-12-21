from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from .authentification import load_credentials, refresh_access_token, print_token_ttl


class GoogleTasksManager:
    """
    A manager class for Google Tasks API to handle task lists, tasks, and subtasks.
    """

    def __init__(self, token_path):
        """
        Initializes the GoogleTasksManager with the provided token path.

        Args:
            token_path (str): Path to the token file.
        """
        self.token_path = token_path
        self.credentials = self._get_credentials()
        self.service = build('tasks', 'v1', credentials=self.credentials)

    def _get_credentials(self):
        """
        Loads and refreshes credentials.

        Returns:
            google.oauth2.credentials.Credentials: Authorized credentials object.
        """
        credentials = load_credentials(self.token_path)
        return refresh_access_token(credentials, self.token_path)

    def list_task_lists(self):
        """
        Lists all task lists.

        Returns:
            dict: A dictionary with task list titles as keys and their IDs as values.
        """
        try:
            print_token_ttl(self.credentials)
            tasklists = self.service.tasklists().list().execute()
            return {tl['title']: tl['id'] for tl in tasklists.get('items', [])}
        except Exception as e:
            raise Exception(f"Error listing task lists: {e}")

    def create_task_list(self, task_list_name):
        """
        Creates a new task list.

        Args:
            task_list_name (str): Name of the new task list.

        Returns:
            dict: Details of the created task list.
        """
        try:
            tasklist = {"title": task_list_name}
            created_tasklist = self.service.tasklists().insert(body=tasklist).execute()
            return {"title": created_tasklist['title'], "id": created_tasklist['id']}
        except Exception as e:
            raise Exception(f"Error creating task list: {e}")

    def list_tasks_in_tasklist(self, tasklist_id, include_completed=True):
        """
        Lists all tasks in a specified task list.

        Args:
            tasklist_id (str): ID of the task list.
            include_completed (bool): Whether to include completed tasks.

        Returns:
            dict: A dictionary with task titles as keys and task details as values.
        """
        try:
            tasks = self.service.tasks().list(
                tasklist=tasklist_id,
                showCompleted=include_completed,
                showHidden=include_completed
            ).execute()
            return {
                task.get('title', 'No Title'): {
                    "id": task['id'],
                    "status": task.get('status'),
                    "completed": task.get('completed'),
                }
                for task in tasks.get('items', [])
            }
        except Exception as e:
            raise Exception(f"Error listing tasks in task list: {e}")

    def create_task(self, tasklist_id, task_title, task_notes=None, due_date=None):
        """
        Creates a new task in a specified task list.

        Args:
            tasklist_id (str): ID of the task list.
            task_title (str): Title of the new task.
            task_notes (str): Notes for the task (optional).
            due_date (str): Due date in RFC 3339 format (optional).

        Returns:
            dict: Details of the created task.
        """
        try:
            task_body = {"title": task_title, "notes": task_notes, "due": due_date}
            return self.service.tasks().insert(tasklist=tasklist_id, body=task_body).execute()
        except Exception as e:
            raise Exception(f"Error creating task: {e}")

    def get_task_details(self, tasklist_id, task_id):
        """
        Fetches details of a specific task.

        Args:
            tasklist_id (str): ID of the task list.
            task_id (str): ID of the task.

        Returns:
            dict: Details of the task.
        """
        try:
            task = self.service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
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

    def delete_task(self, tasklist_id, task_id):
        """
        Deletes a specific task.

        Args:
            tasklist_id (str): ID of the task list.
            task_id (str): ID of the task.

        Returns:
            bool: True if the task was successfully deleted.
        """
        try:
            self.service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()
            return True
        except Exception as e:
            raise Exception(f"Error deleting task: {e}")

    def mark_task_completed(self, tasklist_id, task_id):
        """
        Marks a specific task as completed.

        Args:
            tasklist_id (str): ID of the task list.
            task_id (str): ID of the task.

        Returns:
            dict: Details of the updated task.
        """
        try:
            return self.service.tasks().patch(
                tasklist=tasklist_id, task=task_id, body={"status": "completed"}
            ).execute()
        except Exception as e:
            raise Exception(f"Error marking task as completed: {e}")

    def create_subtask(self, tasklist_id, parent_task_id, subtask_title, subtask_notes=None, due_date=None):
        """
        Creates a subtask under a specified parent task.

        Args:
            tasklist_id (str): ID of the task list.
            parent_task_id (str): ID of the parent task.
            subtask_title (str): Title of the subtask.
            subtask_notes (str): Notes for the subtask (optional).
            due_date (str): Due date in RFC 3339 format (optional).

        Returns:
            dict: Details of the created subtask.
        """
        try:
            subtask_body = {"title": subtask_title, "notes": subtask_notes, "due": due_date}
            created_task = self.service.tasks().insert(tasklist=tasklist_id, body=subtask_body).execute()

            return self.service.tasks().move(
                tasklist=tasklist_id, task=created_task['id'], parent=parent_task_id
            ).execute()
        except Exception as e:
            raise Exception(f"Error creating subtask: {e}")
