"""
Add AI Summary to recent 10 articles from today (2025-12-30)
"""
import asyncio
import logging
from datetime import datetime
from clients.dynamodb_client import DynamoDBClient
from clients.translation_service import TranslationService
from config import Settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def add_ai_summary_to_recent_articles():
    """Add AI Summary to recent 10 articles from today (2025-12-30)"""

    settings = Settings()
    dynamodb_client = DynamoDBClient(
        table_name=settings.dynamodb_table_articles,
        region=settings.aws_region
    )

    translation_service = TranslationService(
        model_id=settings.anthropic_model_id
    )

    try:
        logger.info(f"Fetching recent articles from 2025-12-30")

        # Scan DynamoDB for today's articles
        import boto3
        dynamodb = boto3.resource('dynamodb', region_name=settings.aws_region)
        table = dynamodb.Table(settings.dynamodb_table_articles)

        # Scan with filter
        response = table.scan(
            FilterExpression='begins_with(published_at, :date)',
            ExpressionAttributeValues={
                ':date': '2025-12-30'
            }
        )

        articles = response.get('Items', [])

        # Continue pagination if needed
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                FilterExpression='begins_with(published_at, :date)',
                ExpressionAttributeValues={
                    ':date': '2025-12-30'
                },
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            articles.extend(response.get('Items', []))

        logger.info(f"Total articles found: {len(articles)}")

        # Sort by published_at descending (most recent first)
        articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)

        # Take only first 10
        articles = articles[:10]
        logger.info(f"Processing most recent {len(articles)} articles")

        # Process each article
        success_count = 0
        skip_count = 0
        error_count = 0

        for i, article in enumerate(articles, 1):
            news_id = article.get('news_id')
            title_en = article.get('title_en')
            content_en = article.get('content_en')
            published_at = article.get('published_at')

            logger.info(f"\n{'='*60}")
            logger.info(f"[{i}/{len(articles)}] Processing: {news_id}")
            logger.info(f"  Published: {published_at}")
            logger.info(f"  Title: {title_en[:60]}..." if title_en else "  Title: N/A")

            # Skip if already has AI summary
            if article.get('ai_summary'):
                logger.info(f"  ⏭️  Already has AI summary, skipping")
                skip_count += 1
                continue

            # Skip if missing required fields
            if not title_en or not content_en:
                logger.warning(f"  ⚠️  Missing title or content, skipping")
                skip_count += 1
                continue

            try:
                # Generate AI Summary
                logger.info(f"  🤖 Generating AI summary...")
                summary_data = await translation_service.generate_ai_summary(
                    title=title_en,
                    content=content_en
                )

                ai_summary = summary_data.get('summary', '')
                ai_key_points = summary_data.get('key_points', [])

                logger.info(f"  ✓ Summary: {ai_summary[:120]}...")
                logger.info(f"  ✓ Key points ({len(ai_key_points)}):")
                for idx, point in enumerate(ai_key_points, 1):
                    logger.info(f"    {idx}. {point}")

                # Update DynamoDB
                table.update_item(
                    Key={'news_id': news_id},
                    UpdateExpression='SET ai_summary = :summary, ai_key_points = :points',
                    ExpressionAttributeValues={
                        ':summary': ai_summary,
                        ':points': ai_key_points
                    }
                )

                logger.info(f"  ✅ Successfully updated!")
                success_count += 1

                # Small delay to avoid rate limiting
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"  ❌ Failed to process {news_id}: {e}")
                error_count += 1
                continue

        # Final summary
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Processing complete!")
        logger.info(f"{'='*60}")
        logger.info(f"Total processed: {len(articles)}")
        logger.info(f"Successfully updated: {success_count}")
        logger.info(f"Skipped: {skip_count}")
        logger.info(f"Errors: {error_count}")
        logger.info(f"{'='*60}\n")

        if success_count > 0:
            logger.info(f"🎉 {success_count} articles now have AI summaries!")
            logger.info(f"You can test them at: https://en.sedaily.com")

    finally:
        await translation_service.close()

if __name__ == '__main__':
    asyncio.run(add_ai_summary_to_recent_articles())
