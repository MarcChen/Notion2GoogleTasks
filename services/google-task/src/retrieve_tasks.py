from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from .authentification import load_credentials, refresh_access_token, print_token_ttl

# Function to list all uncompleted tasks
def list_uncompleted_tasks(token_path):
    # Load and refresh credentials
    credentials = load_credentials(token_path)
    credentials = refresh_access_token(credentials, token_path)
    print_token_ttl(credentials)

    # Initialize the Tasks API client
    service = build('tasks', 'v1', credentials=credentials)

    print("Listing uncompleted tasks...")
    uncompleted_tasks = {}
    try:
        tasklists = service.tasklists().list().execute()
        for tasklist in tasklists.get('items', []):
            tasklist_title = tasklist['title']
            tasklist_id = tasklist['id']
            uncompleted_tasks[tasklist_title] = []
            
            # Get tasks within the current task list
            tasks = service.tasks().list(tasklist=tasklist_id).execute()
            if 'items' in tasks:
                for task in tasks['items']:
                    if not task.get('status') == 'completed':
                        uncompleted_tasks[tasklist_title].append({
                            "title": task.get('title', 'No Title'),
                            "id": task['id']
                        })
    except Exception as e:
        print(f"Error accessing Google Tasks API: {e}")
    
    return uncompleted_tasks

def create_task_list(token_path, task_list_name):
    credentials = load_credentials(token_path)
    credentials = refresh_access_token(credentials, token_path)

    service = build('tasks', 'v1', credentials=credentials)

    print(f"Creating task list: {task_list_name}")
    try:
        tasklist = {"title": task_list_name}
        created_tasklist = service.tasklists().insert(body=tasklist).execute()
        return {
            "title": created_tasklist['title'],
            "id": created_tasklist['id']
        }
    except Exception as e:
        print(f"Error creating task list: {e}")
        return None
    
def list_tasks_in_tasklist(token_path, tasklist_id, include_completed=True):
    credentials = load_credentials(token_path)
    credentials = refresh_access_token(credentials, token_path)

    service = build('tasks', 'v1', credentials=credentials)

    print(f"Listing tasks in task list ID: {tasklist_id}")
    task_dict = {}
    try:
        # Include completed and hidden tasks if requested
        tasks = service.tasks().list(
            tasklist=tasklist_id,
            showCompleted=include_completed,
            showHidden=include_completed
        ).execute()
        
        for task in tasks.get('items', []):
            task_dict[task.get('title', 'No Title')] = {
                "id": task['id'],
                "status": task.get('status'),
                "completed": task.get('completed')  # Timestamp if task is completed
            }
    except Exception as e:
        print(f"Error listing tasks: {e}")
    
    return task_dict

def create_task(token_path, tasklist_id, task_title, task_notes=None, due_date=None):
    credentials = load_credentials(token_path)
    credentials = refresh_access_token(credentials, token_path)

    service = build('tasks', 'v1', credentials=credentials)

    print(f"Creating task: {task_title} in task list ID: {tasklist_id}")
    try:
        task = {"title": task_title, "notes": task_notes, "due": due_date}
        created_task = service.tasks().insert(tasklist=tasklist_id, body=task).execute()
        print(f"Task Created: {created_task['title']} (ID: {created_task['id']})")
    except Exception as e:
        print(f"Error creating task: {e}")

def get_task_details(token_path, tasklist_id, task_id):
    credentials = load_credentials(token_path)
    credentials = refresh_access_token(credentials, token_path)

    service = build('tasks', 'v1', credentials=credentials)

    print(f"Fetching task details for task ID: {task_id} in task list ID: {tasklist_id}")
    task_details = {}
    try:
        task = service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
        task_details = {
            "title": task.get("title", "No Title"),
            "notes": task.get("notes", ""),
            "due": task.get("due", ""),
            "status": task.get("status", ""),
            "completed": task.get("completed", ""),
            "updated": task.get("updated", ""),
        }
        print(f"Task details fetched: {task_details}")
    except Exception as e:
        print(f"Error fetching task details: {e}")
    
    return task_details

def delete_task(token_path, tasklist_id, task_id):
    credentials = load_credentials(token_path)
    credentials = refresh_access_token(credentials, token_path)

    service = build('tasks', 'v1', credentials=credentials)

    print(f"Deleting task ID: {task_id} from task list ID: {tasklist_id}")
    try:
        service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()
        print("Task deleted.")
    except Exception as e:
        print(f"Error deleting task: {e}")

def list_task_lists(token_path):
    # Load and refresh credentials
    credentials = load_credentials(token_path)
    credentials = refresh_access_token(credentials, token_path)
    print_token_ttl(credentials)

    # Initialize the Tasks API client
    service = build('tasks', 'v1', credentials=credentials)

    print("Listing all task lists...")
    tasklist_dict = {}
    try:
        tasklists = service.tasklists().list().execute()
        for tasklist in tasklists.get('items', []):
            tasklist_title = tasklist['title']
            tasklist_id = tasklist['id']
            tasklist_dict[tasklist_title] = tasklist_id
            print(f"Task List: {tasklist_title} (ID: {tasklist_id})")
    except Exception as e:
        print(f"Error accessing Google Task Lists API: {e}")
    
    return tasklist_dict

def create_task_list(token_path, task_list_name):
    # Load and refresh credentials
    credentials = load_credentials(token_path)
    credentials = refresh_access_token(credentials, token_path)

    # Initialize the Tasks API client
    service = build('tasks', 'v1', credentials=credentials)

    print(f"Creating task list: {task_list_name}")
    try:
        tasklist = {"title": task_list_name}
        created_tasklist = service.tasklists().insert(body=tasklist).execute()
        print(f"Task List Created: {created_tasklist['title']} (ID: {created_tasklist['id']})")
        return created_tasklist['id']
    except Exception as e:
        print(f"Error creating task list: {e}")

def mark_task_completed(token_path, tasklist_id, task_id):
    credentials = load_credentials(token_path)
    credentials = refresh_access_token(credentials, token_path)

    service = build('tasks', 'v1', credentials=credentials)

    print(f"Marking task ID: {task_id} as completed in task list ID: {tasklist_id}")
    try:
        updated_task = {"status": "completed"}
        service.tasks().patch(tasklist=tasklist_id, task=task_id, body=updated_task).execute()
        print(f"Task marked as completed.")
    except Exception as e:
        print(f"Error marking task as completed: {e}")