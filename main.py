import os
from services.sync_notion_google_task.main import NotionToGoogleTaskSyncer

if __name__ == "__main__":
    notion_api_key = os.getenv("NOTION_API")
    database_id = os.getenv("DATABASE_ID")
    token_path = os.getenv("TOKEN_PATH")
    project_root = os.getenv("PROJECT_ROOT")
    free_mobile_user_id = os.getenv("FREE_MOBILE_USER_ID")
    free_mobile_api_key = os.getenv("FREE_MOBILE_API_KEY")

    assert notion_api_key, "NOTION_API environment variable is required."
    assert database_id, "DATABASE_ID environment variable is required."
    assert token_path, "TOKEN_PATH environment variable is required."
    assert project_root, "PROJECT_ROOT environment variable is required."
    assert free_mobile_user_id, "FREE_MOBILE_USER_ID environment variable is required."
    assert free_mobile_api_key, "FREE_MOBILE_API_KEY environment variable is required."

    # syncer = NotionToGoogleTaskSyncer(notion_api_key=notion_api_key, database_id=database_id, project_root=project_root, token_path=token_path,sms_user=free_mobile_user_id, sms_password=free_mobile_api_key)
    # syncer.sync_pages_to_google_tasks()
    
    # from services.google_task.src.retrieve_tasks import GoogleTasksManager
    # from datetime import datetime
    # # Initialize GoogleTasksManager
    # manager = GoogleTasksManager(token_path)
    # last_time = "2024-12-20T16:14:30Z"
    # last_time = datetime.fromisoformat(last_time.replace("Z", ""))
    
    # # Get task list ID
    # task_lists = manager.list_task_lists()
    # tasklist_id = task_lists.get('Travail')
    # if not tasklist_id:
    #     raise Exception("Task list 'Travail' not found")
    # print(f"Found task list id: {tasklist_id}")
    
    # # Get completed tasks since last check
    # completed_tasks = manager.get_completed_tasks_since(tasklist_id, last_time)
    
    # # Loop over completed tasks and mark them as done
    # for task_title, task_details in completed_tasks.items():
    #     task_id = task_details['id']
    #     print(f"Marking task '{task_title}' with ID '{task_id}' as done.")
    
    # # Initialize NotionClient
    from services.notion.src.notion_client import NotionClient
    notion_client = NotionClient(notion_api_key, database_id, project_root)
    notion_client.mark_page_as_completed(597)
