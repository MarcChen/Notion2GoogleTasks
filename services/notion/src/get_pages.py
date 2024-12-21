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

def parse_notion_response(response):
    """
    Parse the Notion response to extract relevant fields.

    Args:
        response (dict): The JSON response from Notion API.

    Returns:
        list: A list of dictionaries containing extracted fields.
    """
    results = response.get('results', [])
    parsed_data = []

    for page in results:
        properties = page.get('properties', {})
        
        # Extract required fields
        tag = properties.get('Tags', {}).get('multi_select', [])
        if tag != []:
            tag = tag[0].get('name')
        
        importance = properties.get('Importance', {}).get('select', {}).get('name', None)
        unique_id = properties.get('ID', {}).get('unique_id', {}).get('number', None)
        
        # Safely handle 'Due Date' which may be None
        due_date_property = properties.get('Due Date', {}).get('date')
        due_date = due_date_property.get('start', None) if due_date_property else None
        
        page_url = page.get('url', None)
        estimates = properties.get('Estimates', {}).get('select', {}).get('name', None)
        title = properties.get('Name', {}).get('title', [])
        title_text = title[0]['text']['content'] if title else None
        
        text_property = properties.get('Text', {}).get('rich_text', [])
        if text_property != []:
            text_property = text_property[0].get('text', None).get('content', None)

        url_property = properties.get('URL', {}).get('rich_text', [])
        links = [
            text.get('text', {}).get('link', {}).get('url')
            for text in url_property
            if text.get('text', {}).get('link')
        ]


        laste_edited_time = page.get('last_edited_time', None)
        created_time = page.get('created_time', None)

        parent_page_id = properties.get('Parent item', {}).get('relation', [])
        if parent_page_id != []:
            parent_page_id = parent_page_id[0].get('id')

        # Append parsed data to the list
        parsed_data.append({
            "unique_id": unique_id,
            "title": title_text,
            "created_time": created_time,
            "last_edited_time": laste_edited_time,
            "estimates": estimates,
            "importance": importance,
            "tags": tag,
            "due_date": due_date,
            "page_url": page_url,
            "text": text_property,
            "url": links,
            "parent_page_id": parent_page_id
        })

    return parsed_data


# Fetch and print the filtered and sorted database results
database_data = get_filtered_sorted_database(DATABASE_ID)
if database_data:
    print("Filtered and Sorted Database Content:")
    # print(database_data)
    parsed_data = parse_notion_response(database_data)
    for item in parsed_data:
        print(item)

