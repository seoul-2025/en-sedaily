"""
CMS Delete Handler
Direct DynamoDB delete for CMS article deletion
"""
import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('seodaily-eng-articles-dev')


def lambda_handler(event, context):
    """Delete article directly from DynamoDB"""
    
    try:
        body = json.loads(event['body'])
        news_id = body['news_id']
        
        # Delete from DynamoDB
        table.delete_item(Key={'news_id': news_id})
        
        logger.info(f"✅ Deleted article {news_id}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST,OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({'message': 'Article deleted successfully'})
        }
        
    except Exception as e:
        logger.error(f"❌ Delete failed: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
