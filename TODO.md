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

- fix last issues with last execution results : 

- age 'Lucas Video ' created successfully with 'Today' checkbox set to True!
- Created Notion page '802' from Google Task
- Page 'Blender Avancer' created successfully with 'Today' checkbox set to True!
- Created Notion page '803' from Google Task
- Page 'Pousser la V2 ' created successfully with 'Today' checkbox set to True!
- Created Notion page '804' from Google Task
- Page 'Update Google2Notion : Queue of Creds' created successfully with 'Today' checkbox set to True!
- Created Notion page '805' from Google Task
- Page 'Certification GitHub : Passage Exam' created successfully with 'Today' checkbox set to True!
- Created Notion page '806' from Google Task
- Page 'Renault Graduate ? ' created successfully with 'Today' checkbox set to True!
- Created Notion page '807' from Google Task
- Page 'Slide LLM' created successfully with 'Today' checkbox set to True!
- Created Notion page '808' from Google Task
- Page 'xgBOOST + randomforest' created successfully with 'Today' checkbox set to True!
- Created Notion page '809' from Google Task
- Page 'Climb up Facture' created successfully with 'Today' checkbox set to True!
- Created Notion page '810' from Google Task
- No Notion ID found in task 'Githubs Certification', skipping...
- No Notion ID found in task 'LLM finir le "projet"', skipping...
- No Notion ID found in task 'Installer Blender', skipping...
- No Notion ID found in task 'Remplir Metrics ', skipping...
- No Notion ID found in task 'Publier photo Volant', skipping...
- No Notion ID found in task 'LLM Avancer la présentation & report', skipping...
- No Notion ID found in task 'Fix VIE tracker docker image not pulling last update', skipping...
- No Notion ID found in task 'WildFire Plot les new metrics', skipping...
- No Notion ID found in task 'Rédiger l'intro et ma partie WildFIre', skipping...
- No Notion ID found in task 'Nettoyer DouDoune', skipping...
- No Notion ID found in task 'msg pierre', skipping...
- Error syncing statuses: 'list' object has no attribute 'items'
- SMS sent successfully.
- Page 'Final presentation  - Language Models and Structured Data  | (601)' created successfully with 'Today' checkbox set to True!
- Created Notion page '811' from Google Task
- Error fetching database: 400 Client Error: Bad Request for url: https://api.notion.com/v1/databases/2614254e32d14d5e9d9100b029fb31bb/query
- Failed to fetch database to find task ID 735
- Marked Notion page '735' as completed
- Error syncing statuses: 'list' object has no attribute 'items'
- SMS sent successfully.
- Page 'Integration Test Page - None | (796)' created successfully with 'Today' checkbox set to True!
- Created Notion page '812' from Google Task
- Page 'Integration Test Page - None | (797)' created successfully with 'Today' checkbox set to True!
- Created Notion page '813' from Google Task
- Page 'Integration Test Page - None | (798)' created successfully with 'Today' checkbox set to True!
- Created Notion page '814' from Google Task
- Page 'Integration Test Page - None | (799)' created successfully with 'Today' checkbox set to True!
- Created Notion page '815' from Google Task
- Page 'Integration Test Page - None | (800)' created successfully with 'Today' checkbox set to True!
- Created Notion page '816' from Google Task
- Error fetching database: 400 Client Error: Bad Request for url: https://api.notion.com/v1/databases/2614254e32d14d5e9d9100b029fb31bb/query
- Failed to fetch database to find task ID 685
- Marked Notion page '685' as completed
- Error syncing statuses: 'list' object has no attribute 'items'
- SMS sent successfully.
- Page 'VIE/Graduate Program !!! Offres post études   - None | (416)' created successfully with 'Today' checkbox set to True!
- Created Notion page '817' from Google Task
- Error syncing statuses: 'list' object has no attribute 'items'
- SMS sent successfully.

- Fix these 4 main issues : 
    - Being able to link a task to a subpage from notion (e.g Final presentation  - Language Models and Structured Data  | (601))
    - No notion ID found in task 
    - fix errors in batch quering : `Error syncing statuses: 'list' object has no attribute 'items'`
    - Issue with the following process :  
        - syncer.sync_pages_to_google_tasks() THEN syncer.sync_google_tasks_to_notion(last_successful_sync = last_successful_sync) 
        - Need to make sure 1st method only sync those that were not created by tasks otherwise, it'll be duplicated
        - THEN `sync_pages_to_google_tasks` should retrieve only `Tags != GoogleTask`
        - THEN `sync_google_tasks_to_notion` should push `Tags == GoogleTask`
    - Rich bar progress (and update their descriptions) for both **methods**  

---

### After Working functionalities : 

- [ ] Units test on newly created functions
- [ ] Delete TO-DO 
- [ ] Delete temp.sh -> include it to workflow CI
- [ ] Make a flake8, blake, isort 