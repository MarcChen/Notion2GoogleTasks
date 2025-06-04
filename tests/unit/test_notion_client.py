import json
from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

from services.notion.src.notion_client import NotionClient

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
                "URL": {
                    "rich_text": [
                        {"text": {"link": {"url": "http://example.com"}}}
                    ]
                },
                "Parent item": {"relation": [{"id": "parent_1"}]},
            },
            "url": "http://notion.so/page_1",
            "last_edited_time": "2023-01-01T12:00:00.000Z",
            "created_time": "2023-01-01T10:00:00.000Z",
        }
    ]
}

MOCK_PARENT_PAGE_RESPONSE = {
    "properties": {"Name": {"title": [{"text": {"content": "Parent Page"}}]}}
}


class TestNotionClient:
    def setup_method(self):
        """Initialize the NotionClient instance before each test."""
        self.notion_client = NotionClient(
            "fake_api_key", "fake_database_id", "/fake/project/root"
        )

    @patch("requests.post")
    def test_get_filtered_sorted_database(self, mock_post):
        """Test get_filtered_sorted_database method."""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = MOCK_NOTION_RESPONSE

        with patch(
            "builtins.open",
            mock_open(read_data=json.dumps({"filter": {}, "sort": []})),
        ):
            response = self.notion_client.get_filtered_sorted_database()

        assert response is not None
        assert response["results"][0]["id"] == "page_1"

    @patch("requests.post")
    def test_get_filtered_sorted_database_with_last_edited(self, mock_post):
        """Test get_filtered_sorted_database with last_edited_since filter."""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = MOCK_NOTION_RESPONSE

        with patch(
            "builtins.open",
            mock_open(read_data=json.dumps({"filter": {}, "sort": []})),
        ):
            ts = datetime(2023, 1, 1, 0, 0, 0)
            response = self.notion_client.get_filtered_sorted_database(
                last_edited_since=ts
            )

        assert response is not None
        sent_payload = mock_post.call_args.kwargs["json"]
        assert "filter" in sent_payload
        assert any(
            f.get("timestamp") == "last_edited_time" and
            f.get("last_edited_time", {}).get("on_or_after") == ts.isoformat()
            for f in sent_payload["filter"]["and"]
        )

    @patch("requests.get")
    def test_fetch_parent_page_names(self, mock_get):
        """Test fetch_parent_page_names method."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = MOCK_PARENT_PAGE_RESPONSE

        parent_names = self.notion_client.fetch_parent_page_names({"parent_1"})
        assert parent_names["parent_1"] == "Parent Page"

    @patch("requests.patch")
    @patch.object(
        NotionClient,
        "get_filtered_sorted_database",
        return_value=MOCK_NOTION_RESPONSE,
    )
    def test_mark_page_as_completed(
        self, mock_get_filtered_sorted_database, mock_patch
    ):
        """Test mark_page_as_completed method."""
        mock_patch.return_value.status_code = 200
        mock_patch.return_value.json.return_value = {"status": "success"}

        response = self.notion_client.mark_page_as_completed(123)
        assert response is not None
        assert response["status"] == "success"

    def test_parse_notion_response(self):
        """Test parse_notion_response method."""
        parsed_data = self.notion_client.parse_notion_response(
            MOCK_NOTION_RESPONSE
        )

        assert len(parsed_data) == 1
        assert parsed_data[0]["page_id"] == "page_1"
        assert parsed_data[0]["tags"] == "Tag1"
        assert parsed_data[0]["importance"] == "High"
        assert parsed_data[0]["title"] == "Task 1"

    @patch("requests.post")
    def test_get_filtered_sorted_database_file_not_found(self, mock_post):
        """Test get_filtered_sorted_database when payload file is missing."""
        mock_post.return_value.status_code = 200

        with patch("builtins.open", side_effect=FileNotFoundError):
            response = self.notion_client.get_filtered_sorted_database()
            assert response is None

    def test_parse_notion_response_with_missing_fields(self):
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
        parsed_data = self.notion_client.parse_notion_response(
            incomplete_response
        )

        assert len(parsed_data) == 1
        assert parsed_data[0]["tags"] is None
        assert parsed_data[0]["title"] == "Task 1"

    @patch("services.notion.src.notion_client.requests.patch")
    def test_mark_page_as_completed_failure(self, mock_patch):
        """Test mark_page_as_completed with a failed API call."""
        self.notion_client.get_filtered_sorted_database = MagicMock(
            return_value={
                "results": [
                    {
                        "properties": {"ID": {"unique_id": {"number": 456}}},
                        "id": "mock_page_id",
                    }
                ]
            }
        )

        mock_patch_response = MagicMock()
        mock_patch_response.status_code = 400
        mock_patch.return_value = mock_patch_response

        result = self.notion_client.mark_page_as_completed(task_id=123)

        assert result is None
        mock_patch.assert_called_once_with(
            "https://api.notion.com/v1/pages/mock_page_id",
            headers=self.notion_client.headers,
            json={"properties": {"Status": {"status": {"name": "Done"}}}},
        )

    @patch("services.notion.src.notion_client.requests.patch")
    def test_mark_page_as_completed_api_failure(self, mock_patch):
        """Test mark_page_as_completed with an API failure."""
        self.notion_client.get_filtered_sorted_database = MagicMock(
            return_value={
                "results": [
                    {
                        "properties": {"ID": {"unique_id": {"number": 123}}},
                        "id": "mock_page_id",
                    }
                ]
            }
        )

        mock_patch_response = MagicMock()
        mock_patch_response.status_code = 500
        mock_patch_response.text = "Internal Server Error"
        mock_patch.return_value = mock_patch_response

        result = self.notion_client.mark_page_as_completed(task_id=123)

        assert result is None
        mock_patch.assert_called_once_with(
            "https://api.notion.com/v1/pages/mock_page_id",
            headers=self.notion_client.headers,
            json={"properties": {"Status": {"status": {"name": "Done"}}}},
        )
