import os
from datetime import datetime
from typing import Dict, List, Optional

from rich import print
from rich.console import Console
from rich.live import Live
from rich.progress import Progress

from services.free_sms_alert.main import SMSAPI
from services.google_task.src.retrieve_tasks import GoogleTasksManager
from services.notion.src.notion_client import NotionClient


class NotionToGoogleTaskSyncer:
    def __init__(
        self,
        notion_api_key: str,
        database_id: str,
        project_root: str,
        token_path: str,
        sms_user: str,
        sms_password: str,
    ):
        self.notion_client = NotionClient(notion_api_key, database_id, project_root)
        self.google_tasks_manager = GoogleTasksManager(token_path)
        self.sms_altert = SMSAPI(sms_user, sms_password)

    ### Method to sync Notion pages to Google Tasks ###

    def sync_pages_to_google_tasks(self):
        """
        Synchronizes Notion pages to Google Tasks with a progress bar that remains at the top.
        """
        notion_pages = self.notion_client.get_filtered_sorted_database()
        if not notion_pages:
            print("[red]No pages retrieved from Notion.[/red]")
            return

        parsed_pages = self.notion_client.parse_notion_response(notion_pages)
        google_task_lists = self.google_tasks_manager.list_task_lists()

        console = Console()
        progress = Progress()

        task = progress.add_task("[cyan]Processing Pages...", total=len(parsed_pages))

        with Live(progress, console=console, refresh_per_second=10):
            for page in parsed_pages:
                page_id = page["unique_id"]
                page_title = page["title"]
                tag = page["tags"] or "NoTag"
                due_date = page["due_date"]

                # Adjust the due date to today if it's too far in the future.
                # This is a personal preference to ensure tasks are dealt with promptly.
                recomputed_due_date = self.compute_due_date(page["due_date"])

                importance = page["importance"]
                text = page["text"]
                urls = page["url"]
                parent_page_name = page["parent_page_name"] or None

                console.print(
                    f"[bold]Processing Page: {page_title} (ID: {page_id})[/bold]"
                )

                if self.task_exists(google_task_lists, page_id):
                    console.print(
                        f"[yellow]Task for page '{page_title}' already exists. Skipping...[/yellow]"
                    )
                    progress.advance(task)
                    continue

                try:
                    tasklist_id = self.ensure_tasklist_exists(tag, google_task_lists)
                    console.print(f"  Task List ID for tag '{tag}': {tasklist_id}")
                except Exception as e:
                    console.print(
                        f"[red]Error ensuring task list for tag '{tag}': {e}[/red]"
                    )
                    progress.advance(task)
                    self.sms_altert.send_sms(
                        f"Error ensuring task list for tag '{tag}': {e}"
                    )
                    raise e

                try:
                    task_description = self.build_task_description(
                        importance, text, urls, due_date
                    )
                    console.print(f"  Task Description: {task_description}")
                except Exception as e:
                    console.print(f"[red]Error building task description: {e}[/red]")
                    progress.advance(task)
                    self.sms_altert.send_sms(f"Error building task description: {e}")
                    raise e

                try:
                    self.google_tasks_manager.create_task(
                        tasklist_id=tasklist_id,
                        task_title=f"{page_title} - {parent_page_name} | ({page_id})",
                        task_notes=task_description,
                        due_date=recomputed_due_date,
                    )
                    console.print(
                        f"[green]Task for page '{page_title}' created successfully![/green]"
                    )
                except Exception as e:
                    console.print(
                        f"[red]Error creating task for page '{page_title}': {e}[/red]"
                    )
                    self.sms_altert.send_sms(
                        f"Error creating task for page '{page_title}': {e}"
                    )
                    raise e

                progress.advance(task)

    def task_exists(self, google_task_lists: Dict[str, str], page_id: str) -> bool:
        """
        Checks if a task for the given Notion page ID already exists in Google Tasks.

        Args:
            google_task_lists (Dict[str, str]): A dictionary of Google task lists with their IDs.
            page_id (str): The unique ID of the Notion page.

        Returns:
            bool: True if the task exists, False otherwise.
        """
        for tasklist_name, tasklist_id in google_task_lists.items():
            tasks = self.google_tasks_manager.list_tasks_in_tasklist(tasklist_id)
            if any(task_title.endswith(f"({page_id})") for task_title in tasks):
                return True
        return False

    def ensure_tasklist_exists(
        self, tag: Optional[str], google_task_lists: Dict[str, str]
    ) -> str:
        """
        Ensures that a task list for the given tag exists, creating it if necessary.

        Args:
            tag (Optional[str]): The tag associated with the task list.

        Returns:
            str: The ID of the existing or newly created task list.
        """
        if not tag:
            tag = "NoTag"  # Use a NoTag name if no tag is provided

        if tag not in google_task_lists:
            created_tasklist = self.google_tasks_manager.create_task_list(tag)
            google_task_lists[tag] = created_tasklist["id"]

        return google_task_lists[tag]

    def build_task_description(
        self,
        importance: Optional[str],
        text: Optional[str],
        urls: Optional[List[str]],
        due_date: Optional[str],
    ) -> str:
        """
        Builds a task description from the given properties.

        Args:
            importance (Optional[str]): The importance level of the task.
            text (Optional[str]): The text content from the Notion page.
            urls (Optional[List[str]]): A list of URLs from the Notion page.
            due_date (Optional[str]): The due date of the task.

        Returns:
            str: The task description.
        """
        description_lines = []
        if importance:
            description_lines.append(f"Importance: {importance}")
        if text:
            description_lines.append(f"Details: {text}")
        if urls:
            description_lines.append("Links:")
            for url in urls:
                description_lines.append(f" - {url}")
        if due_date:
            due_date = datetime.fromisoformat(due_date)
            description_lines.append(f"Due Date: {due_date.strftime('%d-%m-%y')}")
        return "\n".join(description_lines)

    def compute_due_date(self, due_date_str: Optional[str]) -> datetime:
        """
        Computes the due date, adjusting it to today if the difference exceeds 14 days.

        Args:
            due_date_str (Optional[str]): The due date as a string in ISO format, or None.

        Returns:
            datetime: The adjusted due date as a `datetime` object.
        """
        today = datetime.utcnow()

        if due_date_str:
            due_date = datetime.fromisoformat(due_date_str)
        else:
            due_date = today  # Default to today if no due date is provided

        # Adjust the due date if it's more than 14 days from today
        if (due_date - today).days > 14:
            due_date = today

        return due_date

    def extract_page_id_from_task_title(self, task_title: str) -> Optional[str]:
        """
        Extracts the Notion page ID from the Google Task title.
        Args:
            task_title (str): The title of the Google Task.
        Returns:
            Optional[str]: The extracted Notion page ID, or None if not found.
        """
        if "(" in task_title and task_title.endswith(")"):
            return task_title.split("(")[-1].rstrip(")")
        return None

    ### Method to sync completed Google Tasks to Notion ###

    def sync_google_tasks_to_notion(self, last_successful_sync: datetime):
        """
        Synchronizes Google Tasks to Notion with proper order and status handling.
        Processing order: 1. New Tasks → 2. Completed Tasks → 3. Status Alignment
        """
        task_lists = self.google_tasks_manager.list_task_lists()

        for tasklist_name, tasklist_id in task_lists.items():
            # 1. Sync NEW tasks from Google Tasks to Notion first
            created_tasks = self.google_tasks_manager.get_created_tasks_since(
                tasklist_id, last_successful_sync
            )
            if created_tasks:
                for task_title, task_details in created_tasks.items():
                    try:
                        # Extract metadata before modification
                        task_id = task_details["id"]
                        is_completed = task_details.get("status") == "completed"

                        notion_page_id = self.notion_client.create_new_page(task_title)

                        if is_completed:
                            self.notion_client.mark_page_as_completed(notion_page_id)

                        # Update Google Task title with Notion ID
                        updated_title = f"{task_title} | ({notion_page_id})"
                        self.google_tasks_manager.modify_task_title(
                            tasklist_id=tasklist_id,
                            task_id=task_id,
                            new_title=updated_title,
                        )
                        print(
                            f"[green]Created Notion page '{notion_page_id}' from Google Task[/green]"
                        )
                    except Exception as e:
                        print(
                            f"[red]Error creating page for task '{task_title}': {e}[/red]"
                        )
                        self.sms_altert.send_sms(f"Task creation error: {str(e)[:50]}")
                        continue

            # 2. Sync COMPLETED tasks to Notion (after creation to ensure pages exist)
            completed_tasks = self.google_tasks_manager.get_completed_tasks_since(
                tasklist_id, last_successful_sync
            )
            if completed_tasks:
                # Collect IDs of tasks processed in the created_tasks loop to avoid duplicates
                created_task_ids = (
                    {details["id"] for details in created_tasks.values()}
                    if created_tasks
                    else set()
                )

                for task_title, task_details in completed_tasks.items():
                    # Skip if this task was already processed in the created_tasks loop
                    if task_details["id"] in created_task_ids:
                        print(
                            f"[yellow]Skipping completed task '{task_title}' (already processed as created task)[/yellow]"
                        )
                        continue
                    try:
                        # Existing logic to handle completed tasks
                        notion_page_id = self.extract_page_id_from_task_title(
                            task_title
                        )
                        if not notion_page_id:
                            print(
                                f"[yellow]No Notion ID found in task '{task_title}', skipping...[/yellow]"
                            )
                            continue
                        self.notion_client.mark_page_as_completed(notion_page_id)
                        print(
                            f"[green]Marked Notion page '{notion_page_id}' as completed[/green]"
                        )
                    except Exception as e:
                        print(
                            f"[red]Error updating completed task '{task_title}': {e}[/red]"
                        )
                        self.sms_alert.send_sms(f"Task completion error: {str(e)[:50]}")
                        continue

            # 3. Align statuses for ACTIVE tasks (Notion → Google Tasks)
            active_tasks = self.google_tasks_manager.list_tasks_in_tasklist(
                tasklist_id, include_completed=False
            )
            task_ids = [
                self.google_tasks_manager.extract_task_id_from_task_title(t)
                for t in active_tasks
            ]
            task_ids = [tid for tid in task_ids if tid is not None]

            if task_ids:
                try:
                    # Get statuses in bulk for efficiency
                    status_mapping = self.notion_client.retrieve_pages_status(task_ids)
                    for notion_id, status in status_mapping.items():
                        if status == "Done":
                            task_id = next(
                                (tid for tid in task_ids if tid == notion_id), None
                            )
                            if task_id:
                                self.google_tasks_manager.mark_task_completed(
                                    tasklist_id, task_id
                                )
                                print(
                                    f"[green]Synced completion for task '{task_id}' to Google[/green]"
                                )
                except Exception as e:
                    print(f"[red]Error syncing statuses: {e}[/red]")
                    self.sms_altert.send_sms(f"Status sync error: {str(e)[:50]}")
