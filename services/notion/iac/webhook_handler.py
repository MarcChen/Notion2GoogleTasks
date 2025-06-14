import json
import boto3
import os
import hmac
import hashlib
import logging
import requests
from datetime import datetime, timedelta
import time
import uuid
import glob
import tempfile

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
ssm = boto3.client('ssm')
events = boto3.client('events')
lambda_client = boto3.client('lambda')

# Environment variables
GITHUB_REPO_OWNER = os.environ['GITHUB_REPO_OWNER']
GITHUB_REPO_NAME = os.environ['GITHUB_REPO_NAME']
GITHUB_PAT_PARAMETER_NAME = os.environ['GITHUB_PAT_PARAMETER_NAME']
NOTION_VERIFICATION_TOKEN_PARAMETER = os.environ[
    'NOTION_VERIFICATION_TOKEN_PARAMETER'
]
PROJECT_NAME = os.environ.get('PROJECT_NAME', 'notion2googletasks')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'prod')

# Configurable parameters for GitHub workflow
GITHUB_WORKFLOW_FILE = os.environ.get(
    'GITHUB_WORKFLOW_FILE', 'sync_notion_page_webhook.yml'
)
GITHUB_TARGET_BRANCH = os.environ.get('GITHUB_TARGET_BRANCH', 'main')

# Optional Notion API for page title retrieval
NOTION_API_KEY_PARAMETER = os.environ.get('NOTION_API_KEY_PARAMETER', None)

BATCH_EVENTS_DIR = '/tmp/batch_events'


def lambda_handler(event, context):
    """
    Main Lambda handler for Notion webhooks
    """
    logger.info(f"Received event: {json.dumps(event, default=str)}")

    try:
        # Parse the incoming webhook
        body = json.loads(event.get('body', '{}'))
        headers = event.get('headers', {})

        # Handle webhook verification (initial subscription)
        if 'verification_token' in body:
            logger.info("Received webhook verification request")
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({
                    'message': 'Webhook verification received',
                    'verification_token': body['verification_token']
                })
            }

        # Verify webhook signature for regular events
        if not verify_notion_signature(
            event.get('body', ''),
            headers.get('X-Notion-Signature', '')
        ):
            logger.warning("Invalid webhook signature")
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid signature'})
            }

        # Process the webhook event
        event_id = body.get('id', 'unknown')
        event_type = body.get('type', 'unknown')

        # Extract page information from webhook
        page_info = extract_page_info_from_webhook(body)
        page_id = page_info.get('page_id')
        page_title = page_info.get('page_title')

        logger.info(f"Processing webhook event: {event_id}, type: {event_type}")
        logger.info(f"Page ID: {page_id}, Page Title: {page_title}")

        # Only trigger GitHub Action if we have a page ID and it's a page event
        if page_id and should_trigger_sync(event_type):
            logger.info("Triggering GitHub Action")
            trigger_github_action(page_id, page_title, event_id, event_type)
        else:
            logger.info(
                f"Skipping GitHub Action trigger - "
                f"Page ID: {page_id}, Event type: {event_type}"
            )

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps({
                'message': 'Webhook processed successfully',
                'event_id': event_id,
                'event_type': event_type,
                'page_id': page_id,
                'page_title': page_title,
                'triggered': page_id is not None and should_trigger_sync(event_type)
            })
        }

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }


def should_trigger_sync(event_type):
    """
    Determine if the event type should trigger a sync
    
    Args:
        event_type (str): The Notion webhook event type
        
    Returns:
        bool: True if sync should be triggered
    """
    # Events that should trigger a sync to Google Tasks
    sync_events = {
        'page.created',
        'page.properties_updated',
        'page.content_updated',
        'page.undeleted',
        'database.content_updated'  # When pages are added/updated in database
    }
    
    return event_type in sync_events


