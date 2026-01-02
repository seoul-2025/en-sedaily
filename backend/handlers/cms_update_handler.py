"""
CMS Update Handler
Direct DynamoDB update for CMS article editing
"""
import json
import logging
import os
from datetime import datetime
import boto3

# Import requests for revalidation
try:
    import requests
except ImportError:
    requests = None
    logging.warning("requests library not available - cache revalidation will be disabled")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('seodaily-eng-articles-dev')


def _trigger_revalidation(article: dict) -> None:
    """Trigger frontend cache revalidation after article update"""
    if not requests:
        logger.warning("requests library not available - skipping revalidation")
        return

    frontend_url = os.getenv('FRONTEND_URL', 'https://en.sedaily.com')
    revalidate_secret = os.getenv('REVALIDATE_SECRET')

    if not revalidate_secret:
        logger.warning("REVALIDATE_SECRET not configured - skipping revalidation")
        return

    try:
        response = requests.post(
            f"{frontend_url}/api/revalidate",
            headers={
                'x-revalidate-secret': revalidate_secret,
                'Content-Type': 'application/json'
            },
            json={
                'type': 'article',
                'category': article.get('category'),
                'slug': article.get('slug'),
                'publishedAt': article.get('published_at')
            },
            timeout=10
        )

        if response.ok:
            logger.info(f"Cache revalidation successful for article: {article.get('news_id')}")
            logger.info(f"Revalidated paths: {response.json().get('paths', [])}")
        else:
            logger.warning(f"Cache revalidation failed: {response.status_code} - {response.text}")
    except Exception as e:
        logger.warning(f"Cache revalidation error: {e}")


def lambda_handler(event, context):
    """Update article directly in DynamoDB"""
    
    try:
        body = json.loads(event['body'])
        news_id = body['news_id']
        updates = body['updates']
        
        # Build update expression
        update_expr = "SET updated_at = :updated_at"
        expr_values = {':updated_at': datetime.utcnow().isoformat()}
        
        # Add fields to update
        updatable = ['title_en', 'content_en', 'category', 'meta_description', 'keywords', 'hashtags', 'naver_tv_url']
        for field in updatable:
            if field in updates:
                update_expr += f", {field} = :{field}"
                expr_values[f':{field}'] = updates[field]
        
        # Update DynamoDB
        response = table.update_item(
            Key={'news_id': news_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_values,
            ReturnValues='ALL_NEW'
        )

        updated_item = response['Attributes']
        logger.info(f"✅ Updated article {news_id}")

        # Trigger frontend cache revalidation
        _trigger_revalidation(updated_item)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST,OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'message': 'Article updated successfully',
                'article': updated_item
            }, default=str)
        }
        
    except Exception as e:
        logger.error(f"❌ Update failed: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
