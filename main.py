import os
from datetime import datetime

from services.sync_notion_google_task.main import NotionToGoogleTaskSyncer

if __name__ == "__main__":
    notion_api_key = os.getenv("NOTION_API")
    database_id = os.getenv("DATABASE_ID")
    token_path = os.getenv("TOKEN_PATH")
    project_root = os.getenv("PROJECT_ROOT")
    free_mobile_user_id = os.getenv("FREE_MOBILE_USER_ID")
    free_mobile_api_key = os.getenv("FREE_MOBILE_API_KEY")
    last_successful_sync = os.getenv("LAST_SUCCESSFUL_SYNC")

    assert notion_api_key, "NOTION_API environment variable is required."
    assert database_id, "DATABASE_ID environment variable is required."
    assert token_path, "TOKEN_PATH environment variable is required."
    assert project_root, "PROJECT_ROOT environment variable is required."
    assert last_successful_sync, "LAST_SUCCESSFUL_SYNC environment variable is required."
    last_successful_sync = datetime.fromisoformat(last_successful_sync.replace("Z", ""))
    assert (
        free_mobile_user_id
    ), "FREE_MOBILE_USER_ID environment variable is required."
    assert (
        free_mobile_api_key
    ), "FREE_MOBILE_API_KEY environment variable is required."

    syncer = NotionToGoogleTaskSyncer(notion_api_key=notion_api_key, database_id=database_id, project_root=project_root, token_path=token_path,sms_user=free_mobile_user_id, sms_password=free_mobile_api_key)
    syncer.sync_pages_to_google_tasks()
    syncer.sync_google_tasks_to_notion(last_successful_sync = last_successful_sync)