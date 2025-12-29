#!/usr/bin/env python3
"""
Category Migration Script
Updates English categories to Korean in DynamoDB

Usage:
    python scripts/migrate_categories_to_korean.py --dry-run  # Preview changes
    python scripts/migrate_categories_to_korean.py            # Execute migration
"""
import asyncio
import argparse
import boto3
from typing import Dict
import sys

# Category mapping: English → Korean
ENGLISH_TO_KOREAN = {
    'finance': '경제',
    'technology': 'IT_과학',
    'politics': '정치',
    'society': '사회',
    'culture': '문화',
    'sports': '스포츠',
    'international': '국제',
    'news': 'news'  # Keep 'news' as-is
}


class CategoryMigrator:
    """Migrates article categories from English to Korean"""

    def __init__(self, table_name: str, region: str, dry_run: bool = False):
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
        self.dry_run = dry_run
        self.stats = {
            'total_articles': 0,
            'updated': 0,
            'skipped_already_korean': 0,
            'skipped_unknown': 0,
            'failed': 0,
            'errors': []
        }

    async def migrate_all(self) -> Dict:
        """Scan all articles and update English categories to Korean"""
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Starting category migration...")
        print(f"Scanning DynamoDB table...")

        # Scan all articles with pagination
        last_evaluated_key = None
        batch_count = 0

        while True:
            batch_count += 1
            print(f"\nFetching batch #{batch_count}...")

            # Scan batch
            scan_kwargs = {
                'Limit': 100,
                'ProjectionExpression': 'news_id, category'
            }
            if last_evaluated_key:
                scan_kwargs['ExclusiveStartKey'] = last_evaluated_key

            response = self.table.scan(**scan_kwargs)
            articles = response.get('Items', [])

            print(f"  Found {len(articles)} articles in this batch")
            self.stats['total_articles'] += len(articles)

            # Process batch
            for article in articles:
                await self.migrate_article(article)

            # Check for more pages
            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break

            # Rate limiting
            await asyncio.sleep(0.1)

        # Print summary
        self.print_summary()
        return self.stats

    async def migrate_article(self, article: Dict):
        """Update a single article's category"""
        news_id = article['news_id']
        old_category = article.get('category', '')

        try:
            # Handle list type category (extract first element)
            if isinstance(old_category, list):
                if len(old_category) > 0:
                    old_category = old_category[0]
                else:
                    old_category = ''

            # Convert to string
            old_category = str(old_category).strip()

            # Check if already in Korean (skip)
            if old_category in ['경제', 'IT_과학', '정치', '사회', '문화', '스포츠', '국제', '지역']:
                self.stats['skipped_already_korean'] += 1
                return

            # Check if English category exists in mapping
            if old_category not in ENGLISH_TO_KOREAN:
                print(f"  ⚠ Unknown category: {old_category} (news_id: {news_id})")
                self.stats['skipped_unknown'] += 1
                return

            # Get Korean category
            new_category = ENGLISH_TO_KOREAN[old_category]

            # Skip if no change needed
            if old_category == new_category:
                self.stats['skipped_already_korean'] += 1
                return

            # Update category
            if self.dry_run:
                print(f"  [DRY RUN] Would update {news_id}:")
                print(f"    OLD: {old_category}")
                print(f"    NEW: {new_category}")
            else:
                # Update DynamoDB
                self.table.update_item(
                    Key={'news_id': news_id},
                    UpdateExpression='SET category = :new_category',
                    ExpressionAttributeValues={
                        ':new_category': new_category
                    }
                )
                print(f"  ✓ Updated {news_id}: {old_category} → {new_category}")

            self.stats['updated'] += 1

        except Exception as e:
            error_msg = f"Error updating {news_id}: {e}"
            print(f"  ✗ {error_msg}")
            self.stats['failed'] += 1
            self.stats['errors'].append(error_msg)

    def print_summary(self):
        """Print migration summary"""
        print("\n" + "="*60)
        print(f"{'DRY RUN ' if self.dry_run else ''}MIGRATION SUMMARY")
        print("="*60)
        print(f"Total articles scanned:    {self.stats['total_articles']}")
        print(f"Articles updated:          {self.stats['updated']}")
        print(f"Already Korean (skipped):  {self.stats['skipped_already_korean']}")
        print(f"Unknown category:          {self.stats['skipped_unknown']}")
        print(f"Failed:                    {self.stats['failed']}")
        print("="*60)

        if self.stats['errors']:
            print("\nERRORS:")
            for error in self.stats['errors'][:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(self.stats['errors']) > 10:
                print(f"  ... and {len(self.stats['errors']) - 10} more errors")

        if self.dry_run:
            print("\n⚠️  This was a DRY RUN - no changes were made to the database")
            print("   Run without --dry-run to execute the migration")


async def main():
    """Main migration function"""
    parser = argparse.ArgumentParser(
        description='Migrate article categories from English to Korean'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying the database'
    )
    args = parser.parse_args()

    # Run migration
    migrator = CategoryMigrator(
        table_name='seodaily-eng-articles-dev',
        region='us-east-1',
        dry_run=args.dry_run
    )

    try:
        await migrator.migrate_all()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration interrupted by user")
        migrator.print_summary()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Migration failed: {e}")
        migrator.print_summary()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
