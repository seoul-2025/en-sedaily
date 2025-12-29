"""
CMS Update Handler
Direct DynamoDB update for CMS article editing
"""
import json
import logging
from datetime import datetime
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('seodaily-eng-articles-dev')


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
        
        logger.info(f"✅ Updated article {news_id}")
        
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
                'article': response['Attributes']
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
