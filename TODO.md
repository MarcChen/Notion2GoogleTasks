# TODO List for V2 Version

## Overview
This TODO list outlines the tasks required to achieve the V2 version of the Notion2GoogleTasks project.

## Tasks

### 1. Upcoming in v2.0
- **Two-Way Sync**:
    - Implement functionality to upload new tasks from Google Tasks to Notion.
    - Ensure task status changes are synchronized between Notion and Google Tasks.
    - Test synchronization thoroughly to handle edge cases and conflicts.
    - Update documentation to reflect new synchronization features.


TO-DO 
- Pooling system to see if Task have new marked task 
    - otherwise mark the page on notion as done 


- Creating a new task will create a page on Notion
- PAT For private repositories: ACCESS : repo / workflow   
    - In order to retrieve last succesfull run


- Units test 
    - create_new_page
    - get_created_tasks_since
    - modify_task_title
    - get_completed_tasks_since

- Test : function `sync_google_tasks_to_notion`
    - If Google Task is Done then Mark Page as Done 
    - If Page marked as Done and still exist in Google Task, terminate it 
    - Add Rich Progress bar

- Delete TO-DO 
- Delete temp.sh -> include it to workflow CI

- Google To Notion : If Notion is marked as Done, need to mark Google Task as Done 
    - Retrieve current Google Task IDs, check if in the IDs if status is Done in Notion


- delete `parse_notion_response` in `noton_client.py` : group it all under the same function to retrieve database
    - Redo `get_filtered_sorted_database` test 
        - now it should handle basic filtered body or search for task ids  
        - Retrieve directly parsed response
    - Write the new test and clean unused functions 

- Impelment this in `sync_google_tasks_to_notion` : 
```
# Get task list ID
    task_lists = manager.list_task_lists()
    for tasklist_name, tasklist_id in task_lists.items():
        # Get completed tasks since last check
        tasks = manager.list_tasks_in_tasklist(tasklist_id)
        tasks_ids =[]
        for task in tasks:
            task_id = task['id']
            print(f"Task ID: {task_id}")
            tasks_ids.append(task_id)    
        # Check if task is marked as done in Notion
        pages_status = notion_client.retrieve_pages_status(tasks_ids)
        for page_id, page_status in pages_status.items():
            if page_status == "Done":
                manager.mark_task_as_done(tasklist_id, page_id)

```

- Make mermaid flowchart to explain all the sync that the tool is doing 
