#!/usr/bin/env python3
"""
Revalidate all today's articles (2025-12-25)
Triggers frontend cache invalidation for all articles
"""
import boto3
import requests
import time
from typing import List, Dict

FRONTEND_URL = "https://en.sedaily.com"
REVALIDATE_SECRET = "d5aed293ec4993ad6b13a4033b3b73986b40206cd6d6f43018b3ec0f01bc2748"
TABLE_NAME = "seodaily-eng-articles-dev"
TARGET_DATE = "2026-01-01"


def get_today_articles() -> List[Dict]:
    """Get articles published today"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(TABLE_NAME)

    articles = []
    last_key = None

    print(f"📥 Fetching articles from {TARGET_DATE}...")

    while True:
        if last_key:
            response = table.scan(ExclusiveStartKey=last_key)
        else:
            response = table.scan()

        for item in response.get('Items', []):
            published_at = item.get('published_at', '')
            if TARGET_DATE in published_at:
                articles.append(item)

        last_key = response.get('LastEvaluatedKey')
        if not last_key:
            break

    print(f"✅ Found {len(articles)} articles")
    return articles


def trigger_revalidation(article: dict) -> bool:
    """Trigger cache revalidation for single article"""
    try:
        response = requests.post(
            f"{FRONTEND_URL}/api/revalidate",
            headers={
                'x-revalidate-secret': REVALIDATE_SECRET,
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

        return response.ok
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    print("=" * 80)
    print(f"🔄 Revalidate Today's Articles ({TARGET_DATE})")
    print("=" * 80)
    print()

    # Get articles
    articles = get_today_articles()

    if not articles:
        print(f"❌ No articles found for {TARGET_DATE}")
        return

    print()
    print(f"🔄 Revalidating {len(articles)} articles...")
    print()

    success_count = 0
    failed_count = 0

    for i, article in enumerate(articles, 1):
        news_id = article['news_id']
        title = article.get('title_en', 'No title')[:50]

        if trigger_revalidation(article):
            success_count += 1
            print(f"   ✅ [{i}/{len(articles)}] {title}...")
        else:
            failed_count += 1
            print(f"   ❌ [{i}/{len(articles)}] {title}...")

        # Rate limiting (2 requests per second)
        time.sleep(0.5)

    # Summary
    print()
    print("=" * 80)
    print("📊 Revalidation Summary")
    print("=" * 80)
    print(f"📅 Date: {TARGET_DATE}")
    print(f"✅ Successfully revalidated: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📈 Success rate: {(success_count / len(articles) * 100):.1f}%")
    print()
    print(f"🎬 All {TARGET_DATE} articles now show Naver TV video on frontend!")
    print()


if __name__ == "__main__":
    main()
