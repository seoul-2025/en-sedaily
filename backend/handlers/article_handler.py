"""
ArticleHandler Lambda Function
Handles article detail retrieval with translation and caching
"""
import logging
from typing import Optional
from dataclasses import dataclass

from clients.bigkinds_client import BigKindsClient, Article, ValidationError
from clients.translation_service import TranslationService, TranslationError
from clients.cache_manager import CacheManager
from clients.dynamodb_client import DynamoDBClient

logger = logging.getLogger(__name__)


@dataclass
class ArticleDetailResponse:
    """Article detail response with translated content"""
    news_id: str
    title: str
    content: str
    published_at: str
    provider: str
    category: str
    slug: Optional[str] = None
    byline: Optional[str] = None
    byline_en: Optional[str] = None
    original_link: Optional[str] = None
    images: list = None
    images_caption: list = None
    meta_description: Optional[str] = None
    keywords: Optional[str] = None
    hashtags: Optional[str] = None
    naver_tv_url: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_key_points: Optional[list] = None

    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.images_caption is None:
            self.images_caption = []
        if self.ai_key_points is None:
            self.ai_key_points = []


class ArticleHandlerError(Exception):
    """Base exception for ArticleHandler errors"""
    pass


class ArticleHandler:
    """
    Handles article detail retrieval with translation and caching
    """
    
    def __init__(
        self,
        bigkinds_client: BigKindsClient,
        translation_service: TranslationService,
        cache_manager: CacheManager,
        dynamodb_client: DynamoDBClient
    ):
        """
        Initialize ArticleHandler with required services
        
        Args:
            bigkinds_client: Client for BigKinds API
            translation_service: Service for translation
            cache_manager: Manager for caching translations
            dynamodb_client: Client for DynamoDB storage
        """
        self.bigkinds_client = bigkinds_client
        self.translation_service = translation_service
        self.cache_manager = cache_manager
        self.dynamodb_client = dynamodb_client
    
    async def handle_article_detail(
        self,
        article_id: str
    ) -> ArticleDetailResponse:
        """
        Handle article detail request with translation and caching

        Args:
            article_id: BigKinds article ID

        Returns:
            ArticleDetailResponse with translated title and content

        Raises:
            ArticleHandlerError: If retrieval or translation fails with user-friendly message
        """
        try:
            # Validate article_id
            if not article_id or not article_id.strip():
                raise ArticleHandlerError("Article ID is required")

            # ONLY retrieve from DynamoDB - no BigKinds fallback
            cached_article = await self.dynamodb_client.get_article(article_id)
            if not cached_article:
                logger.warning(f"Article {article_id} not found in DynamoDB")
                raise ArticleHandlerError(
                    "Article not found. This article has not been processed yet."
                )

            logger.info(f"Retrieved article {article_id} from DynamoDB")
            return ArticleDetailResponse(
                news_id=cached_article['news_id'],
                title=cached_article['title_en'],
                content=cached_article['content_en'],
                published_at=cached_article['published_at'],
                provider=cached_article['provider'],
                category=cached_article.get('category', 'news'),
                slug=cached_article.get('slug'),
                byline=cached_article.get('byline'),
                byline_en=cached_article.get('byline_en'),
                original_link=cached_article.get('original_link'),
                images=cached_article.get('images', []),
                images_caption=cached_article.get('images_caption', []),
                meta_description=cached_article.get('meta_description', ''),
                keywords=cached_article.get('keywords', ''),
                hashtags=cached_article.get('hashtags', ''),
                naver_tv_url=cached_article.get('naver_tv_url', ''),
                ai_summary=cached_article.get('ai_summary', ''),
                ai_key_points=cached_article.get('ai_key_points', [])
            )



        except ArticleHandlerError:
            # Re-raise our own errors
            raise
        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Unexpected error in article handler: {e}", exc_info=True)
            raise ArticleHandlerError(
                "An unexpected error occurred. Please try again later."
            )

    async def handle_article_by_slug(
        self,
        slug: str
    ) -> ArticleDetailResponse:
        """
        Handle article detail request by SEO-friendly slug

        Args:
            slug: Article slug (e.g., 'samsung-reports-strong-q4-earnings')

        Returns:
            ArticleDetailResponse with translated title and content

        Raises:
            ArticleHandlerError: If retrieval fails with user-friendly message
        """
        try:
            # Validate slug
            if not slug or not slug.strip():
                raise ArticleHandlerError("Article slug is required")

            # Retrieve article by slug using GSI
            cached_article = await self.dynamodb_client.get_article_by_slug(slug)
            if not cached_article:
                logger.warning(f"Article with slug '{slug}' not found in DynamoDB")
                raise ArticleHandlerError(
                    "Article not found. This article may have been removed or the URL is incorrect."
                )

            logger.info(f"Retrieved article with slug '{slug}' from DynamoDB (news_id: {cached_article.get('news_id')})")
            return ArticleDetailResponse(
                news_id=cached_article['news_id'],
                title=cached_article['title_en'],
                content=cached_article['content_en'],
                published_at=cached_article['published_at'],
                provider=cached_article['provider'],
                category=cached_article.get('category', 'news'),
                slug=cached_article.get('slug'),
                byline=cached_article.get('byline'),
                byline_en=cached_article.get('byline_en'),
                original_link=cached_article.get('original_link'),
                images=cached_article.get('images', []),
                images_caption=cached_article.get('images_caption', []),
                meta_description=cached_article.get('meta_description', ''),
                keywords=cached_article.get('keywords', ''),
                hashtags=cached_article.get('hashtags', ''),
                naver_tv_url=cached_article.get('naver_tv_url', ''),
                ai_summary=cached_article.get('ai_summary', ''),
                ai_key_points=cached_article.get('ai_key_points', [])
            )

        except ArticleHandlerError:
            # Re-raise our own errors
            raise
        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Unexpected error in article slug handler: {e}", exc_info=True)
            raise ArticleHandlerError(
                "An unexpected error occurred. Please try again later."
            )


