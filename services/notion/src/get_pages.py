import requests
import os
from rich import print
import json
from typing import Dict, List, Optional, Set

NOTION_API_KEY: str = os.getenv("NOTION_API")
DATABASE_ID: str = os.getenv("DATABASE_ID")
PROJECT_ROOT: str = os.getenv("PROJECT_ROOT")

NOTION_URL = "https://api.notion.com/v1/databases/"

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_filtered_sorted_database(database_id: str) -> Optional[Dict]:
    """
    Fetches the database information from Notion with specified filters and sorting.

    Args:
        database_id (str): The ID of the Notion database to query.

    Returns:
        Optional[Dict]: The JSON response from the Notion API if the request is successful; None otherwise.
    """
    url = f"{NOTION_URL}{database_id}/query"
    
    try:
        with open(f"{PROJECT_ROOT}/services/notion/config/query_payload.json", 'r') as file: 
            query_payload = json.load(file)

        response = requests.post(url, headers=HEADERS, json=query_payload)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching database: {e}")
        return None
    except FileNotFoundError as e:
        print(f"Error loading query payload: {e}")
        return None

def fetch_parent_page_names(parent_page_ids: Set[str]) -> Dict[str, Optional[str]]:
    """
    Fetches names of multiple parent pages in one batch to minimize API calls.

    Args:
        parent_page_ids (Set[str]): A set of unique parent page IDs (without hyphens).

    Returns:
        Dict[str, Optional[str]]: A dictionary mapping parent page IDs to their names.
    """
    parent_page_names: Dict[str, Optional[str]] = {}
    for page_id in parent_page_ids:
        page_id = page_id.replace("-", "")  # Remove hyphens
        url = f"https://api.notion.com/v1/pages/{page_id}"

        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            
            title_property = data.get("properties", {}).get("Name", {}).get("title", None)
            if title_property and len(title_property) > 0:
                parent_page_names[page_id] = title_property[0].get("text", {}).get("content", None)
            else:
                parent_page_names[page_id] = None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching parent page {page_id}: {e}")
            parent_page_names[page_id] = None

    return parent_page_names

def mark_page_as_completed(page_id: str) -> Optional[Dict]:
    """
    Marks the 'Status' property of a Notion page as 'Done'.

    Args:
        page_id (str): The ID of the Notion page to update.

    Returns:
        Optional[Dict]: The JSON response from the Notion API if successful; None otherwise.
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

    try:
        response = requests.patch(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        print(f"Page {page_id} marked as 'Done' successfully!")
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error marking page {page_id} as 'Done': {e}")
        return None

def parse_notion_response(response: Dict) -> List[Dict]:
    """
    Parse the Notion response to extract relevant fields, including parent page names.

    Args:
        response (Dict): The JSON response from Notion API.

    Returns:
        List[Dict]: A list of dictionaries containing extracted fields with None instead of [] or {}.
    """
    try:
        results = response.get('results', [])
        parsed_data: List[Dict] = []

        for page in results:
            properties = page.get('properties', {})
            page_id = page.get('id', None).replace("-", "")

            tag = properties.get('Tags', {}).get('multi_select', None)
            if tag and len(tag) > 0:
                tag = tag[0].get('name', None)
            else:
                tag = None

            importance_property = properties.get('Importance', {}).get('select', None)
            importance = importance_property.get('name', None) if importance_property else None

            unique_id = properties.get('ID', {}).get('unique_id', {}).get('number', None)

            due_date_property = properties.get('Due Date', {}).get('date', None)
            due_date = due_date_property.get('start', None) if due_date_property else None

            page_url = page.get('url', None)

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

        parent_page_ids: Set[str] = {item['parent_page_id'] for item in parsed_data if item['parent_page_id']}
        parent_page_names = fetch_parent_page_names(parent_page_ids)

        for item in parsed_data:
            if item['parent_page_id']:
                item['parent_page_name'] = parent_page_names.get(item['parent_page_id'], None)
            else:
                item['parent_page_name'] = None

        return parsed_data

    except KeyError as e:
        print(f"Error parsing Notion response: Missing key {e}")
        return []
    except Exception as e:
        print(f"Unexpected error while parsing Notion response: {e}")
        return []

database_data = get_filtered_sorted_database(DATABASE_ID)
if database_data:
    parsed_data = parse_notion_response(database_data)
    for item in parsed_data:
        print(item)