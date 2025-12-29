"""
Fix missing slugs for today's articles (Dec 23, 2025)
"""
import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clients.dynamodb_client import DynamoDBClient
from utils.slug_generator import generate_slug, ensure_unique_slug
from config import settings

async def fix_today_slugs():
    """Fix missing slugs for today's articles"""

    dynamodb_client = DynamoDBClient(
        table_name="seodaily-eng-articles-dev",
        region=settings.region
    )

    print("🔍 Scanning for articles from 2025-12-23...")

    # Scan for today's articles
    response = dynamodb_client.table.scan(
        FilterExpression='begins_with(published_at, :date)',
        ExpressionAttributeValues={
            ':date': '2025-12-23'
        }
    )

    articles = response.get('Items', [])
    print(f"✅ Found {len(articles)} articles from today")

    updated = 0
    skipped = 0
    errors = 0

    for article in articles:
        news_id = article.get('news_id')
        current_slug = article.get('slug')

        # Skip if slug already exists
        if current_slug:
            print(f"⏭️  Skipping {news_id} (already has slug: {current_slug})")
            skipped += 1
            continue

        try:
            # Generate slug
            title_en = article.get('title_en', '')
            published_at = article.get('published_at', '')
            category = article.get('category', 'news')

            if not title_en:
                print(f"⚠️  Skipping {news_id} (no English title)")
                skipped += 1
                continue

            slug = generate_slug(
                title_en=title_en,
                published_at=published_at,
                category=category
            )

            # Ensure uniqueness
            slug = await ensure_unique_slug(
                slug=slug,
                published_at=published_at,
                dynamodb_client=dynamodb_client
            )

            # Update DynamoDB
            dynamodb_client.table.update_item(
                Key={'news_id': news_id},
                UpdateExpression='SET slug = :slug',
                ExpressionAttributeValues={
                    ':slug': slug
                }
            )

            print(f"✅ Updated {news_id} with slug: {slug}")
            updated += 1

        except Exception as e:
            print(f"❌ Error updating {news_id}: {e}")
            errors += 1

    print("\n" + "="*60)
    print(f"📊 Summary:")
    print(f"  Total articles: {len(articles)}")
    print(f"  Updated: {updated}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors: {errors}")
    print("="*60)

if __name__ == '__main__':
    asyncio.run(fix_today_slugs())
