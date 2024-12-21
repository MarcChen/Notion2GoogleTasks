import os
from datetime import datetime
from services.notion.src.notion_client import NotionClient
from services.google_task.src.retrieve_tasks import GoogleTasksManager
from services.sync_notion_google_task.main import NotionToGoogleTaskSyncer

def test_real_integration_sync_pages_to_google_tasks():
    # Load real API keys from environment variables
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
    syncer = NotionToGoogleTaskSyncer(notion_client, google_tasks_manager)

    # Run the sync method
    syncer.sync_pages_to_google_tasks()

    # Verify that the sync process worked
    notion_pages = notion_client.get_filtered_sorted_database()
    if notion_pages :
        pages = notion_client.parse_notion_response(notion_pages)
    google_task_lists = google_tasks_manager.list_task_lists()

    # Check for task creation in Google Tasks
    for page in pages:
        page_id = page['unique_id']
        task_list_id = google_task_lists.get(page['tags'] or "NoTag")
        tasks = google_tasks_manager.list_tasks_in_tasklist(task_list_id)
        
        assert any(f"({page_id})" in task for task in tasks), f"Task for Notion page {page_id} was not found in Google Tasks."

    print("Integration test passed. All tasks were synchronized successfully.")
