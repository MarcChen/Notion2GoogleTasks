import requests
import os
from rich import print
import json

# Replace with your Notion API key and database ID
NOTION_API_KEY = os.getenv("NOTION_API")
DATABASE_ID = os.getenv("DATABASE_ID")
PROJECT_ROOT = os.getenv("PROJECT_ROOT")

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
    with open(f"{PROJECT_ROOT}/services/notion/config/query_payload.json", 'r') as file: 
        query_payload = json.load(file)



    # Send request to Notion API
    response = requests.post(url, headers=HEADERS, json=query_payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def fetch_parent_page_names(parent_page_ids):
    """
    Fetches names of multiple parent pages in one batch to minimize API calls.

    Args:
        parent_page_ids (set): A set of unique parent page IDs (without hyphens).

    Returns:
        dict: A dictionary mapping parent page IDs to their names.
    """
    parent_page_names = {}
    for page_id in parent_page_ids:
        page_id = page_id.replace("-", "")  # Remove hyphens
        url = f"https://api.notion.com/v1/pages/{page_id}"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            # Extract the title from the page properties
            title_property = data.get("properties", {}).get("Name", {}).get("title", None)
            if title_property and len(title_property) > 0:
                parent_page_names[page_id] = title_property[0].get("text", {}).get("content", None)
            else:
                parent_page_names[page_id] = None
        else:
            print(f"Error fetching parent page {page_id}: {response.status_code}, {response.text}")
            parent_page_names[page_id] = None

    return parent_page_names

def mark_page_as_completed(page_id):
    """
    Marks the 'Status' property of a Notion page as 'Done'.
    
    Args:
        page_id (str): The ID of the Notion page to update.
    
    Returns:
        dict: The JSON response from the Notion API if successful.
        None: If the request fails, prints an error and returns None.
    """
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            "Status": {
                "status": {
                    "name": "Done"
                }
            }
        }
    }

    response = requests.patch(url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        print(f"Page {page_id} marked as 'Done' successfully!")
        return response.json()
    else:
        print(f"Error marking page {page_id} as 'Done': {response.status_code}, {response.text}")
        return None

def parse_notion_response(response):
    """
    Parse the Notion response to extract relevant fields, including parent page names.

    Args:
        response (dict): The JSON response from Notion API.

    Returns:
        list: A list of dictionaries containing extracted fields with None instead of [] or {}.
    """
    results = response.get('results', [])
    parsed_data = []

    # Parse each page
    for page in results:
        properties = page.get('properties', {})
        page_id = page.get('id', None).replace("-", "")

        # Extract required fields
        tag = properties.get('Tags', {}).get('multi_select', None)
        if tag and len(tag) > 0:
            tag = tag[0].get('name', None)
        else:
            tag = None

        # Safely handle 'select' for Importance
        importance_property = properties.get('Importance', {}).get('select', None)
        importance = importance_property.get('name', None) if importance_property else None

        unique_id = properties.get('ID', {}).get('unique_id', {}).get('number', None)

        # Safely handle 'Due Date' which may be None
        due_date_property = properties.get('Due Date', {}).get('date', None)
        due_date = due_date_property.get('start', None) if due_date_property else None

        page_url = page.get('url', None)

        # Safely handle 'select' for Estimates
        estimates_property = properties.get('Estimates', {}).get('select', None)
        estimates = estimates_property.get('name', None) if estimates_property else None

        title = properties.get('Name', {}).get('title', None)
        title_text = title[0]['text']['content'] if title and len(title) > 0 else None

        text_property = properties.get('Text', {}).get('rich_text', None)
        text_property = text_property[0].get('text', {}).get('content', None) if text_property and len(text_property) > 0 else None

        url_property = properties.get('URL', {}).get('rich_text', None)
        links = [
            text.get('text', {}).get('link', {}).get('url', None)
            for text in (url_property or [])
            if text.get('text', {}).get('link')
        ] if url_property else None
        links = links if links and len(links) > 0 else None

        laste_edited_time = page.get('last_edited_time', None)
        created_time = page.get('created_time', None)

        parent_page_id = properties.get('Parent item', {}).get('relation', None)
        if parent_page_id and len(parent_page_id) > 0:
            parent_page_id = parent_page_id[0].get('id', "").replace("-", "")
        else:
            parent_page_id = None

        # Append parsed data to the list
        parsed_data.append({
            "unique_id": unique_id,
            "page_id": page_id,
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

    # Collect unique parent page IDs
    parent_page_ids = {item['parent_page_id'] for item in parsed_data if item['parent_page_id']}
    parent_page_names = fetch_parent_page_names(parent_page_ids)

    # Add parent page names to the parsed data
    for item in parsed_data:
        if item['parent_page_id']:
            item['parent_page_name'] = parent_page_names.get(item['parent_page_id'], None)
        else:
            item['parent_page_name'] = None

    return parsed_data





# Fetch and print the filtered and sorted database results
database_data = get_filtered_sorted_database(DATABASE_ID)
if database_data:
    # print(database_data)
    parsed_data = parse_notion_response(database_data)
    # for item in parsed_data:
    #     print(item)
    # mark_page_as_completed("16319fda-9f9d-8052-8d9d-ecdf97ad3af2")