def extract_page_info_from_webhook(body):
    """
    Extract page ID and title from Notion webhook payload
    
    Args:
        body (dict): The webhook body from Notion
        
    Returns:
        dict: Dictionary containing page_id and page_title
    """
    page_info = {'page_id': None, 'page_title': None}

    try:
        event_type = body.get('type', '')
        entity = body.get('entity', {})
        data = body.get('data', {})

        # Handle page events
        if entity.get('type') == 'page':
            page_id = entity.get('id', '').replace('-', '')
            if page_id:
                page_info['page_id'] = page_id
                # Fetch title from Notion API since it's not in webhook
                page_info['page_title'] = fetch_page_title_from_notion(page_id)

        # Handle database content updates (pages added/updated in database)
        elif (entity.get('type') == 'database' and 
              event_type == 'database.content_updated'):
            # Extract page IDs from updated_blocks if they represent pages
            updated_blocks = data.get('updated_blocks', [])
            for block in updated_blocks:
                if block.get('type') == 'block':
                    # This could be a page within the database
                    block_id = block.get('id', '').replace('-', '')
                    if block_id:
                        # Try to determine if this block is actually a page
                        # For now, we'll use the first block as the page ID
                        if not page_info['page_id']:
                            page_info['page_id'] = block_id
                            page_info['page_title'] = (
                                fetch_page_title_from_notion(block_id)
                            )

        # Handle comment events that contain page_id
        elif entity.get('type') == 'comment' and 'page_id' in data:
            page_id = data.get('page_id', '').replace('-', '')
            if page_id:
                page_info['page_id'] = page_id
                page_info['page_title'] = fetch_page_title_from_notion(page_id)

        logger.info(f"Extracted page info: {page_info}")

    except Exception as e:
        logger.error(f"Error extracting page info from webhook: {str(e)}")

    return page_info


def fetch_page_title_from_notion(page_id):
    """
    Fetch page title from Notion API
    
    Args:
        page_id (str): The Notion page ID
        
    Returns:
        str: The page title or None if unable to fetch
    """
    if not NOTION_API_KEY_PARAMETER:
        logger.info(
            "No Notion API key parameter configured, cannot fetch page title"
        )
        return None

    try:
        # Get Notion API key from Parameter Store
        notion_api_key = get_parameter_value(NOTION_API_KEY_PARAMETER)

        # Fetch page details from Notion API
        url = f"https://api.notion.com/v1/pages/{page_id}"
        headers = {
            'Authorization': f'Bearer {notion_api_key}',
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json',
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Extract title from page properties
        properties = data.get('properties', {})
        
        # Try common title property names
        for title_key in ['Name', 'Title', 'title']:
            title_property = properties.get(title_key, {}).get('title', [])
            if title_property and len(title_property) > 0:
                return title_property[0].get('text', {}).get('content', '')

        # If no title property found, try to get it from the page object
        # For database pages, the title might be in a different structure
        if 'parent' in data and data['parent'].get('type') == 'database_id':
            # This is a database page, title extraction is more complex
            # For now, return a generic title
            return f"Database Page {page_id[:8]}"

        logger.warning(f"No title found for page {page_id}")
        return None

    except Exception as e:
        logger.error(f"Error fetching page title from Notion API: {str(e)}")
        return None


def verify_notion_signature(body, signature):
    """
    Verify the Notion webhook signature using the verification token
    Based on Notion's webhook documentation
    """
    if not signature:
        logger.warning("No signature provided, skipping verification")
        return True  # Skip verification if no signature

    try:
        # Get verification token from Parameter Store
        verification_token = get_parameter_value(
            NOTION_VERIFICATION_TOKEN_PARAMETER
        )

        # Calculate the expected signature
        body_json = json.dumps(json.loads(body), separators=(",", ":"))
        hmac_obj = hmac.new(
            verification_token.encode('utf-8'),
            body_json.encode('utf-8'),
            hashlib.sha256
        )
        expected_signature = "sha256=" + hmac_obj.hexdigest()

        # Use timing-safe comparison
        return hmac.compare_digest(expected_signature, signature)

    except Exception as e:
        logger.error(f"Error verifying signature: {str(e)}")
        return False


def get_parameter_value(parameter_name):
    """
    Retrieve parameter value from AWS Systems Manager Parameter Store
    """
    try:
        response = ssm.get_parameter(
            Name=parameter_name,
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except Exception as e:
        logger.error(f"Error retrieving parameter {parameter_name}: {str(e)}")
        raise


def trigger_github_action(page_id, page_title, event_id, event_type):
    """
    Trigger GitHub Action using repository dispatch
    """
    try:
        # Get GitHub token from Parameter Store
        github_token = get_parameter_value(GITHUB_PAT_PARAMETER_NAME)

        # Trigger workflow dispatch event
        url = (
            f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/"
            f"{GITHUB_REPO_NAME}/actions/workflows/{GITHUB_WORKFLOW_FILE}/"
            f"dispatches"
        )

        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
        }

        payload = {
            'ref': GITHUB_TARGET_BRANCH,
            'inputs': {
                'page_id': str(page_id),
                'page_title': page_title or f'Page {page_id[:8]}',
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        logger.info(f"Successfully triggered GitHub Action: {response.status_code}")
        logger.info(
            f"Workflow: {GITHUB_WORKFLOW_FILE}, Branch: {GITHUB_TARGET_BRANCH}"
        )
        logger.info(f"Inputs: page_id={page_id}, page_title={page_title}")

    except Exception as e:
        logger.error(f"Error triggering GitHub Action: {str(e)}")
        raise
