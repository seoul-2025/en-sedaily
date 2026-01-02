"""
Update missing byline_en fields in DynamoDB
Adds translated byline_en for articles that don't have it
"""
import boto3
from utils.byline_translator import translate_byline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_missing_byline_en():
    """Update articles that are missing byline_en field"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('seodaily-eng-articles-dev')

    # Scan for articles without byline_en
    logger.info("Scanning for articles without byline_en...")

    updated_count = 0
    scanned_count = 0
    error_count = 0

    # Scan parameters
    scan_kwargs = {
        'FilterExpression': 'attribute_not_exists(byline_en)',
        'ProjectionExpression': 'news_id, byline'
    }

    done = False
    start_key = None

    while not done:
        if start_key:
            scan_kwargs['ExclusiveStartKey'] = start_key

        response = table.scan(**scan_kwargs)
        items = response.get('Items', [])
        scanned_count += len(items)

        logger.info(f"Found {len(items)} articles without byline_en in this batch")

        # Update each item
        for item in items:
            news_id = item.get('news_id')
            byline = item.get('byline', '')

            try:
                # Translate byline
                byline_en = translate_byline(byline) if byline else 'Seoul Economic Daily'

                # Update item
                table.update_item(
                    Key={'news_id': news_id},
                    UpdateExpression='SET byline_en = :byline_en',
                    ExpressionAttributeValues={
                        ':byline_en': byline_en
                    }
                )

                updated_count += 1
                logger.info(f"Updated {news_id}: '{byline}' → '{byline_en}'")

            except Exception as e:
                error_count += 1
                logger.error(f"Error updating {news_id}: {e}")

        # Check if there are more items to scan
        start_key = response.get('LastEvaluatedKey', None)
        done = start_key is None

    logger.info(f"""
    ========================================
    Update Complete!
    ========================================
    Scanned: {scanned_count} articles
    Updated: {updated_count} articles
    Errors: {error_count} articles
    """)

if __name__ == "__main__":
    update_missing_byline_en()
