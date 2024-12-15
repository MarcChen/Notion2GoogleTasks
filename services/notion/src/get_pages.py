import requests
import os

# Replace with your Notion API key and database ID
NOTION_API_KEY = os.getenv("NOTION_API")
DATABASE_ID = os.getenv("DATABASE_ID")

# Notion API base URL
NOTION_URL = "https://api.notion.com/v1/databases/"

# Headers for the API request
HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"  # Use the latest Notion API version
}

def get_filtered_sorted_database(database_id):
    """
    Fetches the database information from Notion with specified filters and sorting.
    This function sends a POST request to the Notion API to query a database with the given
    database_id. The query includes filters to only include pages where the "Today" checkbox
    is checked and the "Status" is not "backlog", "abandoned", or "Done". The results are
    sorted by "Importance" in descending order and "Due Date" in ascending order.
    Args:
        database_id (str): The ID of the Notion database to query.
    Returns:
        dict: The JSON response from the Notion API if the request is successful.
        None: If the request fails, None is returned and an error message is printed.
    Note:
        You should tune the filters and sorting criteria depending on what pages/tasks
        of the database you'd like to sync with Google Tasks.
    """
    url = f"{NOTION_URL}{database_id}/query"
    
    # Query payload: Add filter and sorting 

    query_payload = {
    "filter": {
        "and": [
            {
                "property": "Today",
                "checkbox": {
                    "equals": True 
                }
            },
            {
                "and": [
                    {
                        "property": "Status",
                        "status": {
                            "does_not_equal": "backlog"
                        }
                    },
                    {
                        "property": "Status",
                        "status": {
                            "does_not_equal": "abandoned"
                        }
                    },
                    {
                        "property": "Status",
                        "status": {
                            "does_not_equal": "Done"
                        }
                    }
                ]
            }
        ]
    },
    "sorts": [
        {
            "property": "Importance",
            "direction": "descending"
        },
        {
            "property": "Due Date",
            "direction": "ascending"
        }
    ]
}

    
    # Send request to Notion API
    response = requests.post(url, headers=HEADERS, json=query_payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# Fetch and print the filtered and sorted database results
database_data = get_filtered_sorted_database(DATABASE_ID)
if database_data:
    print("Filtered and Sorted Database Content:")
    print(database_data)
