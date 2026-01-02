"""
Standalone script to fix missing slugs for Dec 23 articles
Does not require config.py
"""
import boto3
import re
from datetime import datetime

def generate_slug(title_en: str, max_length: int = 60) -> str:
    """Generate SEO-friendly slug from English title"""
    # Convert to lowercase
    slug = title_en.lower()

    # Remove special characters except spaces and hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)

    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)

    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)

    # Trim to max length at word boundary
    if len(slug) > max_length:
        slug = slug[:max_length]
        # Cut at last hyphen to avoid cutting words
        last_hyphen = slug.rfind('-')
        if last_hyphen > max_length * 0.7:  # Only if not cutting too much
            slug = slug[:last_hyphen]

    # Remove leading/trailing hyphens
    slug = slug.strip('-')

    return slug

def main():
    print("🔧 Starting slug fix for Dec 23, 2025 articles...")

    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('seodaily-eng-articles-dev')

    # Scan for Dec 23 articles (with pagination)
    print("📊 Scanning DynamoDB for articles from 2025-12-23...")

    articles = []
    response = table.scan(
        FilterExpression='begins_with(published_at, :date)',
        ExpressionAttributeValues={
            ':date': '2025-12-23'
        }
    )
    articles.extend(response['Items'])

    # Handle pagination
    while 'LastEvaluatedKey' in response:
        print(f"  📄 Fetching more items... (found {len(articles)} so far)")
        response = table.scan(
            FilterExpression='begins_with(published_at, :date)',
            ExpressionAttributeValues={
                ':date': '2025-12-23'
            },
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        articles.extend(response['Items'])
    total = len(articles)
    print(f"✅ Found {total} articles from Dec 23")

    updated = 0
    skipped = 0
    errors = 0

    for i, article in enumerate(articles, 1):
        news_id = article.get('news_id')
        current_slug = article.get('slug')
        title_en = article.get('title_en', '')

        print(f"\n[{i}/{total}] Processing {news_id}...")

        # Skip if already has slug
        if current_slug:
            print(f"  ⏭️  Already has slug: {current_slug}")
            skipped += 1
            continue

        # Skip if no English title
        if not title_en:
            print(f"  ⚠️  No English title, skipping")
            skipped += 1
            continue

        try:
            # Generate slug
            slug = generate_slug(title_en)

            # Check uniqueness by querying GSI
            existing = table.query(
                IndexName='slug-index',
                KeyConditionExpression='slug = :slug',
                ExpressionAttributeValues={
                    ':slug': slug
                }
            )

            # If slug exists, append date
            if existing.get('Items'):
                published_at = article.get('published_at', '')
                date_suffix = published_at[:10].replace('-', '')  # YYYYMMDD
                slug = f"{slug}-{date_suffix}"
                print(f"  🔄 Slug exists, using: {slug}")

            # Update DynamoDB
            table.update_item(
                Key={'news_id': news_id},
                UpdateExpression='SET slug = :slug',
                ExpressionAttributeValues={
                    ':slug': slug
                }
            )

            print(f"  ✅ Updated with slug: {slug}")
            updated += 1

        except Exception as e:
            print(f"  ❌ Error: {e}")
            errors += 1

    print("\n" + "="*70)
    print(f"📊 SUMMARY")
    print("="*70)
    print(f"Total articles:     {total}")
    print(f"✅ Updated:         {updated}")
    print(f"⏭️  Skipped:         {skipped}")
    print(f"❌ Errors:          {errors}")
    print("="*70)

    if updated > 0:
        print("\n🎉 Slugs have been generated! Please wait 1-2 minutes for CloudFront cache to clear.")
        print("   Then refresh the homepage: https://en.sedaily.com")

if __name__ == '__main__':
    main()
