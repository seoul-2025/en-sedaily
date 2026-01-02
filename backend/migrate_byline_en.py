#!/usr/bin/env python3
"""
Migration Script: Add byline_en to existing articles
Updates all articles in DynamoDB with translated English bylines
"""

import boto3
import sys
import os
from decimal import Decimal
from typing import List, Dict, Any

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from byline_translator import translate_byline


class BylineMigration:
    """Migrates existing articles to include byline_en field"""

    def __init__(self, table_name: str = "seodaily-eng-articles-dev", region: str = "us-east-1"):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
        self.stats = {
            'total': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }

    def scan_all_articles(self) -> List[Dict[str, Any]]:
        """Scan all articles from DynamoDB"""
        print(f"📖 Scanning all articles from {self.table_name}...")

        articles = []
        last_evaluated_key = None

        while True:
            if last_evaluated_key:
                response = self.table.scan(ExclusiveStartKey=last_evaluated_key)
            else:
                response = self.table.scan()

            items = response.get('Items', [])
            articles.extend(items)

            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break

            print(f"  Scanned {len(articles)} articles so far...")

        print(f"✅ Found {len(articles)} total items")
        return articles

    def update_article_byline(self, article: Dict[str, Any]) -> bool:
        """Update a single article with byline_en"""
        news_id = article.get('news_id')

        # Skip settings and other non-article items
        if not news_id or news_id == 'settings_config':
            return False

        byline_ko = article.get('byline', '')
        byline_en_existing = article.get('byline_en')

        # Skip if byline_en already exists and is valid
        if byline_en_existing and byline_en_existing != 'Seoul Economic Daily':
            print(f"  ⏭️  {news_id}: byline_en already exists ({byline_en_existing})")
            self.stats['skipped'] += 1
            return True

        # Translate byline
        byline_en = translate_byline(byline_ko) if byline_ko else 'Seoul Economic Daily'

        try:
            # Update only the byline_en field
            self.table.update_item(
                Key={'news_id': news_id},
                UpdateExpression='SET byline_en = :byline_en',
                ExpressionAttributeValues={':byline_en': byline_en}
            )

            print(f"  ✅ {news_id}: '{byline_ko}' → '{byline_en}'")
            self.stats['updated'] += 1
            return True

        except Exception as e:
            print(f"  ❌ {news_id}: Error - {e}")
            self.stats['errors'] += 1
            return False

    def migrate(self, dry_run: bool = False, limit: int = None):
        """
        Run migration to add byline_en to all articles

        Args:
            dry_run: If True, only preview changes without updating
            limit: Maximum number of articles to update (for testing)
        """
        print("\n" + "="*60)
        print("📝 Byline Migration Script")
        print("="*60)

        if dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
        if limit:
            print(f"⚠️  LIMITED RUN - Maximum {limit} articles")

        print()

        # Scan all articles
        articles = self.scan_all_articles()
        self.stats['total'] = len(articles)

        # Filter out settings and non-article items
        articles = [a for a in articles if a.get('news_id') != 'settings_config']

        print(f"\n📊 Processing {len(articles)} articles...")
        print("-" * 60)

        # Process articles
        for i, article in enumerate(articles):
            if limit and i >= limit:
                print(f"\n⚠️  Reached limit of {limit} articles")
                break

            if not dry_run:
                self.update_article_byline(article)
            else:
                news_id = article.get('news_id')
                byline_ko = article.get('byline', '')
                byline_en = translate_byline(byline_ko) if byline_ko else 'Seoul Economic Daily'
                print(f"  [DRY RUN] {news_id}: '{byline_ko}' → '{byline_en}'")

        # Print summary
        print("\n" + "="*60)
        print("📊 Migration Summary")
        print("="*60)
        print(f"Total articles: {self.stats['total']}")
        print(f"Updated: {self.stats['updated']}")
        print(f"Skipped (already has byline_en): {self.stats['skipped']}")
        print(f"Errors: {self.stats['errors']}")
        print("="*60)

        if dry_run:
            print("\n💡 This was a DRY RUN. Run without --dry-run to apply changes.")
        else:
            print("\n✅ Migration completed!")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Migrate byline_en field to existing articles')
    parser.add_argument('--table', default='seodaily-eng-articles-dev', help='DynamoDB table name')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    parser.add_argument('--limit', type=int, help='Limit number of articles to process (for testing)')

    args = parser.parse_args()

    migration = BylineMigration(table_name=args.table, region=args.region)
    migration.migrate(dry_run=args.dry_run, limit=args.limit)


if __name__ == "__main__":
    main()
