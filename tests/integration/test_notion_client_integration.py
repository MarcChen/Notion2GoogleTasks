import os
from datetime import datetime

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
    """
    Integration test for fetching filtered and sorted database entries.

    This test validates:
    1. Basic database query functionality (no filters)
    2. Date-filtered query functionality using LAST_SUCCESSFUL_SYNC environment variable
    3. Proper response structure and data validation
    4. Logical consistency between filtered and unfiltered results
    """

    def _validate_database_response(response, context=""):
        """Helper function to validate database response structure."""
        assert response is not None, f"Database response is None {context}"
        assert isinstance(response, dict), f"Response is not a dictionary {context}"
        assert "results" in response, f"Response missing 'results' key {context}"
        assert isinstance(response["results"], list), f"Results is not a list {context}"
        return response["results"]

    def _parse_last_sync_timestamp(timestamp_str):
        """
        Parse last successful sync timestamp from environment variable.

        Args:
            timestamp_str: ISO timestamp string, optionally with 'Z' suffix

        Returns:
            datetime: Parsed datetime object

        Raises:
            ValueError: If timestamp format is invalid
        """
        if not timestamp_str:
            return None

        # Handle both ISO format with and without 'Z' suffix
        clean_timestamp = (
            timestamp_str.replace("Z", "+00:00")
            if timestamp_str.endswith("Z")
            else timestamp_str
        )

        try:
            return datetime.fromisoformat(clean_timestamp)
        except ValueError as e:
            raise ValueError(
                f"Invalid timestamp format: '{timestamp_str}'. "
                f"Expected ISO format (e.g., '2024-01-01T00:00:00' or '2024-01-01T00:00:00Z'). "
                f"Error: {e}"
            )

    # Phase 1: Test unfiltered database query
    print("🔍 Testing unfiltered database query...")
    unfiltered_response = notion_client.get_filtered_sorted_database()
    unfiltered_results = _validate_database_response(
        unfiltered_response, "(unfiltered)"
    )

    unfiltered_count = len(unfiltered_results)
    print(f"✅ Fetched {unfiltered_count} total entries from database")

    # Phase 2: Test date-filtered query if LAST_SUCCESSFUL_SYNC is provided
    last_sync_str = os.getenv("LAST_SUCCESSFUL_SYNC")

    if not last_sync_str:
        print("⚠️  LAST_SUCCESSFUL_SYNC environment variable not set")
        print("   To test date filtering, set LAST_SUCCESSFUL_SYNC to an ISO datetime")
        print("   Example: export LAST_SUCCESSFUL_SYNC='2024-01-01T00:00:00'")
        return

    print(f"🔍 Testing date-filtered query with timestamp: {last_sync_str}")

    try:
        last_successful_sync = _parse_last_sync_timestamp(last_sync_str)
        print(f"   Parsed timestamp: {last_successful_sync}")

        # Execute filtered query
        filtered_response = notion_client.get_filtered_sorted_database(
            last_successful_sync=last_successful_sync
        )
        filtered_results = _validate_database_response(filtered_response, "(filtered)")

        filtered_count = len(filtered_results)
        print(
            f"✅ Fetched {filtered_count} entries modified since {last_successful_sync}"
        )

        # Phase 3: Validate logical consistency
        assert filtered_count <= unfiltered_count, (
            f"Filtered results ({filtered_count}) should not exceed "
            f"unfiltered results ({unfiltered_count})"
        )

        # Calculate and report filtering effectiveness
        if unfiltered_count > 0:
            filter_ratio = (unfiltered_count - filtered_count) / unfiltered_count * 100
            print(f"📊 Filter efficiency: {filter_ratio:.1f}% of entries filtered out")

        # Phase 4: Validate that filtered results actually contain recent modifications
        if filtered_results:
            print("🔍 Validating filtered results contain recent modifications...")

            # Check if results have last_edited_time property
            sample_result = filtered_results[0]
            if "last_edited_time" in sample_result:
                last_edited = datetime.fromisoformat(
                    sample_result["last_edited_time"].replace("Z", "+00:00")
                )
                assert last_edited >= last_successful_sync, (
                    f"Filtered result has last_edited_time {last_edited} "
                    f"which is before filter timestamp {last_successful_sync}"
                )
                print(f"✅ Sample result last edited: {last_edited}")
            else:
                print("⚠️  Results don't contain last_edited_time property")

        print("🎉 Date filtering integration test completed successfully!")

    except ValueError as e:
        pytest.fail(f"Invalid LAST_SUCCESSFUL_SYNC format: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error during date filtering test: {e}")
