"""
SearchHandler Lambda Function - DynamoDB Only
Only returns articles that are already translated and stored in DynamoDB
"""
import logging
import boto3
from typing import List
from dataclasses import dataclass
from datetime import datetime
import math

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class SearchResponse:
    total_hits: int
    page: int
    page_size: int
    total_pages: int
    articles: List[dict]


async def search_dynamodb(query: str, published_from: str, published_until: str, categories: List[str], page: int, page_size: int):
    """Search DynamoDB for translated articles"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('seodaily-eng-articles-dev')

    # No category mapping needed - categories are stored in Korean

    # Scan all items with pagination
    items = []
    response = table.scan()
    items.extend(response.get('Items', []))

    # Handle pagination
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))

    logger.info(f"Total items scanned from DynamoDB: {len(items)}")
    logger.info(f"Category filter: {categories}")

    # Filter in Python: query, date range, content exists, and category
    filtered_items = []
    query_lower = query.lower() if query else ''

    logger.info(f"Date filter: {published_from} to {published_until} (exclusive)")
    
    for item in items:
        # Query filter (search in title, content, keywords, and hashtags)
        if query_lower and query_lower != '*':
            title = item.get('title_en', '').lower()
            content = item.get('content_en', '').lower()
            keywords = item.get('keywords', '').lower()
            hashtags = item.get('hashtags', '').lower()
            
            if query_lower not in title and query_lower not in content and query_lower not in keywords and query_lower not in hashtags:
                continue
        
        # Date filter (published_until is exclusive)
        pub_date = item.get('published_at', '')[:10]
        if pub_date < published_from or pub_date >= published_until:
            continue
        
        # Category filter (Korean)
        if categories and item.get('category') not in categories:
            continue
        
        filtered_items.append(item)
    
    items = filtered_items
    logger.info(f"Filtered items: {len(items)}")
    
    # Sort by published_at descending
    items.sort(key=lambda x: x.get('published_at', ''), reverse=True)
    
    # Pagination
    total_hits = len(items)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_items = items[start_idx:end_idx]
    
    # Transform to article format
    articles = []
    for item in paginated_items:
        # Get content preview (first 200 chars for list view)
        content_en = item.get('content_en', '')
        content_preview = content_en[:200] if content_en else ''

        articles.append({
            'news_id': item.get('news_id'),
            'title': item.get('title_en'),
            'published_at': item.get('published_at'),
            'provider': item.get('provider', 'Seoul Economic Daily'),
            'category': item.get('category', 'news'),
            'slug': item.get('slug'),
            'original_link': item.get('original_link'),
            'content': content_preview,
            'byline': item.get('byline', ''),
            'meta_description': item.get('meta_description', '')
        })
    
    return SearchResponse(
        total_hits=total_hits,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total_hits / page_size) if total_hits > 0 else 0,
        articles=articles
    )


def lambda_handler(event: dict, context) -> dict:
    import asyncio
    import json
    
    try:
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)
        
        query = body.get("query", "")
        filters = body.get("filters", {})
        page = body.get("page", 1)
        page_size = body.get("page_size", 10)
        
        # Run async search
        response = asyncio.run(search_dynamodb(
            query=query,
            published_from=filters.get("published_from", "2024-01-01"),
            published_until=filters.get("published_until", datetime.now().strftime("%Y-%m-%d")),
            categories=filters.get("categories", []),
            page=page,
            page_size=page_size
        ))
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "total_hits": response.total_hits,
                "page": response.page,
                "page_size": response.page_size,
                "total_pages": response.total_pages,
                "articles": response.articles
            })
        }
    
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": {
                    "code": "SEARCH_ERROR",
                    "message": str(e)
                }
            })
        }
