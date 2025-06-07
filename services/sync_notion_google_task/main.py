import datetime as dt
from datetime import datetime
from typing import Dict, List, Optional

from pytest import console_main
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
        verbose: bool = True,
    ):
        self.notion_client = NotionClient(notion_api_key, database_id, project_root)
        self.google_tasks_manager = GoogleTasksManager(token_path)
        self.sms_client = SMSAPI(sms_user, sms_password)
        self.verbose = verbose

    def _verbose_print(
        self, message: str, console: Console, style: str = "", *args, **kwargs
    ):
        """Print message only if verbose mode is enabled.

        Args:
            message (str): The message template with {} placeholders
            style (str): Rich markup style for colored output
            *args: Arguments to format into the message when verbose is True
            **kwargs: Keyword arguments to format into the message when verbose is True
        """
        if self.verbose:
            # When verbose is on, format the message with all provided arguments
            formatted_message = (
                message.format(*args, **kwargs) if (args or kwargs) else message
            )
            if style:
                console.print(f"[{style}]{formatted_message}[/{style}]")
            else:
                console.print(formatted_message)
        else:
            # When verbose is off, replace all parameters with ***
            # Count the number of {} placeholders and replace them with ***
            placeholder_count = message.count("{}")
            if placeholder_count > 0:
                sanitized_message = message.format(*(["***"] * placeholder_count))
            else:
                sanitized_message = message

            if style:
                console.print(f"[{style}]{sanitized_message}[/{style}]")
            else:
                console.print(sanitized_message)

    def _safe_truncate(self, text: str, max_length: int = 20) -> str:
        """Safely truncate text for non-verbose output."""
        if not text:
            return "N/A"
        return text if len(text) <= max_length else f"{text[:max_length]}..."

    # Method to sync Notion pages to Google Tasks

    def sync_pages_to_google_tasks(
        self, last_successful_sync: Optional[datetime] = None
    ):
        """
        Synchronizes Notion pages to Google Tasks with a progress bar that remains at the top.

        Args:
            last_successful_sync (Optional[datetime]): If provided, only sync pages
                                                      modified since this timestamp.
        """
        notion_pages = self.notion_client.get_filtered_sorted_database(
            last_successful_sync=last_successful_sync
        )
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
                page_url = page["page_url"]
                parent_page_name = page["parent_page_name"] or None

                self._verbose_print("Processing Page ID: {}", console, "bold", page_id)
                self._verbose_print("Page Title: {}", console, "blue", page_title)

                # Modify check: also skip if the Notion page has the FromTask checkbox enabled
                if self.task_exists(google_task_lists, page_id) or page.get(
                    "FromTask", False
                ):
                    self._verbose_print("Task for page ID '{}' already exists or FromTask enabled. Skipping...", console, "yellow", page_id)
                    progress.advance(task)
                    continue

                try:
                    tasklist_id = self.ensure_tasklist_exists(tag, google_task_lists)
                except Exception as e:
                    self._verbose_print("Error ensuring task list for tag '{}': {}", console, "red", tag, e)
                    progress.advance(task)
                    self.sms_client.send_sms(
                        f"Error ensuring task list for tag '{tag}': {e}"
                    )
                    raise e

                try:
                    task_description = self.build_task_description(
                        importance, text, urls, page_url, due_date
                    )
                except Exception as e:
                    console.print(f"[red]Error building task description: {e}[/red]")
                    progress.advance(task)
                    self.sms_client.send_sms(f"Error building task description: {e}")
                    raise e

                try:
                    task_title_full = (
                        f"{page_title} - {parent_page_name} | ({page_id})"
                        if parent_page_name
                        else f"{page_title} | ({page_id})"
                    )
                    self.google_tasks_manager.create_task(
                        tasklist_id=tasklist_id,
                        task_title=task_title_full,
                        task_notes=task_description,
                        due_date=recomputed_due_date,
                    )
                    self._verbose_print("Task for page ID '{}' created successfully!", console, "green", page_id)
                except Exception as e:
                    self._verbose_print("Error creating task for page ID '{}': {}", console, "red", page_id, e)
                    self.sms_client.send_sms(
                        f"Error creating task for page ID '{page_id}': {e}"
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
        page_url: Optional[str],
        due_date: Optional[str],
    ) -> str:
        """
        Builds a task description from the given properties.

        Args:
            importance (Optional[str]): The importance level of the task.
            text (Optional[str]): The text content from the Notion page.
            urls (Optional[List[str]]): A list of URLs from the Notion page.
            page_url (Optional[List[str]]): Notion page URL.
            due_date (Optional[str]): The due date of the task.

        Returns:
            str: The task description.
        """
        description_lines = []
        if page_url:
            description_lines.append(f"Page URL: {page_url}")
        if importance:
            description_lines.append(f"Importance: {importance}")
        if text:
            description_lines.append(f"Details: {text}")
        if urls:
            description_lines.append("Links:")
            for url in urls:
                description_lines.append(f" - {url}")
        if due_date:
            due_date_obj = datetime.fromisoformat(due_date)
            description_lines.append(f"Due Date: {due_date_obj.strftime('%d-%m-%y')}")
        return "\n".join(description_lines)

    def compute_due_date(self, due_date_str: Optional[str]) -> datetime:
        """
        Computes the due date, adjusting it to today if the difference exceeds 1 year.

        Args:
            due_date_str (Optional[str]): The due date as a string in ISO format, or None.

        Returns:
            datetime: The adjusted due date as a `datetime` object.
        """
        today = datetime.now(dt.timezone.utc)

        if due_date_str:
            due_date = datetime.fromisoformat(due_date_str)
            if due_date.tzinfo is None:
                due_date = due_date.replace(tzinfo=dt.timezone.utc)

            # Calculate the difference in days
            days_difference = (due_date - today).days

            # Adjust the due date if it's more than 365 days from today
            if days_difference > 365:
                return today
            else:
                return due_date
        else:
            return today

    def extract_page_id_from_task_title(self, task_title: str) -> Optional[int]:
        """
        Extracts the Notion page ID from the Google Task title.
        Args:
            task_title (str): The title of the Google Task.
        Returns:
            Optional[int]: The extracted Notion page ID as an integer, or None if not found.
        """
        if "(" in task_title and task_title.endswith(")"):
            try:
                return int(task_title.split("(")[-1].rstrip(")"))
            except ValueError:
                return None
        return None

    def extract_parent_page_from_task_title(
        self, task_title: str
    ) -> tuple[str, Optional[str]]:
        """
        Extracts parent page name from task title if it contains the format "title - parent_page_name".
        Properly handles parent page names that contain hyphens.

        Args:
            task_title (str): The title of the Google Task.

        Returns:
            tuple[str, Optional[str]]: A tuple of (cleaned_title, parent_page_name).
            cleaned_title is the task title without the parent page reference.
            parent_page_name is the extracted parent page name or None if not found.
        """
        # Look for the first occurrence of " - " as the separator between title and parent
        # This preserves any hyphens in the parent page name
        separator_index = task_title.find(" - ")

        if separator_index != -1:
            # Title has format "title - parent_page_name"
            cleaned_title = task_title[:separator_index].strip()
            parent_page_name = task_title[separator_index + 3 :].strip()
            return cleaned_title, parent_page_name

        # No parent page reference found
        return task_title, None

    # Method to sync completed Google Tasks to Notion #

    def sync_google_tasks_to_notion(self, last_successful_sync: datetime):
        """
        Synchronizes Google Tasks to Notion with proper order and status handling.
        Processing order: 1. New Tasks → 2. Completed Tasks → 3. Status Alignment
        """

        def print_progress(current_step: int, total_steps: int, step_description: str):
            """
            Prints a simple progress message in the form:
                Step X/Y: step_description
            """
            print(
                f"\n[blue]Step {current_step}/{total_steps}: {step_description}[/blue]"
            )

        TOTAL_STEPS = 3
        console = Console()
        task_lists = self.google_tasks_manager.list_task_lists()

        for tasklist_name, tasklist_id in task_lists.items():
            # Print out the task list name
            self._verbose_print("Processing Task List: {}", console, "bold", tasklist_name)

            # -----------------------------
            # Part 1: Sync NEW tasks
            # -----------------------------
            print_progress(
                current_step=1,
                total_steps=TOTAL_STEPS,
                step_description="Sync NEW tasks from Google Tasks to Notion",
            )
            created_tasks = self.google_tasks_manager.get_created_tasks_since(
                tasklist_id, last_successful_sync
            )
            if created_tasks:
                for task_title, task_details in created_tasks.items():
                    try:
                        task_id = task_details["id"]
                        task_due = task_details["due"]
                        is_completed = task_details.get("status") == "completed"
                        potential_notion_id = self.extract_page_id_from_task_title(
                            task_title
                        )

                        if potential_notion_id:
                            if is_completed:
                                self.notion_client.mark_page_as_completed(
                                    potential_notion_id
                                )
                            continue

                        # Check if task title contains parent page reference
                        cleaned_title, parent_page_name = (
                            self.extract_parent_page_from_task_title(task_title)
                        )
                        parent_page_id = None

                        if parent_page_name:
                            # Find the parent page ID by name
                            parent_page_id = (
                                self.notion_client.find_parent_page_by_name(
                                    parent_page_name
                                )
                            )
                            if parent_page_id:
                                self._verbose_print("Found parent page '{}' with ID: {}", console, "green", parent_page_name, parent_page_id)
                            else:
                                self._verbose_print("Parent page '{}' not found, creating task without parent", console, "yellow", parent_page_name)

                        # Create new Notion page with FromTask checkbox = True
                        notion_page_id = self.notion_client.create_new_page(
                            cleaned_title,
                            tasklist_name,
                            task_due,
                            from_task=True,
                            parent_page_id=parent_page_id,
                        )
                        updated_title = f"{cleaned_title} | ({notion_page_id})"
                        self.google_tasks_manager.modify_task_title(
                            tasklist_id=tasklist_id,
                            task_id=task_id,
                            new_title=updated_title,
                        )
                    except Exception as e:
                        self._verbose_print("Error creating page for task '{}': {}", console, "red", task_title, e)
                        self.sms_client.send_sms(f"Task creation error: {str(e)[:50]}")
                        continue

            # -----------------------------
            # Part 2: Sync COMPLETED tasks
            # -----------------------------
            print_progress(
                current_step=2,
                total_steps=TOTAL_STEPS,
                step_description="Sync COMPLETED tasks to Notion",
            )
            completed_tasks = self.google_tasks_manager.get_completed_tasks_since(
                tasklist_id, last_successful_sync
            )
            if completed_tasks:
                created_task_ids = (
                    {details["id"] for details in created_tasks.values()}
                    if created_tasks
                    else set()
                )
                for task_title, task_details in completed_tasks.items():
                    if task_details["id"] in created_task_ids:
                        continue
                    try:
                        notion_page_id = self.extract_page_id_from_task_title(
                            task_title
                        )
                        if not notion_page_id:
                            print(
                                "[yellow]No Notion ID found in task title, skipping...[/yellow]"
                            )
                            continue
                        self.notion_client.mark_page_as_completed(notion_page_id)
                    except Exception as e:
                        print(f"[red]Error updating completed task: {e}[/red]")
                        self.sms_client.send_sms(
                            f"Error updating completed task: {str(e)[:50]}"
                        )
                        continue

            # -----------------------------
            # Part 3: Align statuses (Notion → Google Tasks)
            # -----------------------------
            print_progress(
                current_step=3,
                total_steps=TOTAL_STEPS,
                step_description="Align statuses for ACTIVE tasks (Notion → Google)",
            )
            active_tasks = self.google_tasks_manager.list_tasks_in_tasklist(
                tasklist_id, include_completed=False
            )

            notion_to_google = {}
            for title, task_data in active_tasks.items():
                notion_id = self.google_tasks_manager.extract_task_id_from_task_title(
                    title
                )
                if notion_id is not None:
                    notion_to_google[str(notion_id)] = task_data["id"]

            if notion_to_google:
                try:
                    notion_ids = [
                        int(notion_id) for notion_id in notion_to_google.keys()
                    ]
                    status_mapping = self.notion_client.retrieve_pages_status(
                        notion_ids
                    )
                    for status_item in status_mapping:
                        notion_id = str(status_item["task_id"])
                        status = status_item["page_status"]
                        if status == "Done":
                            google_task_id = notion_to_google.get(notion_id)
                            if google_task_id:
                                self.google_tasks_manager.mark_task_completed(
                                    tasklist_id, google_task_id
                                )
                                self._verbose_print("Marked Google Task ID '{}' as completed", console, "green", google_task_id)
                except Exception as e:
                    console.print(f"[red]Error syncing statuses: {e}[/red]")

            console.print("[green]Done processing all steps for this task list![/green]")
