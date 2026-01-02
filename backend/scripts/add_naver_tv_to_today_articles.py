#!/usr/bin/env python3
"""
Add Naver TV URL to today's articles (2025-12-25)
Usage: python3 add_naver_tv_to_today_articles.py
"""
import boto3
import time
from typing import List, Dict
from datetime import datetime

NAVER_TV_URL = "https://tv.naver.com/v/91371573"
TABLE_NAME = "seodaily-eng-articles-dev"
REGION = "us-east-1"
TARGET_DATE = "2026-01-01"


def get_today_articles() -> List[Dict]:
    """Get articles published today"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(TABLE_NAME)

    articles = []
    last_key = None

    print(f"📥 Scanning articles from {TARGET_DATE}...")

    while True:
        if last_key:
            response = table.scan(ExclusiveStartKey=last_key)
        else:
            response = table.scan()

        for item in response.get('Items', []):
            # Check if published_at contains today's date
            published_at = item.get('published_at', '')
            if TARGET_DATE in published_at:
                articles.append(item)

        last_key = response.get('LastEvaluatedKey')

        if not last_key:
            break

    print(f"✅ Found {len(articles)} articles from {TARGET_DATE}")
    return articles


def update_article_with_video(news_id: str) -> bool:
    """Update single article with Naver TV URL"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
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
    print(f"🎬 Add Naver TV Video to Today's Articles ({TARGET_DATE})")
    print("=" * 80)
    print(f"Video URL: {NAVER_TV_URL}")
    print()

    # Get today's articles
    articles = get_today_articles()

    if not articles:
        print(f"❌ No articles found for {TARGET_DATE}")
        return

    # Show sample articles
    print()
    print("📰 Sample articles found:")
    for article in articles[:5]:
        print(f"   - {article.get('title_en', 'No title')[:60]}...")
    if len(articles) > 5:
        print(f"   ... and {len(articles) - 5} more")

    # Confirm
    print()
    print(f"⚠️  This will update {len(articles)} articles from {TARGET_DATE}")
    confirm = input(f"Continue? (yes/no): ")

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
            print(f"   ✅ [{i}/{len(articles)}] {news_id}")
        else:
            failed_count += 1

        # Rate limiting
        time.sleep(0.2)

    # Summary
    print()
    print("=" * 80)
    print("📊 Update Summary")
    print("=" * 80)
    print(f"📅 Date: {TARGET_DATE}")
    print(f"✅ Successfully updated: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📈 Success rate: {(success_count / len(articles) * 100):.1f}%")
    print()
    print(f"🎬 Video URL added: {NAVER_TV_URL}")
    print(f"✅ All {TARGET_DATE} articles now have the Naver TV video!")
    print()


if __name__ == "__main__":
    main()
