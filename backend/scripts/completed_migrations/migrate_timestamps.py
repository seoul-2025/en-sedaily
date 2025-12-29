#!/usr/bin/env python3
"""
Timestamp Migration Script
Updates all existing articles in DynamoDB to use actual publish time from news_id
instead of midnight (00:00:00) timestamps.

Usage:
    python scripts/migrate_timestamps.py --dry-run  # Preview changes
    python scripts/migrate_timestamps.py            # Execute migration
"""
import asyncio
import argparse
from datetime import datetime
from typing import Dict, List
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clients.dynamodb_client import DynamoDBClient
from utils.date_utils import extract_timestamp_from_news_id
from config import settings


class TimestampMigrator:
    """Migrates article timestamps from midnight to actual publish time"""

    def __init__(self, dynamodb_client: DynamoDBClient, dry_run: bool = False):
        self.dynamodb_client = dynamodb_client
        self.dry_run = dry_run
        self.stats = {
            'total_articles': 0,
            'updated': 0,
            'skipped_no_change': 0,
            'failed': 0,
            'errors': []
        }

    async def migrate_all(self) -> Dict:
        """Scan all articles and update timestamps"""
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Starting timestamp migration...")
        print(f"Scanning DynamoDB table: {settings.dynamodb_table_articles}")

        # Scan all articles with pagination
        last_evaluated_key = None
        batch_count = 0

        while True:
            batch_count += 1
            print(f"\nFetching batch #{batch_count}...")

            # Scan batch
            scan_kwargs = {
                'Limit': 100,
                'ProjectionExpression': 'news_id, published_at'
            }
            if last_evaluated_key:
                scan_kwargs['ExclusiveStartKey'] = last_evaluated_key

            response = self.dynamodb_client.table.scan(**scan_kwargs)
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
        """Update a single article's timestamp"""
        news_id = article['news_id']
        old_timestamp = article.get('published_at', '')

        try:
            # Extract actual timestamp from news_id
            new_timestamp = extract_timestamp_from_news_id(news_id)

            # Check if already has correct time (not midnight)
            if 'T00:00:00' not in old_timestamp:
                print(f"  ✓ {news_id}: Already has non-midnight time ({old_timestamp})")
                self.stats['skipped_no_change'] += 1
                return

            # Check if timestamp would change
            if old_timestamp == new_timestamp:
                print(f"  - {news_id}: No change needed")
                self.stats['skipped_no_change'] += 1
                return

            # Update timestamp
            if self.dry_run:
                print(f"  [DRY RUN] Would update {news_id}:")
                print(f"    OLD: {old_timestamp}")
                print(f"    NEW: {new_timestamp}")
            else:
                # Update DynamoDB
                self.dynamodb_client.table.update_item(
                    Key={'news_id': news_id},
                    UpdateExpression='SET published_at = :new_timestamp',
                    ExpressionAttributeValues={
                        ':new_timestamp': new_timestamp
                    }
                )
                print(f"  ✓ Updated {news_id}: {old_timestamp} → {new_timestamp}")

            self.stats['updated'] += 1

        except ValueError as e:
            error_msg = f"Failed to parse timestamp from {news_id}: {e}"
            print(f"  ✗ {error_msg}")
            self.stats['failed'] += 1
            self.stats['errors'].append(error_msg)

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
        print(f"Skipped (no change):       {self.stats['skipped_no_change']}")
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
        description='Migrate article timestamps from midnight to actual publish time'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying the database'
    )
    args = parser.parse_args()

    # Initialize DynamoDB client
    dynamodb_client = DynamoDBClient(
        table_name=settings.dynamodb_table_articles,
        region=settings.region
    )

    # Run migration
    migrator = TimestampMigrator(dynamodb_client, dry_run=args.dry_run)
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
