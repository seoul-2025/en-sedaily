"""
Admin Handler - CMS CRUD Operations
Handles article management for admin dashboard
"""
import logging
import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key, Attr

# Import requests for revalidation
try:
    import requests
except ImportError:
    requests = None
    logger.warning("requests library not available - cache revalidation will be disabled")

logger = logging.getLogger(__name__)
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


def list_articles(event: dict, context) -> dict:
    """List articles with pagination and filtering"""
    try:
        params = event.get('queryStringParameters') or {}
        page = int(params.get('page', 1))
        page_size = int(params.get('page_size', 20))
        category = params.get('category')
        status = params.get('status', 'all')  # Default to 'all' since status field doesn't exist in DB
        sort_order = params.get('sort_order', 'desc')  # 'asc' or 'desc'

        # Scan with filter - paginate through all items
        scan_kwargs = {}
        filter_expressions = []

        if status != 'all':
            filter_expressions.append(Attr('status').eq(status))
        if category:
            filter_expressions.append(Attr('category').eq(category))

        if filter_expressions:
            scan_kwargs['FilterExpression'] = filter_expressions[0]
            for expr in filter_expressions[1:]:
                scan_kwargs['FilterExpression'] &= expr

        # Paginate through all scan results
        items = []
        last_evaluated_key = None

        while True:
            if last_evaluated_key:
                scan_kwargs['ExclusiveStartKey'] = last_evaluated_key

            response = table.scan(**scan_kwargs)
            items.extend(response.get('Items', []))

            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break

        # Sort by published_at with order from query param
        items.sort(key=lambda x: x.get('published_at', ''), reverse=(sort_order == 'desc'))
        
        # Pagination
        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = items[start:end]
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'articles': paginated,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }, default=str)
        }
    except Exception as e:
        logger.error(f"List articles error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }


def get_article(event: dict, context) -> dict:
    """Get single article by ID"""
    try:
        article_id = event['pathParameters']['id']
        
        response = table.get_item(Key={'news_id': article_id})
        item = response.get('Item')
        
        if not item:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Article not found'})
            }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(item, default=str)
        }
    except Exception as e:
        logger.error(f"Get article error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }


def update_article(event: dict, context) -> dict:
    """Update article"""
    try:
        article_id = event['pathParameters']['id']
        body = json.loads(event['body'])
        
        # Get user from Cognito claims (if authenticated)
        user_id = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub', 'system')
        
        # Build update expression
        update_expr = "SET updated_at = :updated_at, updated_by = :updated_by"
        expr_values = {
            ':updated_at': datetime.now().isoformat(),
            ':updated_by': user_id
        }
        
        # Updatable fields
        updatable = ['title_en', 'content_en', 'category', 'status', 'meta_description', 'keywords', 'hashtags', 'byline']
        for field in updatable:
            if field in body:
                update_expr += f", {field} = :{field}"
                expr_values[f':{field}'] = body[field]
        
        response = table.update_item(
            Key={'news_id': article_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_values,
            ReturnValues='ALL_NEW'
        )

        updated_item = response['Attributes']

        # Trigger frontend cache revalidation
        _trigger_revalidation(updated_item)

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(updated_item, default=str)
        }
    except Exception as e:
        logger.error(f"Update article error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }


def delete_article(event: dict, context) -> dict:
    """Soft delete article (set status to deleted)"""
    try:
        article_id = event['pathParameters']['id']
        user_id = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub', 'system')
        
        table.update_item(
            Key={'news_id': article_id},
            UpdateExpression='SET #status = :status, updated_at = :updated_at, updated_by = :updated_by',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'deleted',
                ':updated_at': datetime.now().isoformat(),
                ':updated_by': user_id
            }
        )
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Article deleted successfully'})
        }
    except Exception as e:
        logger.error(f"Delete article error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }


def bulk_update(event: dict, context) -> dict:
    """Bulk update articles"""
    try:
        body = json.loads(event['body'])
        article_ids = body.get('article_ids', [])
        updates = body.get('updates', {})
        user_id = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub', 'system')
        
        updated_count = 0
        for article_id in article_ids:
            update_expr = "SET updated_at = :updated_at, updated_by = :updated_by"
            expr_values = {
                ':updated_at': datetime.now().isoformat(),
                ':updated_by': user_id
            }
            
            for field, value in updates.items():
                if field in ['category', 'status']:
                    update_expr += f", {field} = :{field}"
                    expr_values[f':{field}'] = value
            
            table.update_item(
                Key={'news_id': article_id},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_values
            )
            updated_count += 1
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': f'{updated_count} articles updated successfully'})
        }
    except Exception as e:
        logger.error(f"Bulk update error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }


def get_settings(event: dict, context) -> dict:
    """Get CMS settings (Naver TV URL, effective date, etc.)"""
    try:
        response = table.get_item(Key={'news_id': 'settings_config'})
        item = response.get('Item', {})

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'naver_tv_url': item.get('naver_tv_url', 'https://tv.naver.com/v/90963232?playlistNo=998605'),
                'effective_date': item.get('effective_date', datetime.now().strftime('%Y-%m-%d'))
            })
        }
    except Exception as e:
        logger.error(f"Get settings error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }


def save_settings(event: dict, context) -> dict:
    """Save CMS settings and update existing articles"""
    try:
        body = json.loads(event['body'])
        naver_tv_url = body.get('naver_tv_url', '')
        effective_date = body.get('effective_date', '')

        if not naver_tv_url or not effective_date:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'naver_tv_url and effective_date are required'})
            }

        # Save settings
        table.put_item(
            Item={
                'news_id': 'settings_config',
                'naver_tv_url': naver_tv_url,
                'effective_date': effective_date,
                'updated_at': datetime.now().isoformat()
            }
        )

        logger.info(f"Settings saved: {naver_tv_url} effective from {effective_date}")

        # Update existing articles published on or after effective_date
        updated_count = 0
        scan_kwargs = {
            'FilterExpression': Attr('published_at').gte(effective_date) & Attr('news_id').ne('settings_config')
        }

        while True:
            response = table.scan(**scan_kwargs)
            items = response.get('Items', [])

            for item in items:
                try:
                    table.update_item(
                        Key={'news_id': item['news_id']},
                        UpdateExpression='SET naver_tv_url = :url',
                        ExpressionAttributeValues={':url': naver_tv_url}
                    )
                    updated_count += 1
                except Exception as update_error:
                    logger.warning(f"Failed to update article {item['news_id']}: {update_error}")

            # Check if there are more items to scan
            if 'LastEvaluatedKey' not in response:
                break
            scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']

        logger.info(f"Updated {updated_count} existing articles with new Naver TV URL")

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'message': 'Settings saved successfully',
                'updated_articles': updated_count
            })
        }
    except Exception as e:
        logger.error(f"Save settings error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }


# Lambda handlers
def lambda_handler_list(event, context):
    return list_articles(event, context)

def lambda_handler_get(event, context):
    return get_article(event, context)

def lambda_handler_update(event, context):
    return update_article(event, context)

def lambda_handler_delete(event, context):
    return delete_article(event, context)

def lambda_handler_bulk(event, context):
    return bulk_update(event, context)

def lambda_handler_get_settings(event, context):
    return get_settings(event, context)

def lambda_handler_save_settings(event, context):
    return save_settings(event, context)
