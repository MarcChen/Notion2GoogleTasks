import os
import pytest
from services.notion.src.notion_client import NotionClient

# Variable to store the ID of the created page for reuse
CREATED_PAGE_ID = None


@pytest.fixture
def notion_client():
    """Fixture for initializing the NotionClient."""
    notion_api_key = os.getenv("NOTION_API")
    database_id = os.getenv("DATABASE_ID")
    project_root = os.getenv("PROJECT_ROOT")
    assert (
        notion_api_key
    ), "NOTION_API environment variable is required for integration tests."
    assert (
        database_id
    ), "DATABASE_ID environment variable is required for integration tests."
    return NotionClient(notion_api_key, database_id, project_root)


def test_create_new_page_integration(notion_client):
    """Integration test for creating a new page."""
    global CREATED_TASK_ID
    title = "Integration Test Page"
    response = notion_client.create_new_page(title)

    assert response is not None, "Failed to create a new page."
    assert isinstance(response, int), "Response should return a unique task ID."
    CREATED_TASK_ID = response  # Store the task ID globally for subsequent tests
    print(f"Created page with Task ID: {CREATED_TASK_ID}")


def test_mark_page_as_completed_integration(notion_client):
    """Integration test for marking a page as completed."""
    global CREATED_TASK_ID
    assert (
        CREATED_TASK_ID is not None
    ), "No task ID available from test_create_new_page_integration."

    # Mark the page as completed
    response = notion_client.mark_page_as_completed(CREATED_TASK_ID)
    assert response is not None, "Failed to mark page as completed."
    assert (
        response.get("properties", {}).get("Status", {}).get("status", {}).get("name")
        == "Done"
    )
    print(f"Page with Task ID {CREATED_TASK_ID} marked as 'Done'.")


def test_fetch_parent_page_names_integration(notion_client):
    """Integration test for fetching parent page names."""
    # Use the valid parent page ID provided
    parent_page_ids = {"14d19fda9f9d80fa91c6e95f183ec94e"}
    response = notion_client.fetch_parent_page_names(parent_page_ids)
    assert response is not None, "Failed to fetch parent page names."
    assert isinstance(response, dict), "Response is not a dictionary."
    for page_id, name in response.items():
        print(f"Parent Page ID: {page_id}, Name: {name}")


def test_get_filtered_sorted_database_integration(notion_client):
    """Integration test for fetching filtered and sorted database entries."""
    response = notion_client.get_filtered_sorted_database()
    assert response is not None, "Failed to fetch database entries."
    assert "results" in response, "Response does not contain 'results' key."
    print(f"Fetched {len(response['results'])} entries from the database.")
