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
    
    from services.google_task.src.retrieve_tasks import GoogleTasksManager
    from datetime import datetime
    # Initialize GoogleTasksManager
    manager = GoogleTasksManager(token_path)

    # # Initialize NotionClient
    from services.notion.src.notion_client import NotionClient
    notion_client = NotionClient(notion_api_key, database_id, project_root)
    last_time = "2024-12-30T20:12:48Z"
    last_time = datetime.fromisoformat(last_time.replace("Z", ""))
    
    # Get task list ID
    task_lists = manager.list_task_lists()
    tasklist_id = task_lists.get('Mes tâches')
    if not tasklist_id:
        raise Exception("Task list 'Mes tâches' not found")
    print(f"Found task list id: {tasklist_id}")
    
    # Get completed tasks since last check
    # completed_tasks = manager.get_completed_tasks_since(tasklist_id, last_time)
    created_tasks = manager.get_created_tasks_since(tasklist_id, last_time)
    print(f"Created tasks: {created_tasks}")
    # Access the ID of the created task
    for task_title, task_details in created_tasks.items():
        task_id = task_details['id']
        print(f"Task ID: {task_id}")
        ID = notion_client.create_new_page(task_title)
        manager.modify_task_title(tasklist_id, task_id, f"{task_title} | ({ID})")


    # # Loop over completed tasks and mark them as done
    # for task_title, task_details in completed_tasks.items():
    #     task_id = task_details['id']
    #     notion_client.mark_page_as_completed(task_id)
    

