import pytest
from unittest.mock import patch, mock_open
from services.notion.src.notion_client import NotionClient
import json

# Sample data for mocking responses
MOCK_NOTION_RESPONSE = {
    "results": [
        {
            "id": "page_1",
            "properties": {
                "Tags": {"multi_select": [{"name": "Tag1"}]},
                "Importance": {"select": {"name": "High"}},
                "ID": {"unique_id": {"number": 123}},
                "Due Date": {"date": {"start": "2023-01-01"}},
                "Name": {"title": [{"text": {"content": "Task 1"}}]},
                "Text": {"rich_text": [{"text": {"content": "Some text"}}]},
                "URL": {"rich_text": [{"text": {"link": {"url": "http://example.com"}}}]},
                "Parent item": {"relation": [{"id": "parent_1"}]},
            },
            "url": "http://notion.so/page_1",
            "last_edited_time": "2023-01-01T12:00:00.000Z",
            "created_time": "2023-01-01T10:00:00.000Z",
        }
    ]
}

MOCK_PARENT_PAGE_RESPONSE = {
    "properties": {
        "Name": {"title": [{"text": {"content": "Parent Page"}}]}
    }
}

@pytest.fixture
def notion_client():
    """Fixture for initializing the NotionClient."""
    return NotionClient("fake_api_key", "fake_database_id", "/fake/project/root")

@patch("requests.post")
def test_get_filtered_sorted_database(mock_post, notion_client):
    """Test get_filtered_sorted_database method."""
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = MOCK_NOTION_RESPONSE

    with patch("builtins.open", mock_open(read_data=json.dumps({"filter": {}, "sort": []}))):
        response = notion_client.get_filtered_sorted_database()
    
    assert response is not None
    assert response["results"][0]["id"] == "page_1"

@patch("requests.get")
def test_fetch_parent_page_names(mock_get, notion_client):
    """Test fetch_parent_page_names method."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = MOCK_PARENT_PAGE_RESPONSE

    parent_names = notion_client.fetch_parent_page_names({"parent_1"})
    assert parent_names["parent_1"] == "Parent Page"

@patch("requests.patch")
def test_mark_page_as_completed(mock_patch, notion_client):
    """Test mark_page_as_completed method."""
    mock_patch.return_value.status_code = 200
    mock_patch.return_value.json.return_value = {"status": "success"}

    response = notion_client.mark_page_as_completed("page_1")
    assert response is not None
    assert response["status"] == "success"

def test_parse_notion_response(notion_client):
    """Test parse_notion_response method."""
    parsed_data = notion_client.parse_notion_response(MOCK_NOTION_RESPONSE)

    assert len(parsed_data) == 1
    assert parsed_data[0]["page_id"] == "page_1"
    assert parsed_data[0]["tags"] == "Tag1"
    assert parsed_data[0]["importance"] == "High"
    assert parsed_data[0]["title"] == "Task 1"
