#!/usr/bin/env python3
"""
Fix Existing Articles - Extract [HEADLINE] and [ARTICLE] sections
"""
import boto3
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_sections(text):
    """Extract [HEADLINE] and [ARTICLE] sections from translated text"""
    if not text:
        return None, None
    
    # Extract headline
    headline_match = re.search(r'\[HEADLINE\]\s*([^\[]+)', text, re.IGNORECASE)
    headline = headline_match.group(1).strip() if headline_match else None
    
    # Extract article content
    article_match = re.search(r'\[ARTICLE\]\s*(.+?)(?=\[DISCLAIMER\]|\[SEO/AEO\]|$)', text, re.IGNORECASE | re.DOTALL)
    article = article_match.group(1).strip() if article_match else None
    
    return headline, article


def fix_existing_articles():
    """Fix all existing articles in DynamoDB"""
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('seodaily-eng-articles-dev')
    
    # Scan all articles
    logger.info("Scanning all articles from DynamoDB...")
    response = table.scan()
    articles = response.get('Items', [])
    
    logger.info(f"Found {len(articles)} articles to process")
    
    success_count = 0
    skip_count = 0
    failed_count = 0
    
    for idx, article in enumerate(articles, 1):
        news_id = article.get('news_id')
        title_en = article.get('title_en', '')
        content_en = article.get('content_en', '')
        
        logger.info(f"[{idx}/{len(articles)}] Processing {news_id}")
        
        # Check if already has [HEADLINE] or [ARTICLE] markers
        if '[HEADLINE]' in title_en or '[ARTICLE]' in content_en:
            # Extract sections
            new_title, new_content = None, None
            
            if '[HEADLINE]' in title_en:
                new_title, _ = extract_sections(title_en)
            
            if '[ARTICLE]' in content_en:
                _, new_content = extract_sections(content_en)
            
            # Update if extracted
            if new_title or new_content:
                try:
                    update_expr = []
                    expr_values = {}
                    
                    if new_title:
                        update_expr.append('title_en = :title')
                        expr_values[':title'] = new_title
                        logger.info(f"  ✅ Extracted title: {new_title[:50]}...")
                    
                    if new_content:
                        update_expr.append('content_en = :content')
                        expr_values[':content'] = new_content
                        logger.info(f"  ✅ Extracted content: {len(new_content)} chars")
                    
                    if update_expr:
                        table.update_item(
                            Key={'news_id': news_id},
                            UpdateExpression='SET ' + ', '.join(update_expr),
                            ExpressionAttributeValues=expr_values
                        )
                        success_count += 1
                except Exception as e:
                    logger.error(f"  ❌ Failed to update {news_id}: {e}")
                    failed_count += 1
            else:
                logger.info(f"  ⏭️  No sections found to extract")
                skip_count += 1
        else:
            logger.info(f"  ⏭️  No markers found, skipping")
            skip_count += 1
    
    # Final report
    logger.info("=" * 50)
    logger.info("FINAL RESULTS")
    logger.info("=" * 50)
    logger.info(f"Total Articles: {len(articles)}")
    logger.info(f"Successfully Updated: {success_count}")
    logger.info(f"Skipped: {skip_count}")
    logger.info(f"Failed: {failed_count}")
    logger.info("=" * 50)


if __name__ == "__main__":
    fix_existing_articles()
