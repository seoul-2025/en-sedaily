"""
Related Articles Handler - Hashtag-based recommendations
Returns articles with matching hashtags for better relevance
"""
import logging
import boto3
import json
from typing import List, Set

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def extract_hashtags(hashtags_str: str) -> Set[str]:
    """Extract hashtags from string"""
    if not hashtags_str:
        return set()
    
    # Split by comma, space, or newline
    tags = hashtags_str.replace(',', ' ').replace('\n', ' ').split()
    # Remove # prefix and convert to lowercase
    return {tag.strip().lstrip('#').lower() for tag in tags if tag.strip()}


def calculate_relevance_score(article_tags: Set[str], target_tags: Set[str], same_category: bool) -> float:
    """Calculate relevance score based on hashtag overlap"""
    if not target_tags:
        return 1.0 if same_category else 0.5
    
    # Count matching hashtags
    matching_tags = len(article_tags & target_tags)
    
    # Score: matching tags + category bonus
    score = matching_tags * 2.0
    if same_category:
        score += 1.0
    
    return score


async def get_related_articles(article_id: str, limit: int = 4):
    """Get related articles based on hashtags and category"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('seodaily-eng-articles-dev')
    
    try:
        # Get source article
        response = table.get_item(Key={'news_id': article_id})
        if 'Item' not in response:
            logger.warning(f"Article {article_id} not found")
            return []
        
        source_article = response['Item']
        source_hashtags = extract_hashtags(source_article.get('hashtags', ''))
        source_category = source_article.get('category', '')
        
        logger.info(f"Source article {article_id}: category={source_category}, hashtags={source_hashtags}")
        
        # Scan all articles
        scan_response = table.scan()
        all_articles = scan_response.get('Items', [])
        
        # Calculate relevance scores
        scored_articles = []
        for article in all_articles:
            # Skip source article
            if article.get('news_id') == article_id:
                continue
            
            # Skip articles without content
            if not article.get('content_en', '').strip():
                continue
            
            article_hashtags = extract_hashtags(article.get('hashtags', ''))
            same_category = article.get('category') == source_category
            
            score = calculate_relevance_score(article_hashtags, source_hashtags, same_category)
            
            # Only include if score > 0
            if score > 0:
                scored_articles.append({
                    'article': article,
                    'score': score,
                    'matching_tags': len(article_hashtags & source_hashtags)
                })
        
        # Sort by score (descending) and published_at (descending)
        scored_articles.sort(key=lambda x: (x['score'], x['article'].get('published_at', '')), reverse=True)
        
        # Return top N
        results = []
        for item in scored_articles[:limit]:
            article = item['article']
            results.append({
                'news_id': article.get('news_id'),
                'title': article.get('title_en'),
                'published_at': article.get('published_at'),
                'category': article.get('category', 'news'),
                'provider': article.get('provider', 'Seoul Economic Daily'),
                'relevance_score': item['score'],
                'matching_tags': item['matching_tags']
            })
        
        logger.info(f"Found {len(results)} related articles for {article_id}")
        return results
        
    except Exception as e:
        logger.error(f"Error getting related articles: {e}", exc_info=True)
        return []


def lambda_handler(event: dict, context) -> dict:
    """Lambda handler for related articles"""
    import asyncio
    
    try:
        # Get article_id from path parameters
        path_parameters = event.get("pathParameters", {})
        article_id = path_parameters.get("article_id", "")
        
        if not article_id:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": "Article ID is required"
                })
            }
        
        # Get limit from query parameters (default: 4)
        query_params = event.get("queryStringParameters") or {}
        limit = int(query_params.get("limit", 4))
        
        # Get related articles
        articles = asyncio.run(get_related_articles(article_id, limit))
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "article_id": article_id,
                "related_articles": articles,
                "count": len(articles)
            })
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": str(e)
            })
        }