def lambda_handler(event: dict, context) -> dict:
    """
    AWS Lambda handler function for article detail requests
    
    Args:
        event: Lambda event containing article_id
        context: Lambda context
    
    Returns:
        API Gateway response dict
    """
    import asyncio
    from config import settings
    
    # Run async handler in event loop
    return asyncio.run(_async_handler(event, context))


async def _async_handler(event: dict, context) -> dict:
    """
    Async implementation of Lambda handler
    """
    from config import settings
    
    try:
        # Parse request
        path_parameters = event.get("pathParameters", {})
        article_id = path_parameters.get("article_id", "")
        
        if not article_id:
            import json
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": {
                        "code": "MISSING_ARTICLE_ID",
                        "message": "Article ID is required",
                        "retry_possible": False
                    }
                })
            }
        
        # Initialize services
        bigkinds_client = BigKindsClient(
            api_key=settings.bigkinds_api_key,
            base_url=settings.bigkinds_api_url
        )
        
        translation_service = TranslationService(
            model_id=settings.anthropic_model_id,
            anthropic_api_key=settings.anthropic_api_key
        )
        
        cache_manager = CacheManager(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            db=settings.redis_db,
            default_ttl=settings.cache_ttl
        )
        
        dynamodb_client = DynamoDBClient(
            table_name="seodaily-eng-articles-dev",
            region=settings.region
        )
        
        # Create handler and process request
        handler = ArticleHandler(
            bigkinds_client=bigkinds_client,
            translation_service=translation_service,
            cache_manager=cache_manager,
            dynamodb_client=dynamodb_client
        )
        
        response = await handler.handle_article_detail(article_id)
        
        # Clean up
        await bigkinds_client.close()
        await cache_manager.close()
        
        # Return success response
        import json
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "news_id": response.news_id,
                "title": response.title,
                "content": response.content,
                "published_at": response.published_at,
                "provider": response.provider,
                "category": response.category,
                "slug": response.slug,
                "byline": response.byline,
                "byline_en": response.byline_en,
                "original_link": response.original_link,
                "images": response.images,
                "images_caption": response.images_caption,
                "meta_description": response.meta_description,
                "keywords": response.keywords,
                "hashtags": response.hashtags,
                "naver_tv_url": response.naver_tv_url,
                "ai_summary": response.ai_summary,
                "ai_key_points": response.ai_key_points
            })
        }
    
    except ArticleHandlerError as e:
        import json
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": {
                    "code": "ARTICLE_ERROR",
                    "message": str(e),
                    "retry_possible": True
                }
            })
        }
    
    except Exception as e:
        logger.error(f"Lambda handler error: {e}", exc_info=True)
        import json
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "retry_possible": True
                }
            })
        }
