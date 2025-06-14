import json
from datetime import datetime
from typing import Dict, List, Optional, Set

import requests
from rich import print


class NotionClient:
    def __init__(self, notion_api_key: str, database_id: str, project_root: str):
        """
        Initialize the NotionClient with API key, database ID, and project root.

        Args:
            notion_api_key (str): Notion API key.
            database_id (str): Notion database ID.
            project_root (str): Path to the project root directory.
        """
        self.notion_api_key = notion_api_key
        self.database_id = database_id
        self.project_root = project_root
        self.headers = {
            "Authorization": f"Bearer {self.notion_api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

    def get_filtered_sorted_database(
        self,
        query_page_ids: List[int] = [-1],
        last_successful_sync: Optional[datetime] = None,
    ) -> Optional[Dict]:
        """
        Fetches the database information from Notion with specified filters and sorting.
        Args:
            query_page_ids (List[int], optional): A list of page IDs to filter the database query.
                                                  Defaults to [-1], which loads the default query payload from a JSON file.
            last_successful_sync (Optional[datetime], optional): If provided, adds a filter to only retrieve
                                                                pages modified since this timestamp.
        Returns:
            Optional[Dict]: The JSON response from the Notion API if the request is successful; None otherwise.
        """
        url = f"https://api.notion.com/v1/databases/{self.database_id}/query"

        try:
            if query_page_ids == [-1]:
                with open(
                    f"{self.project_root}/services/notion/config/query_payload.json",
                    "r",
                ) as file:
                    query_payload = json.load(file)

                if last_successful_sync:
                    sync_timestamp = last_successful_sync.isoformat()

                    timestamp_filter = {
                        "timestamp": "last_edited_time",
                        "last_edited_time": {"on_or_after": sync_timestamp},
                    }

                    if "filter" in query_payload:
                        if "and" in query_payload["filter"]:
                            query_payload["filter"]["and"].append(timestamp_filter)
                        else:
                            existing_filter = query_payload["filter"]
                            query_payload["filter"] = {
                                "and": [existing_filter, timestamp_filter]
                            }
                    else:
                        query_payload["filter"] = timestamp_filter
            else:
                query_payload = {
                    "filter": {
                        "or": [
                            {
                                "property": "ID",
                                "unique_id": {"equals": page_id},
                            }
                            for page_id in query_page_ids
                        ]
                    }
                }

            response = requests.post(url, headers=self.headers, json=query_payload)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"[red]Error fetching database: {e}[/red]")
            return None
        except FileNotFoundError as e:
            print(f"[red]Error loading query payload: {e}[/red]")
            return None
        
    def get_page_by_id(self, page_id: str) -> Optional[Dict]:
        """
        Fetches a single page from Notion by its ID.

        Args:
            page_id (str): The unique ID of the page to fetch (without hyphens).

        Returns:
            Optional[Dict]: The JSON response from the Notion API if successful; None otherwise.
        """
        url = f"https://api.notion.com/v1/pages/{page_id.replace('-', '')}"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"[red]Error fetching page {page_id}: {e}[/red]")
            return None

    def fetch_parent_page_names(
        self, parent_page_ids: Set[str]
    ) -> Dict[str, Optional[str]]:
        """
        Fetches names of multiple parent pages in one batch to minimize API calls.

        Args:
            parent_page_ids (Set[str]): A set of unique parent page IDs (without hyphens).

        Returns:
            Dict[str, Optional[str]]: A dictionary mapping parent page IDs to their names.
        """
        parent_page_names: Dict[str, Optional[str]] = {}
        for page_id in parent_page_ids:
            page_id = page_id.replace("-", "")
            url = f"https://api.notion.com/v1/pages/{page_id}"

            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                title_property = (
                    data.get("properties", {}).get("Name", {}).get("title", None)
                )
                if title_property and len(title_property) > 0:
                    parent_page_names[page_id] = (
                        title_property[0].get("text", {}).get("content", None)
                    )
                else:
                    parent_page_names[page_id] = None

            except requests.exceptions.RequestException as e:
                print(f"[red]Error fetching parent page {page_id}: {e}[/red]")
                parent_page_names[page_id] = None

        return parent_page_names

    def find_parent_page_by_name(self, parent_name: str) -> Optional[str]:
        """
        Finds a parent page ID by searching for a page with the given name.

        Args:
            parent_name (str): The name of the parent page to search for.

        Returns:
            Optional[str]: The parent page ID if found, None otherwise.
        """
        url = f"https://api.notion.com/v1/search"
        payload = {
            "query": parent_name,
            "filter": {"value": "page", "property": "object"},
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            for result in results:
                if result.get("object") == "page":
                    # Check if the page title matches exactly
                    properties = result.get("properties", {})
                    title_property = properties.get("Name", {}).get(
                        "title", None
                    ) or properties.get("title", {}).get("title", None)

                    if title_property and len(title_property) > 0:
                        page_title = (
                            title_property[0].get("text", {}).get("content", "")
                        )
                        if page_title.lower() == parent_name.lower():
                            return result.get("id", "").replace("-", "")

            print(f"[yellow]Parent page '{parent_name}' not found[/yellow]")
            return None

        except requests.exceptions.RequestException as e:
            print(f"[red]Error searching for parent page '{parent_name}': {e}[/red]")
            return None

    def mark_page_as_completed(self, task_id: int) -> Optional[Dict]:
        """
        Marks the 'Status' property of a Notion page as 'Done' based on the task ID.

        Args:
            task_id (int): The unique task ID to update.

        Returns:
            Optional[Dict]: The JSON response from the Notion API if successful; None otherwise.
        """
        # Fetch the database to find the unique page ID corresponding to the task ID
        # In notion DB, there's 2 UID, one is the page ID (necessary for API call) and the other is the task ID

        try:
            database_response = self.get_filtered_sorted_database(
                query_page_ids=[task_id]
            )
        except Exception as e:
            print(f"[red]Error fetching database to find task ID {task_id}: {e}[/red]")
            return None

        if database_response is None:
            print(f"[red]Failed to fetch database response for task ID {task_id}[/red]")
            return None

        parsed_data = self.parse_notion_response(database_response)
        page_status = parsed_data[0].get("page_status", None)
        if page_status == "Done":
            print(f"[orange1]Task {task_id} is already marked as 'Done'[/orange1]")
            return None

        page_id = parsed_data[0].get("page_id", None)
        if page_id is None:
            print(f"[red]Failed to find page ID for task ID {task_id}[/red]")
            raise Exception(f"Failed to find page ID for task ID {task_id}")

        # Update the page status to 'Done'
        url = f"https://api.notion.com/v1/pages/{page_id}"
        payload = {"properties": {"Status": {"status": {"name": "Done"}}}}

        try:
            response = requests.patch(url, headers=self.headers, json=payload)
            if response.status_code == 200:
                print(f"[green]Task {task_id} marked as 'Done' successfully![/green]")
                return response.json()
            else:
                print(
                    f"[red]Failed to mark task {task_id} as 'Done'. Status Code: {response.status_code}. Error: {response.text}[/red]"
                )
                return None

        except requests.exceptions.RequestException as e:
            print(f"[red]Error marking task {task_id} as 'Done': {e}[/red]")
            return None

    def create_new_page(
        self,
        title: str,
        tag: Optional[str] = None,
        due_date: Optional[datetime] = None,
        from_task: bool = False,
        parent_page_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Create a new page in the Notion database.
        If from_task is True, sets the FromTask checkbox to True.

        Args:
            title (str): The title of the new page.
            tag (Optional[str]): The tag for the new page.
            due_date (Optional[datetime]): The due date for the new page.
            from_task (bool): Flag to indicate this page comes from a task.
            parent_page_id (Optional[str]): The ID of the parent page to link to.

        Returns:
            Optional[str]: The unique page ID if successful; None otherwise.
        """
        url = "https://api.notion.com/v1/pages"
        # Start with base payload
        payload = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Name": {"title": [{"text": {"content": title}}]},
                "Today": {"checkbox": True},
                "FromTask": {"checkbox": from_task},
            },
        }

        # Add Tags only if tag parameter is provided
        if tag is not None:
            payload["properties"]["Tags"] = {"multi_select": [{"name": tag}]}

        # Add Due Date only if due_date parameter is provided
        if due_date is not None:
            payload["properties"]["Due Date"] = {
                "date": {
                    "start": due_date,
                }
            }

        # Add Parent item relation only if parent_page_id parameter is provided
        if parent_page_id is not None:
            payload["properties"]["Parent item"] = {
                "relation": [{"id": parent_page_id}]
            }

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            print(
                f"[green]Page with ID '{response.json().get('ID', 'N/A')}' created successfully with 'FromTask' set to {from_task}![/green]"
            )
            return (
                response.json()
                .get("properties", {})
                .get("ID", {})
                .get("unique_id", {})
                .get("number", None)
            )

        except requests.exceptions.RequestException as e:
            print(f"[red]Error creating page '{title}': {e}[/red]")
            return None

    def retrieve_pages_status(self, tasks_id: List[int]) -> List[Dict]:
        """
        Retrieve the status of multiple pages based on their task IDs.

        Args:
            tasks_id (List[int]): A list of task IDs to retrieve status for.

        Returns:
            List[Dict]: A list of dictionaries containing the task ID and status of each page.
        """
        database_response = self.get_filtered_sorted_database(query_page_ids=tasks_id)
        if not database_response:
            print("[red]Failed to fetch database to retrieve pages status.[/red]")
            return []

        parsed_data = self.parse_notion_response(database_response)
        tasks_status = []
        for page in parsed_data:
            if int(page["unique_id"]) in tasks_id:
                tasks_status.append(
                    {
                        "task_id": page["unique_id"],
                        "title": page["title"],
                        "page_status": page["page_status"],
                    }
                )
        return tasks_status

    def parse_notion_response(self, response: Dict) -> List[Dict]:
        """
        Parse the Notion response to extract relevant fields, including parent page names.

        Args:
            response (Dict): The JSON response from Notion API.

        Returns:
            List[Dict]: A list of dictionaries containing extracted fields with None instead of [] or {}.
        """
        try:
            results = response.get("results", [])
            parsed_data: List[Dict] = []

            for page in results:
                properties = page.get("properties", {})
                page_id = page.get("id", None).replace("-", "")

                tag = properties.get("Tags", {}).get("multi_select", None)
                if tag and len(tag) > 0:
                    tag = tag[0].get("name", None)
                else:
                    tag = None

                importance_property = properties.get("Importance", {}).get(
                    "select", None
                )
                importance = (
                    importance_property.get("name", None)
                    if importance_property
                    else None
                )

                unique_id = (
                    properties.get("ID", {}).get("unique_id", {}).get("number", None)
                )

                due_date_property = properties.get("Due Date", {}).get("date", None)
                due_date = (
                    due_date_property.get("start", None) if due_date_property else None
                )

                page_url = page.get("url", None)

                estimates_property = properties.get("Estimates", {}).get("select", None)
                estimates = (
                    estimates_property.get("name", None) if estimates_property else None
                )

                title = properties.get("Name", {}).get("title", None)
                title_text = (
                    title[0]["text"]["content"] if title and len(title) > 0 else None
                )

                text_property = properties.get("Text", {}).get("rich_text", None)
                text_property = (
                    text_property[0].get("text", {}).get("content", None)
                    if text_property and len(text_property) > 0
                    else None
                )

                url_property = properties.get("URL", {}).get("rich_text", None)
                links = (
                    [
                        text.get("text", {}).get("link", {}).get("url", None)
                        for text in (url_property or [])
                        if text.get("text", {}).get("link")
                    ]
                    if url_property
                    else None
                )
                links = links if links and len(links) > 0 else None

                laste_edited_time = page.get("last_edited_time", None)
                created_time = page.get("created_time", None)

                parent_page_id = properties.get("Parent item", {}).get("relation", None)
                if parent_page_id and len(parent_page_id) > 0:
                    parent_page_id = parent_page_id[0].get("id", "").replace("-", "")
                else:
                    parent_page_id = None

                status_property = properties.get("Status", {}).get("status", None)
                status = status_property.get("name", None) if status_property else None

                task_id = (
                    properties.get("ID", {}).get("unique_id", {}).get("number", None)
                )
                # Extract "FromTask" checkbox from properties.
                from_task = properties.get("FromTask", {}).get("checkbox", False)

                parsed_data.append(
                    {
                        "unique_id": unique_id,
                        "page_id": page_id,
                        "task_id": task_id,
                        "title": title_text,
                        "page_status": status,
                        "created_time": created_time,
                        "last_edited_time": laste_edited_time,
                        "estimates": estimates,
                        "importance": importance,
                        "tags": tag,
                        "due_date": due_date,
                        "page_url": page_url,
                        "text": text_property,
                        "url": links,
                        "parent_page_id": parent_page_id,
                        "FromTask": from_task,
                    }
                )

            parent_page_ids: Set[str] = {
                item["parent_page_id"] for item in parsed_data if item["parent_page_id"]
            }
            parent_page_names = self.fetch_parent_page_names(parent_page_ids)

            for item in parsed_data:
                if item["parent_page_id"]:
                    item["parent_page_name"] = parent_page_names.get(
                        item["parent_page_id"], None
                    )
                else:
                    item["parent_page_name"] = None

            return parsed_data

        except KeyError as e:
            print(f"Error parsing Notion response: Missing key {e}")
            return []
        except Exception as e:
            print(f"Unexpected error while parsing Notion response: {e}")
            return []
