import argparse
import os
from datetime import datetime
from typing import List, Optional

from services.sync_notion_google_task.main import NotionToGoogleTaskSyncer


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sync Notion pages to Google Tasks and vice versa."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Enable verbose logging (default: True). Use --no-verbose to disable.",
    )
    parser.add_argument(
        "--no-verbose",
        dest="verbose",
        action="store_false",
        help="Disable verbose logging to hide sensitive information.",
    )
    parser.add_argument(
        "--mode",
        choices=["full", "single"],
        default="full",
        help="Sync mode: 'full' for entire database or 'single' for a specific page. Automatically set to 'single' when --page-id is provided.",
    )
    parser.add_argument(
        "--page-id",
        type=int,
        help="ID of the Notion page to sync. When provided, automatically sets mode to 'single'.",
    )
    parser.add_argument(
        "--page-title",
        type=str,
        help="Title of the Notion page (optional, used with mode=single).",
    )
    parser.add_argument(
        "--skip-google-to-notion",
        action="store_true",
        help="Skip syncing Google Tasks to Notion (useful for webhook processing).",
    )

    args = parser.parse_args()

    # Auto-set mode to 'single' if page-id is provided
    if args.page_id is not None:
        args.mode = "single"

    # Validate arguments
    if args.mode == "single" and args.page_id is None:
        parser.error("--page-id is required when --mode=single")

    notion_api_key = os.getenv("NOTION_API")
    database_id = os.getenv("DATABASE_ID")
    token_path = os.getenv("TOKEN_PATH")
    project_root = os.getenv("PROJECT_ROOT")
    free_mobile_user_id = os.getenv("FREE_MOBILE_USER_ID")
    free_mobile_api_key = os.getenv("FREE_MOBILE_API_KEY")
    last_successful_sync = os.getenv("LAST_SUCCESSFUL_SYNC")

    assert notion_api_key, "NOTION_API environment variable is required."
    assert database_id, "DATABASE_ID environment variable is required."
    assert token_path, "TOKEN_PATH environment variable is required."
    assert project_root, "PROJECT_ROOT environment variable is required."
    
    # Last successful sync is optional when processing a single page
    if args.mode == "full":
        assert (
            last_successful_sync
        ), "LAST_SUCCESSFUL_SYNC environment variable is required for full sync mode."
        last_successful_sync = datetime.fromisoformat(last_successful_sync.replace("Z", ""))
    
    assert free_mobile_user_id, "FREE_MOBILE_USER_ID environment variable is required."
    assert free_mobile_api_key, "FREE_MOBILE_API_KEY environment variable is required."

    syncer = NotionToGoogleTaskSyncer(
        notion_api_key=notion_api_key,
        database_id=database_id,
        project_root=project_root,
        token_path=token_path,
        sms_user=free_mobile_user_id,
        sms_password=free_mobile_api_key,
        verbose=args.verbose,
    )

    if args.mode == "single":
        # Process a single page
        print(f"Processing single Notion page (ID: {args.page_id})")
        # Use a list with the specific page ID
        query_page_ids = [args.page_id]
        syncer.sync_pages_to_google_tasks(
            query_page_ids=query_page_ids,
        )
    else:
        # Full synchronization
        print("Processing full database synchronization")
        syncer.sync_pages_to_google_tasks(last_successful_sync=last_successful_sync)
        
        if not args.skip_google_to_notion:
            syncer.sync_google_tasks_to_notion(last_successful_sync=last_successful_sync)
