from typing import Optional, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from services.google_task.src.authentification import load_credentials, refresh_access_token, print_token_ttl
from datetime import datetime
import time

class GoogleTasksManager:
    """
    A manager class for Google Tasks API to handle task lists, tasks, and subtasks.
    """

    def __init__(self, token_path: str):
        """
        Initializes the GoogleTasksManager with the provided token path.

        Args:
            token_path (str): Path to the token file.
        """
        self.token_path: str = token_path
        self.credentials: Credentials = self._get_credentials()
        self.service = build('tasks', 'v1', credentials=self.credentials)

    def _get_credentials(self) -> Credentials:
        """
        Loads and refreshes credentials.

        Returns:
            google.oauth2.credentials.Credentials: Authorized credentials object.
        """
        credentials = load_credentials(self.token_path)
        return refresh_access_token(credentials, self.token_path)

    def list_task_lists(self) -> Dict[str, str]:
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

    def create_task_list(self, task_list_name: str) -> Dict[str, str]:
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

    def list_tasks_in_tasklist(self, tasklist_id: str, include_completed: bool = True) -> Dict[str, Dict[str, Any]]:
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

    def create_task(
        self,
        tasklist_id: str,
        task_title: str,
        task_notes: Optional[str] = None,
        due_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Creates a new task in a specified task list.

        Args:
            tasklist_id (str): ID of the task list.
            task_title (str): Title of the new task.
            task_notes (Optional[str]): Notes for the task (optional).
            due_date (Optional[datetime]): Due date as a datetime object (optional).

        Returns:
            dict: Details of the created task.
        """
        try:
            task_body = {"title": task_title, "notes": task_notes}
            if due_date:
                if isinstance(due_date, datetime):
                    due_date = due_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'  # Convert datetime to RFC 3339
                elif not isinstance(due_date, str):
                    raise ValueError("due_date must be a datetime object or an ISO 8601 formatted string")
                task_body["due"] = due_date
            response = self.service.tasks().insert(tasklist=tasklist_id, body=task_body).execute()
            return response
        except Exception as e:
            raise Exception(f"Error creating task: {e}")

    def get_task_details(self, tasklist_id: str, task_id: str) -> Dict[str, Any]:
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

    def delete_task(self, tasklist_id: str, task_id: str) -> bool:
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

    def mark_task_completed(self, tasklist_id: str, task_id: str) -> Dict[str, Any]:
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

    def create_subtask(
        self,
        tasklist_id: str,
        parent_task_id: str,
        subtask_title: str,
        subtask_notes: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates a subtask under a specified parent task.

        Args:
            tasklist_id (str): ID of the task list.
            parent_task_id (str): ID of the parent task.
            subtask_title (str): Title of the subtask.
            subtask_notes (Optional[str]): Notes for the subtask (optional).
            due_date (Optional[str]): Due date in RFC 3339 format (optional).

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

    def get_completed_tasks_since(self, tasklist_id: str, last_checked: datetime) -> Dict[str, Dict[str, Any]]:
        """
        Retrieves tasks that have been completed since the last check.

        Args:
            tasklist_id (str): ID of the task list.
            last_checked (datetime): The timestamp of the last check.

        Returns:
            dict: A dictionary with task titles as keys and task details as values.
        """
        try:
            tasks = self.service.tasks().list(
                tasklist=tasklist_id,
                showCompleted=True,
                showHidden=True,
                updatedMin=last_checked.isoformat() + 'Z'
            ).execute()
            return {
                task.get('title', 'No Title'): {
                    "id": task['id'],
                    "status": task.get('status'),
                    "completed": task.get('completed'),
                    "updated": task.get('updated'),
                }
                for task in tasks.get('items', []) if task.get('status') == 'completed'
            }
        except Exception as e:
            raise Exception(f"Error retrieving completed tasks: {e}")

    def get_created_tasks_since(self, tasklist_id: str, last_checked: datetime) -> Dict[str, Dict[str, Any]]:
        """
        Retrieves tasks that have been created since the last check.

        Args:
            tasklist_id (str): ID of the task list.
            last_checked (datetime): The timestamp of the last check.

        Returns:
            dict: A dictionary with task titles as keys and task details as values.
        """
        try:
            tasks = self.service.tasks().list(
                tasklist=tasklist_id,
                showCompleted=True,
                showHidden=True,
                updatedMin=last_checked.isoformat() + 'Z'
            ).execute()
            return {
                task.get('title', 'No Title'): {
                    "id": task['id'],
                    "status": task.get('status'),
                    "completed": task.get('completed'),
                    "updated": task.get('updated'),
                }
                for task in tasks.get('items', []) if task.get('status') == 'needsAction'
            }
        except Exception as e:
            raise Exception(f"Error retrieving created tasks: {e}")
        
    def modify_task_title(self, tasklist_id: str, task_id: str, new_title: str) -> Dict[str, Any]:
        """
        Modifies the title of a specific task.

        Args:
            tasklist_id (str): ID of the task list.
            task_id (str): ID of the task.
            new_title (str): New title for the task.

        Returns:
            dict: Details of the updated task.
        """
        try:
            return self.service.tasks().patch(
                tasklist=tasklist_id, task=task_id, body={"title": new_title}
            ).execute()
        except Exception as e:
            raise Exception(f"Error modifying task title: {e}")