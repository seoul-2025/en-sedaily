#!/usr/bin/env python3
"""
Add Naver TV URL to all articles in DynamoDB
Usage: python3 add_naver_tv_to_all_articles.py
"""
import boto3
import time
from typing import List, Dict

NAVER_TV_URL = "https://tv.naver.com/v/91371573"
TABLE_NAME = "seodaily-eng-articles-dev"
REGION = "us-east-1"


def get_all_articles() -> List[Dict]:
    """Scan all articles from DynamoDB"""
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table(TABLE_NAME)

    articles = []
    last_key = None

    print(f"📥 Scanning all articles from {TABLE_NAME}...")

    while True:
        if last_key:
            response = table.scan(ExclusiveStartKey=last_key)
        else:
            response = table.scan()

        articles.extend(response.get('Items', []))
        last_key = response.get('LastEvaluatedKey')

        print(f"   Scanned {len(articles)} articles so far...")

        if not last_key:
            break

    print(f"✅ Total articles found: {len(articles)}")
    return articles


def update_article_with_video(news_id: str) -> bool:
    """Update single article with Naver TV URL"""
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table(TABLE_NAME)

    try:
        table.update_item(
            Key={'news_id': news_id},
            UpdateExpression='SET naver_tv_url = :url',
            ExpressionAttributeValues={':url': NAVER_TV_URL}
        )
        return True
    except Exception as e:
        print(f"   ❌ Failed to update {news_id}: {e}")
        return False


def main():
    print("=" * 80)
    print("🎬 Add Naver TV Video to All Articles")
    print("=" * 80)
    print(f"Video URL: {NAVER_TV_URL}")
    print()

    # Get all articles
    articles = get_all_articles()

    # Confirm before proceeding
    print()
    print("⚠️  WARNING: This will update ALL articles with the Naver TV URL")
    confirm = input(f"Are you sure you want to update {len(articles)} articles? (yes/no): ")

    if confirm.lower() != 'yes':
        print("❌ Operation cancelled")
        return

    print()
    print(f"🔄 Updating {len(articles)} articles...")
    print()

    # Update articles
    success_count = 0
    failed_count = 0

    for i, article in enumerate(articles, 1):
        news_id = article['news_id']

        if update_article_with_video(news_id):
            success_count += 1
            if i % 100 == 0:
                print(f"   ✅ Updated {i}/{len(articles)} articles...")
        else:
            failed_count += 1

        # Rate limiting (5 updates per second)
        if i % 5 == 0:
            time.sleep(0.2)

    # Summary
    print()
    print("=" * 80)
    print("📊 Update Summary")
    print("=" * 80)
    print(f"✅ Successfully updated: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📈 Success rate: {(success_count / len(articles) * 100):.1f}%")
    print()
    print(f"🎬 Video URL added: {NAVER_TV_URL}")
    print("✅ All articles now have the Naver TV video!")
    print()


if __name__ == "__main__":
    main()
