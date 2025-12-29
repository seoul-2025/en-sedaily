#!/usr/bin/env python3
"""
Slug Migration Script

Batch migration script to generate slugs for existing articles in DynamoDB.
Processes 7,889+ articles and adds SEO-friendly slugs.

Usage:
    # Dry run (preview only)
    python3 migrate_slugs.py --dry-run

    # Actual migration
    python3 migrate_slugs.py

    # Custom table
    python3 migrate_slugs.py --table seodaily-eng-articles-prod

Author: Seoul Economic Daily
Date: 2025-12-22
"""

import asyncio
import argparse
import sys
import os
from typing import List, Dict, Any
from datetime import datetime
import logging

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import boto3
from boto3.dynamodb.conditions import Key, Attr

from clients.dynamodb_client import DynamoDBClient
from utils.slug_generator import generate_slug, ensure_unique_slug

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class SlugMigrator:
    """Handles batch migration of slugs for existing articles"""

    def __init__(self, table_name: str = "seodaily-eng-articles-dev", region: str = "us-east-1"):
        self.table_name = table_name
        self.region = region
        self.dynamodb_client = DynamoDBClient(table_name=table_name, region=region)
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)

        self.stats = {
            'total': 0,
            'migrated': 0,
            'skipped': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None,
            'errors': []
        }

    async def scan_all_articles(self) -> List[Dict[str, Any]]:
        """
        Scan all articles from DynamoDB.

        Uses pagination to handle large datasets.

        Returns:
            List of all article items
        """
        logger.info(f"Scanning all articles from table '{self.table_name}'...")

        articles = []
        scan_kwargs = {
            'ProjectionExpression': 'news_id, title_en, published_at, category, slug'
        }

        try:
            response = self.table.scan(**scan_kwargs)
            articles.extend(response.get('Items', []))

            # Handle pagination
            while 'LastEvaluatedKey' in response:
                logger.info(f"Scanned {len(articles)} articles so far... (paginating)")
                scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
                response = self.table.scan(**scan_kwargs)
                articles.extend(response.get('Items', []))

            logger.info(f"✓ Total articles found: {len(articles)}")
            return articles

        except Exception as e:
            logger.error(f"Failed to scan table: {e}", exc_info=True)
            raise

    async def migrate_article(self, article: Dict[str, Any], dry_run: bool = False) -> bool:
        """
        Generate and save slug for a single article.

        Args:
            article: Article item from DynamoDB
            dry_run: If True, only log what would happen (no actual update)

        Returns:
            True if successful, False otherwise
        """
        try:
            news_id = article.get('news_id')
            if not news_id:
                logger.warning("Article missing news_id, skipping")
                self.stats['failed'] += 1
                return False

            # Skip if slug already exists
            existing_slug = article.get('slug')
            if existing_slug and existing_slug.strip():
                logger.debug(f"Skipping {news_id}: slug already exists ({existing_slug})")
                self.stats['skipped'] += 1
                return True

            # Get required fields
            title_en = article.get('title_en', '')
            published_at = article.get('published_at', '')
            category = article.get('category', 'news')

            if not title_en:
                logger.warning(f"Article {news_id} missing title_en, using fallback slug")

            # Generate slug
            slug = generate_slug(
                title_en=title_en,
                published_at=published_at,
                category=category
            )

            # Ensure uniqueness (this checks DynamoDB via GSI)
            slug = await ensure_unique_slug(
                slug=slug,
                published_at=published_at,
                dynamodb_client=self.dynamodb_client
            )

            if dry_run:
                logger.info(f"[DRY RUN] Would migrate {news_id}: '{title_en[:50]}...' → '{slug}'")
                self.stats['migrated'] += 1
                return True

            # Update article with slug
            self.table.update_item(
                Key={'news_id': news_id},
                UpdateExpression='SET slug = :slug, updated_at = :updated_at',
                ExpressionAttributeValues={
                    ':slug': slug,
                    ':updated_at': datetime.utcnow().isoformat()
                }
            )

            logger.info(f"✓ Migrated {news_id}: {slug}")
            self.stats['migrated'] += 1
            return True

        except Exception as e:
            error_msg = f"Failed to migrate {article.get('news_id', 'unknown')}: {e}"
            logger.error(error_msg)
            self.stats['failed'] += 1
            self.stats['errors'].append(error_msg)
            return False

    async def migrate_batch(
        self,
        articles: List[Dict[str, Any]],
        batch_size: int = 50,
        dry_run: bool = False
    ):
        """
        Process articles in batches to avoid throttling.

        Args:
            articles: List of articles to migrate
            batch_size: Number of articles per batch
            dry_run: If True, only preview changes
        """
        total = len(articles)
        num_batches = (total + batch_size - 1) // batch_size

        logger.info(f"Processing {total} articles in {num_batches} batches of {batch_size}")

        for i in range(0, total, batch_size):
            batch = articles[i:i + batch_size]
            batch_num = i // batch_size + 1

            logger.info(f"\n--- Batch {batch_num}/{num_batches} ---")

            # Process batch concurrently (within batch)
            tasks = [self.migrate_article(article, dry_run) for article in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Count exceptions
            exceptions = [r for r in results if isinstance(r, Exception)]
            if exceptions:
                logger.warning(f"Batch {batch_num} had {len(exceptions)} exceptions")

            # Rate limiting: wait between batches (except last batch)
            if i + batch_size < total:
                logger.debug("Waiting 1 second before next batch...")
                await asyncio.sleep(1)

    async def run_migration(self, dry_run: bool = False, sample_size: int = None):
        """
        Execute the migration.

        Args:
            dry_run: If True, only preview changes without updating
            sample_size: If set, only migrate first N articles (for testing)

        Returns:
            Migration statistics
        """
        self.stats['start_time'] = datetime.now()

        logger.info("=" * 80)
        logger.info(f"Starting Slug Migration (dry_run={dry_run})")
        logger.info("=" * 80)
        logger.info(f"Table: {self.table_name}")
        logger.info(f"Region: {self.region}")
        logger.info("")

        # Scan all articles
        articles = await self.scan_all_articles()
        self.stats['total'] = len(articles)

        if not articles:
            logger.warning("No articles found in table")
            return self.stats

        # Sample mode
        if sample_size:
            logger.info(f"Sample mode: processing first {sample_size} articles only")
            articles = articles[:sample_size]

        # Run migration
        await self.migrate_batch(articles, batch_size=50, dry_run=dry_run)

        # Calculate duration
        self.stats['end_time'] = datetime.now()
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()

        # Print summary
        logger.info("")
        logger.info("=" * 80)
        logger.info("MIGRATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Total articles:           {self.stats['total']}")
        logger.info(f"Migrated:                 {self.stats['migrated']}")
        logger.info(f"Skipped (already had slug): {self.stats['skipped']}")
        logger.info(f"Failed:                   {self.stats['failed']}")
        logger.info(f"Duration:                 {duration:.2f} seconds")
        logger.info(f"Rate:                     {self.stats['migrated'] / max(duration, 1):.2f} articles/sec")
        logger.info("=" * 80)

        if self.stats['errors']:
            logger.info("")
            logger.info("Errors encountered:")
            for error in self.stats['errors'][:10]:  # Show first 10 errors
                logger.info(f"  - {error}")
            if len(self.stats['errors']) > 10:
                logger.info(f"  ... and {len(self.stats['errors']) - 10} more errors")

        if dry_run:
            logger.info("")
            logger.info("This was a DRY RUN - no changes were made to DynamoDB")
            logger.info("Run without --dry-run to perform actual migration")

        return self.stats


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Migrate articles to slug-based URLs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what would be migrated (no changes)
  python3 migrate_slugs.py --dry-run

  # Migrate first 10 articles (testing)
  python3 migrate_slugs.py --dry-run --sample 10

  # Actual migration of all articles
  python3 migrate_slugs.py

  # Use different table
  python3 migrate_slugs.py --table seodaily-eng-articles-prod
        """
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode (preview only, no changes)'
    )
    parser.add_argument(
        '--table',
        default='seodaily-eng-articles-dev',
        help='DynamoDB table name (default: seodaily-eng-articles-dev)'
    )
    parser.add_argument(
        '--sample',
        type=int,
        help='Only migrate first N articles (for testing)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Set log level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger('utils.slug_generator').setLevel(logging.DEBUG)

    # Create migrator
    migrator = SlugMigrator(table_name=args.table)

    # Run migration
    try:
        stats = await migrator.run_migration(
            dry_run=args.dry_run,
            sample_size=args.sample
        )

        # Exit with error code if any failures
        if stats['failed'] > 0:
            logger.error(f"\nMigration completed with {stats['failed']} failures")
            sys.exit(1)

        logger.info("\n✓ Migration completed successfully")
        sys.exit(0)

    except KeyboardInterrupt:
        logger.warning("\n\nMigration interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n\nMigration failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
