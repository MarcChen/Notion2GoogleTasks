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
NOTION_VERIFICATION_TOKEN_PARAMETER = os.environ['NOTION_VERIFICATION_TOKEN_PARAMETER']
BATCH_WINDOW_SECONDS = int(os.environ.get('BATCH_WINDOW_SECONDS', '60'))
PROJECT_NAME = os.environ.get('PROJECT_NAME', 'notion2googletasks')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'prod')
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
        
        logger.info(f"Processing webhook event: {event_id}, type: {event_type}")
        
        # Directly trigger GitHub Action
        logger.info("Triggering GitHub Action")
        trigger_github_action(event_id, event_type)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps({
                'message': 'Webhook processed successfully',
                'event_id': event_id,
                'event_type': event_type,
                'triggered': True
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }

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
        verification_token = get_parameter_value(NOTION_VERIFICATION_TOKEN_PARAMETER)
        
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

def trigger_github_action(event_id, event_type):
    """
    Trigger GitHub Action using repository dispatch
    """
    try:
        # Get GitHub token from Parameter Store
        github_token = get_parameter_value(GITHUB_PAT_PARAMETER_NAME)
        
        # Trigger workflow dispatch event
        url = (
            f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/"
            f"{GITHUB_REPO_NAME}/actions/workflows/sync_notion_to_google.yml/dispatches"
        )
        
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
        }
        
        payload = {
            'ref': 'main',
            'inputs': {
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'notion-webhook-lambda',
            'notion_event_id': event_id,
            'notion_event_type': event_type
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        logger.info(f"Successfully triggered GitHub Action: {response.status_code}")
        
    except Exception as e:
        logger.error(f"Error triggering GitHub Action: {str(e)}")
        raise
