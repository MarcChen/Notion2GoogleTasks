import os
from services.sync_notion_google_task.main import NotionToGoogleTaskSyncer

if __name__ == "__main__":
    notion_api_key = os.getenv("NOTION_API")
    database_id = os.getenv("DATABASE_ID")
    token_path = os.getenv("TOKEN_PATH")
    project_root = os.getenv("PROJECT_ROOT")

    assert notion_api_key, "NOTION_API environment variable is required."
    assert database_id, "DATABASE_ID environment variable is required."
    assert token_path, "TOKEN_PATH environment variable is required."
    assert project_root, "PROJECT_ROOT environment variable is required."

    syncer = NotionToGoogleTaskSyncer(notion_api_key, database_id, project_root, token_path)
    syncer.sync_pages_to_google_tasks()
