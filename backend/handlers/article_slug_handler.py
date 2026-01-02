"""
Article Slug Handler Lambda Function
Handles article retrieval by SEO-friendly slug
"""
import logging
import asyncio
import json
from handlers.article_handler import ArticleHandler, ArticleHandlerError
from clients.bigkinds_client import BigKindsClient
from clients.translation_service import TranslationService
from clients.cache_manager import CacheManager
from clients.dynamodb_client import DynamoDBClient

logger = logging.getLogger(__name__)


def lambda_handler(event: dict, context) -> dict:
    """
    AWS Lambda handler function for article detail requests by slug

    Args:
        event: Lambda event containing slug in path parameters
        context: Lambda context

    Returns:
        API Gateway response dict
    """
    # Run async handler in event loop
    return asyncio.run(_async_handler(event, context))


async def _async_handler(event: dict, context) -> dict:
    """
    Async implementation of Lambda handler for slug-based lookup
    """
    from config import settings

    try:
        # Parse request
        path_parameters = event.get("pathParameters", {})
        slug = path_parameters.get("slug", "")

        if not slug:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": {
                        "code": "MISSING_SLUG",
                        "message": "Article slug is required",
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

        # Use slug-based lookup
        response = await handler.handle_article_by_slug(slug)

        # Clean up
        await bigkinds_client.close()
        await cache_manager.close()

        # Return success response
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "public, max-age=3600"  # Cache for 1 hour
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
        return {
            "statusCode": 404 if "not found" in str(e).lower() else 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": {
                    "code": "ARTICLE_NOT_FOUND",
                    "message": str(e),
                    "retry_possible": False
                }
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
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "retry_possible": True
                }
            })
        }
