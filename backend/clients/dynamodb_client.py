"""
DynamoDB Client
Handles storage and retrieval of translated articles
"""
import boto3
from typing import Optional, Dict, Any
from datetime import datetime


class DynamoDBClient:
    """Client for DynamoDB operations"""
    
    def __init__(self, table_name: str = "seodaily-eng-articles-dev", region: str = "us-east-1"):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
    
    async def get_article(self, news_id: str) -> Optional[Dict[str, Any]]:
        """Get translated article from DynamoDB"""
        try:
            response = self.table.get_item(Key={'news_id': news_id})
            return response.get('Item')
        except Exception:
            return None
    
    async def save_article(self, article: Dict[str, Any]) -> bool:
        """Save translated article to DynamoDB"""
        import logging
        logger = logging.getLogger(__name__)

        try:
            news_id = article['news_id']

            # Determine Naver TV URL based on publication date
            published_at = article.get('published_at', '')
            default_naver_tv_url = 'https://tv.naver.com/v/90963232?playlistNo=998605'

            # Use new URL for articles published on or after 2025-12-26
            if published_at and published_at >= '2025-12-26':
                default_naver_tv_url = 'https://tv.naver.com/v/91011883'

            item = {
                'news_id': news_id,
                'slug': article.get('slug', ''),  # NEW: SEO-friendly URL slug
                'title_ko': article.get('title_ko', ''),
                'title_en': article.get('title_en', ''),
                'content_ko': article.get('content_ko', ''),
                'content_en': article.get('content_en', ''),
                'published_at': published_at,
                'category': article.get('category', ''),
                'provider': article.get('provider', ''),
                'byline': article.get('byline'),
                'original_link': article.get('original_link'),
                'images': article.get('images', []),
                'images_caption': article.get('images_caption', []),
                'meta_description': article.get('meta_description', ''),
                'keywords': article.get('keywords', ''),
                'hashtags': article.get('hashtags', ''),
                'naver_tv_url': article.get('naver_tv_url', default_naver_tv_url),
                'translated_at': datetime.utcnow().isoformat()
            }
            
            # Put item and get response
            response = self.table.put_item(Item=item)
            
            # Verify it was saved by reading it back
            verify = self.table.get_item(Key={'news_id': news_id})
            if 'Item' not in verify:
                logger.error(f"Verification failed: Article {news_id} not found after put_item")
                return False
            
            logger.info(f"Verified save for article {news_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save article {article.get('news_id')}: {e}", exc_info=True)
            return False
    
    async def article_exists(self, news_id: str) -> bool:
        """Check if article already exists in DynamoDB"""
        article = await self.get_article(news_id)
        return article is not None
    
    async def batch_check_exists(self, news_ids: list) -> set:
        """Check which articles exist in DynamoDB (batch operation)"""
        if not news_ids:
            return set()

        existing_ids = set()

        # DynamoDB batch_get_item limit is 100 items
        batch_size = 100
        for i in range(0, len(news_ids), batch_size):
            batch = news_ids[i:i+batch_size]
            keys = [{'news_id': nid} for nid in batch]

            try:
                response = self.dynamodb.batch_get_item(
                    RequestItems={
                        self.table_name: {
                            'Keys': keys,
                            'ProjectionExpression': 'news_id'
                        }
                    }
                )

                items = response.get('Responses', {}).get(self.table_name, [])
                for item in items:
                    existing_ids.add(item['news_id'])

            except Exception as e:
                # Fallback to individual checks if batch fails
                for nid in batch:
                    if await self.article_exists(nid):
                        existing_ids.add(nid)

        return existing_ids

    async def get_article_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Get article by slug using Global Secondary Index (GSI).

        This method queries the 'slug-index' GSI to retrieve an article by its slug.
        The GSI must be created on the 'slug' attribute for this to work.

        Args:
            slug: SEO-friendly URL slug (e.g., "samsung-q4-earnings-beat-expectations")

        Returns:
            Article dict if found, None otherwise

        Note:
            Requires GSI 'slug-index' to be created on the DynamoDB table.
            AWS CLI command to create GSI:
            ```bash
            aws dynamodb update-table \
              --table-name seodaily-eng-articles-dev \
              --attribute-definitions AttributeName=slug,AttributeType=S \
              --global-secondary-indexes \
                "[{
                  \"IndexName\": \"slug-index\",
                  \"KeySchema\": [{\"AttributeName\":\"slug\",\"KeyType\":\"HASH\"}],
                  \"Projection\": {\"ProjectionType\":\"ALL\"},
                  \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
                }]"
            ```
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            response = self.table.query(
                IndexName='slug-index',
                KeyConditionExpression='slug = :slug',
                ExpressionAttributeValues={':slug': slug}
            )

            items = response.get('Items', [])

            if not items:
                logger.debug(f"No article found with slug: {slug}")
                return None

            if len(items) > 1:
                logger.warning(f"Multiple articles found with slug: {slug} (count: {len(items)})")

            return items[0]

        except Exception as e:
            logger.error(f"Failed to query article by slug '{slug}': {e}", exc_info=True)
            return None

    async def slug_exists(self, slug: str) -> bool:
        """
        Check if a slug already exists in DynamoDB.

        Used for ensuring slug uniqueness during article creation.

        Args:
            slug: SEO-friendly URL slug to check

        Returns:
            True if slug exists, False otherwise
        """
        article = await self.get_article_by_slug(slug)
        return article is not None
