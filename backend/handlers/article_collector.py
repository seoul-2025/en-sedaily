"""
Article Collector Lambda Function
Automatically collects and translates new Seoul Economic articles
"""
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any

from clients.bigkinds_client import BigKindsClient
from clients.translation_service import TranslationService
from clients.dynamodb_client import DynamoDBClient
from config import settings
from utils.slug_generator import generate_slug, ensure_unique_slug
from utils.date_utils import extract_timestamp_from_news_id

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Category mapping: English → Korean (for consistency with existing data)
ENGLISH_TO_KOREAN_CATEGORY = {
    'finance': '경제',
    'technology': 'IT_과학',
    'politics': '정치',
    'society': '사회',
    'culture': '문화',
    'sports': '스포츠',
    'international': '국제',
    'news': 'news'  # Keep 'news' as-is
}


async def collect_and_translate_articles(hours: int = 24) -> Dict[str, Any]:
    """
    Collect articles from last N hours and translate them
    
    Args:
        hours: Number of hours to look back
    
    Returns:
        Summary of collection results
    """
    bigkinds_client = None
    dynamodb_client = None
    
    try:
        # Initialize clients
        bigkinds_client = BigKindsClient(
            api_key=settings.bigkinds_api_key,
            base_url=settings.bigkinds_api_url
        )
        
        translation_service = TranslationService(
            model_id=settings.anthropic_model_id,
            anthropic_api_key=settings.anthropic_api_key
        )
        
        dynamodb_client = DynamoDBClient(
            table_name=settings.dynamodb_table_articles,
            region=settings.region
        )
        
        # Calculate date range - collect today's articles (KST timezone)
        from datetime import timezone
        kst = timezone(timedelta(hours=9))
        now_kst = datetime.now(kst)
        # Start of today in KST (00:00:00)
        from_date = now_kst.replace(hour=0, minute=0, second=0, microsecond=0)
        # End of today (23:59:59) + 1 day for exclusive until
        until = from_date + timedelta(days=2)
        
        print(f"DEBUG: Collecting articles from {from_date.strftime('%Y-%m-%d')} to {until.strftime('%Y-%m-%d')}")
        logger.info(f"Collecting articles from {from_date} to {until}")
        
        # Collect ALL articles with pagination
        all_articles = []
        return_from = 0
        batch_size = 100
        max_results = 10000
        
        while return_from < max_results:
            logger.info(f"Fetching batch: return_from={return_from}, batch_size={batch_size}")
            
            search_result = await bigkinds_client.search_news(
                query="",
                published_from=from_date.strftime("%Y-%m-%d"),
                published_until=until.strftime("%Y-%m-%d"),
                providers=["서울경제"],
                return_from=return_from,
                return_size=batch_size,
                fields=["news_id", "published_at", "provider_link_page"]
            )
            
            batch_count = len(search_result.documents)
            all_articles.extend(search_result.documents)
            
            logger.info(f"Batch {return_from//batch_size + 1}: Got {batch_count} articles, Total: {search_result.total_hits}")
            
            if batch_count == 0:
                break
            
            if len(all_articles) >= search_result.total_hits:
                break
            
            return_from += batch_size
        
        logger.info(f"Found {len(all_articles)} total articles across all batches")
        
        # Get full article details with content
        news_ids = [article.news_id for article in all_articles]
        if not news_ids:
            logger.info("No articles found for today")
            return {
                "status": "success",
                "total_found": 0,
                "new_articles": 0,
                "cached_articles": 0,
                "failed_articles": 0,
                "collection_time": datetime.now().isoformat()
            }
        
        logger.info(f"Fetching full details for {len(news_ids)} articles")
        
        # Batch check existing articles
        existing_ids = await dynamodb_client.batch_check_exists(news_ids)
        logger.info(f"Found {len(existing_ids)} existing articles, {len(news_ids) - len(existing_ids)} new")
        
        # Filter to only new articles
        new_news_ids = [nid for nid in news_ids if nid not in existing_ids]
        
        if not new_news_ids:
            logger.info(f"All {len(all_articles)} articles already exist in database")
            return {
                "status": "success",
                "total_found": len(all_articles),
                "new_articles": 0,
                "cached_articles": len(existing_ids),
                "failed_articles": 0,
                "collection_time": datetime.now().isoformat(),
                "message": "No new articles to process"
            }
        
        # Get details only for new articles (batch by 100 to avoid API limits)
        detailed_articles = []
        batch_size_detail = 100
        
        for i in range(0, len(new_news_ids), batch_size_detail):
            batch_ids = new_news_ids[i:i+batch_size_detail]
            logger.info(f"Fetching details for batch {i//batch_size_detail + 1}: {len(batch_ids)} articles")
            
            batch_articles = await bigkinds_client.get_article_detail(
                news_ids=batch_ids,
                fields=[
                    "news_id", "title", "content", "published_at",
                    "provider_name", "category", "byline", 
                    "provider_link_page",  # ONLY provider_link_page
                    "images", "images_caption"
                ]
            )
            detailed_articles.extend(batch_articles)
        
        logger.info(f"Got {len(detailed_articles)} detailed articles")
        
        new_articles = 0
        cached_articles = len(existing_ids)
        failed_articles = 0
        
        for article in detailed_articles:
            try:
                # Skip articles without content
                if not article.content or not article.content.strip():
                    logger.info(f"Skipping article {article.news_id} - no content")
                    continue
                
                # Translate title and content with chunking for large content
                logger.info(f"Translating article {article.news_id}")
                
                # Combine title and content for full article translation
                full_text = f"Title: {article.title}\n\nContent: {article.content or ''}"
                
                # Split large content into chunks
                max_chunk_size = 4000
                
                if len(full_text) > max_chunk_size:
                    logger.info(f"Article {article.news_id} is large ({len(full_text)} chars), splitting into chunks")
                    chunks = [full_text[i:i+max_chunk_size] for i in range(0, len(full_text), max_chunk_size)]
                    translated_chunks = []
                    for chunk in chunks:
                        translated_chunk = await translation_service.translate(
                            chunk,
                            source_lang="ko",
                            target_lang="en"
                        )
                        translated_chunks.append(translated_chunk)
                    translated_full = " ".join(translated_chunks)
                else:
                    translated_full = await translation_service.translate(
                        full_text,
                        source_lang="ko",
                        target_lang="en"
                    )
                
                # Extract sections from Claude translation
                import re
                
                # Extract [HEADLINE]
                headline_match = re.search(r'\[HEADLINE\]\s*([^\[]+)', translated_full, re.IGNORECASE)
                title_en = headline_match.group(1).strip() if headline_match else article.title
                
                # Extract [BYLINE]
                byline_match = re.search(r'\[BYLINE\]\s*By\s+([^\[\n]+)', translated_full, re.IGNORECASE)
                byline_en = byline_match.group(1).strip() if byline_match else article.byline
                
                # Extract [ARTICLE]
                article_match = re.search(r'\[ARTICLE\]\s*(.+?)(?=\[DISCLAIMER\]|\[SEO/AEO\]|$)', translated_full, re.IGNORECASE | re.DOTALL)
                content_en = article_match.group(1).strip() if article_match else translated_full

                # Generate AI Summary
                ai_summary = ''
                ai_key_points = []
                try:
                    logger.info(f"Generating AI summary for article {article.news_id}")
                    summary_data = await translation_service.generate_ai_summary(
                        title=title_en,
                        content=content_en
                    )
                    ai_summary = summary_data.get('summary', '')
                    ai_key_points = summary_data.get('key_points', [])
                    logger.info(f"Successfully generated AI summary for article {article.news_id}")
                except Exception as e:
                    logger.warning(f"Failed to generate AI summary for article {article.news_id}: {e}")
                    # Continue without AI summary - it's not critical

                # Extract [SEO/AEO] metadata
                seo_section = re.search(r'\[SEO/AEO\]\s*(.+?)$', translated_full, re.IGNORECASE | re.DOTALL)
                meta_description = ''
                keywords = ''
                hashtags = ''
                
                if seo_section:
                    seo_content = seo_section.group(1)
                    
                    # Extract Meta Description
                    meta_match = re.search(r'Meta Description[:\s]+(.+?)(?=\n\n|Keywords:|Hashtags:|Q&A:|$)', seo_content, re.IGNORECASE | re.DOTALL)
                    if meta_match:
                        meta_description = meta_match.group(1).strip()
                    
                    # Extract Keywords
                    keywords_match = re.search(r'Keywords[:\s]+(.+?)(?=\n\n|Hashtags:|Q&A:|$)', seo_content, re.IGNORECASE | re.DOTALL)
                    if keywords_match:
                        keywords = keywords_match.group(1).strip()
                    
                    # Extract Hashtags
                    hashtags_match = re.search(r'Hashtags[:\s]+(.+?)(?=\n\n|Q&A:|$)', seo_content, re.IGNORECASE | re.DOTALL)
                    if hashtags_match:
                        hashtags = hashtags_match.group(1).strip()
                
                # Extract main category from array
                category = article.category
                if isinstance(category, list):
                    if category:
                        category = category[0].split('>')[0] if '>' in category[0] else category[0]
                    else:
                        category = 'news'  # Default for empty list
                elif isinstance(category, str):
                    if '>' in category:
                        category = category.split('>')[0]
                else:
                    category = 'news'  # Default for None or other types

                # Convert English category to Korean (if needed)
                category = ENGLISH_TO_KOREAN_CATEGORY.get(category, category)

                # Ensure category is always a string (keep Korean as-is)
                category = str(category) if category else 'news'
                
                # Log if no original_link (but still save)
                if not article.original_link:
                    logger.warning(f"Article {article.news_id} has no provider_link_page")

                # Generate SEO-friendly slug
                slug = generate_slug(
                    title_en=title_en,
                    published_at=article.published_at,
                    category=category
                )

                # Ensure slug uniqueness
                slug = await ensure_unique_slug(
                    slug=slug,
                    published_at=article.published_at,
                    dynamodb_client=dynamodb_client
                )

                logger.info(f"Generated slug for article {article.news_id}: {slug}")

                # Extract actual publish time from news_id (with fallback)
                try:
                    actual_published_at = extract_timestamp_from_news_id(article.news_id)
                    logger.info(f"Extracted actual timestamp from news_id: {actual_published_at}")
                except ValueError as e:
                    logger.warning(f"Failed to extract timestamp from news_id {article.news_id}: {e}. Using BigKinds timestamp.")
                    actual_published_at = article.published_at

                # Add Naver TV video for December 31st articles
                naver_tv_url = None
                if actual_published_at.startswith('2025-12-31'):
                    naver_tv_url = 'https://tv.naver.com/v/91304512'
                    logger.info(f"Adding Naver TV video to Dec 31 article: {article.news_id}")

                # Save to DynamoDB with SEO metadata, slug, and AI summary
                article_data = {
                    'news_id': article.news_id,
                    'slug': slug,  # NEW: SEO-friendly URL slug
                    'title_ko': article.title,
                    'title_en': title_en,
                    'content_ko': article.content or '',
                    'content_en': content_en,
                    'published_at': actual_published_at,  # Use actual timestamp from news_id
                    'category': category,
                    'provider': article.provider,
                    'byline': byline_en,
                    'original_link': article.original_link,
                    'images': article.images,
                    'images_caption': article.images_caption,
                    'meta_description': meta_description,
                    'keywords': keywords,
                    'hashtags': hashtags,
                    'ai_summary': ai_summary,
                    'ai_key_points': ai_key_points
                }

                # Add naver_tv_url if exists
                if naver_tv_url:
                    article_data['naver_tv_url'] = naver_tv_url

                saved = await dynamodb_client.save_article(article_data)
                
                if saved:
                    new_articles += 1
                    logger.info(f"Successfully saved article {article.news_id}")
                    if meta_description:
                        logger.info(f"  SEO: Meta={len(meta_description)} chars, Keywords={bool(keywords)}, Hashtags={bool(hashtags)}")
                else:
                    failed_articles += 1
                    logger.error(f"Failed to save article {article.news_id} to DynamoDB")
                
            except Exception as e:
                failed_articles += 1
                logger.error(f"Failed to process article {article.news_id}: {e}")
                continue
        
        result = {
            "status": "success",
            "total_found": len(all_articles),
            "new_articles": new_articles,
            "cached_articles": cached_articles,
            "failed_articles": failed_articles,
            "collection_time": datetime.now().isoformat()
        }
        
        logger.info(f"Collection complete: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Collection failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "collection_time": datetime.now().isoformat()
        }
    
    finally:
        if bigkinds_client:
            await bigkinds_client.close()


def lambda_handler(event: dict, context) -> dict:
    """
    AWS Lambda handler for scheduled article collection
    
    Args:
        event: EventBridge event (contains schedule info)
        context: Lambda context
    
    Returns:
        Collection results
    """
    logger.info(f"Article collection triggered: {event}")
    
    # Ignore hours parameter - always collect today's articles
    # Run async collection
    result = asyncio.run(collect_and_translate_articles(24))
    
    return {
        "statusCode": 200,
        "body": result
    }
