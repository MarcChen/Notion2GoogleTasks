import os
from datetime import datetime
from services.notion.src.notion_client import NotionClient
from services.google_task.src.retrieve_tasks import GoogleTasksManager
from services.sync_notion_google_task.main import NotionToGoogleTaskSyncer

def test_real_integration_sync_pages_to_google_tasks():
    # Load real API keys and paths from environment variables
    notion_api_key = os.getenv("NOTION_API")
    database_id = os.getenv("DATABASE_ID")
    token_path = os.getenv("TOKEN_PATH")
    project_root = os.getenv("PROJECT_ROOT")

    assert notion_api_key, "NOTION_API environment variable is required."
    assert database_id, "DATABASE_ID environment variable is required."
    assert token_path, "TOKEN_PATH environment variable is required."
    assert project_root, "PROJECT_ROOT environment variable is required."

    # Initialize real clients
    notion_client = NotionClient(notion_api_key, database_id, project_root)
    google_tasks_manager = GoogleTasksManager(token_path)
    syncer = NotionToGoogleTaskSyncer(
        notion_api_key=notion_api_key,
        database_id=database_id,
        project_root=project_root,
        token_path=token_path,
    )

    # Run the synchronization method
    syncer.sync_pages_to_google_tasks()

    # Fetch the Notion pages after sync
    notion_pages = notion_client.get_filtered_sorted_database()
    parsed_pages = notion_client.parse_notion_response(notion_pages) if notion_pages else []

    # Fetch Google Task lists
    google_task_lists = google_tasks_manager.list_task_lists()

    # Validate synchronization
    for page in parsed_pages:
        page_id = page["unique_id"]
        tag = page["tags"] or "NoTag"
        tasklist_id = google_task_lists.get(tag)

        if not tasklist_id:
            assert False, f"Task list for tag '{tag}' was not found."

        tasks = google_tasks_manager.list_tasks_in_tasklist(tasklist_id)
        assert any(
            f"({page_id})" in task for task in tasks.keys()
        ), f"Task for Notion page {page_id} was not found in Google Tasks."

    print("Integration test passed. All tasks were synchronized successfully.")
