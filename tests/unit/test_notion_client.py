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


class TestNotionClient:
    @patch("requests.post")
    def test_get_filtered_sorted_database(self, mock_post, notion_client):
        """Test get_filtered_sorted_database method."""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = MOCK_NOTION_RESPONSE

        with patch("builtins.open", mock_open(read_data=json.dumps({"filter": {}, "sort": []}))):
            response = notion_client.get_filtered_sorted_database()
        
        assert response is not None
        assert response["results"][0]["id"] == "page_1"

    @patch("requests.get")
    def test_fetch_parent_page_names(self, mock_get, notion_client):
        """Test fetch_parent_page_names method."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = MOCK_PARENT_PAGE_RESPONSE

        parent_names = notion_client.fetch_parent_page_names({"parent_1"})
        assert parent_names["parent_1"] == "Parent Page"

    @patch("requests.patch")
    @patch.object(NotionClient, 'get_filtered_sorted_database', return_value=MOCK_NOTION_RESPONSE)
    def test_mark_page_as_completed(self, mock_get_filtered_sorted_database, mock_patch, notion_client):
        """Test mark_page_as_completed method."""
        mock_patch.return_value.status_code = 200
        mock_patch.return_value.json.return_value = {"status": "success"}

        response = notion_client.mark_page_as_completed(123)  # Updated to use task_id
        assert response is not None
        assert response["status"] == "success"

    def test_parse_notion_response(self, notion_client):
        """Test parse_notion_response method."""
        parsed_data = notion_client.parse_notion_response(MOCK_NOTION_RESPONSE)

        assert len(parsed_data) == 1
        assert parsed_data[0]["page_id"] == "page_1"
        assert parsed_data[0]["tags"] == "Tag1"
        assert parsed_data[0]["importance"] == "High"
        assert parsed_data[0]["title"] == "Task 1"

    # Extended Tests
    @patch("requests.post")
    def test_get_filtered_sorted_database_file_not_found(self, mock_post, notion_client):
        """Test get_filtered_sorted_database when payload file is missing."""
        mock_post.return_value.status_code = 200

        with patch("builtins.open", side_effect=FileNotFoundError):
            response = notion_client.get_filtered_sorted_database()
            assert response is None

    def test_parse_notion_response_with_missing_fields(self, notion_client):
        """Test parse_notion_response with missing fields."""
        incomplete_response = {
            "results": [
                {
                    "id": "page_1",
                    "properties": {
                        "Name": {"title": [{"text": {"content": "Task 1"}}]},
                        "Tags": {},  # Missing multi_select
                    },
                    "url": "http://notion.so/page_1",
                }
            ]
        }
        parsed_data = notion_client.parse_notion_response(incomplete_response)

        assert len(parsed_data) == 1
        assert parsed_data[0]["tags"] is None  # Should handle missing gracefully
        assert parsed_data[0]["title"] == "Task 1"

    @patch("services.notion.src.notion_client.requests.patch")
    def test_mark_page_as_completed_failure(self, mock_patch, notion_client):
        """Test mark_page_as_completed with a failed API call."""
        # Mock a failed response
        mock_patch.return_value.status_code = 400
        mock_patch.return_value.json.return_value = {"message": "Invalid request"}

        # Call the method
        response = notion_client.mark_page_as_completed("page_1")

        # Assert the method handles failure correctly
        assert response is None  # Should return None on failure
