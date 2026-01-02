"""
Property-based tests for ArticleHandler
Tests article retrieval, translation, caching, and error handling properties
"""
import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock, Mock

from handlers.article_handler import ArticleHandler, ArticleHandlerError, ArticleDetailResponse
from clients.bigkinds_client import Article, ValidationError
from clients.translation_service import TranslationError


# Test data generators
@st.composite
def article_id_strategy(draw):
    """Generate random article IDs"""
    # BigKinds article IDs typically follow pattern: provider_code.date_timestamp
    provider_code = draw(st.integers(min_value=10000000, max_value=99999999))
    date = draw(st.integers(min_value=20200101, max_value=20251231))
    timestamp = draw(st.integers(min_value=100000000, max_value=999999999))
    return f"{provider_code}.{date}{timestamp}"


@st.composite
def article_strategy(draw, article_id=None):
    """Generate random Article objects"""
    news_id = article_id if article_id else draw(article_id_strategy())
    title = draw(st.text(min_size=10, max_size=100))
    content = draw(st.text(min_size=50, max_size=500))
    published_at = draw(st.text(min_size=10, max_size=30))
    provider = draw(st.text(min_size=3, max_size=20))
    category = draw(st.text(min_size=3, max_size=20))
    
    # Optional fields
    byline = draw(st.one_of(st.none(), st.text(min_size=3, max_size=30)))
    original_link = draw(st.one_of(
        st.none(),
        st.text(min_size=10, max_size=50).map(lambda x: f"https://example.com/{x}")
    ))
    
    return Article(
        news_id=news_id,
        title=title,
        content=content,
        published_at=published_at,
        provider=provider,
        category=category,
        byline=byline,
        original_link=original_link,
        images=[],
        images_caption=[]
    )


# Property 10: Article click triggers content retrieval
# Feature: seodaily-eng, Property 10: Article click triggers content retrieval
@pytest.mark.asyncio
@given(
    article_id=article_id_strategy()
)
@settings(max_examples=100)
async def test_article_click_triggers_content_retrieval(article_id):
    """
    For any article ID, clicking the article should trigger a BigKinds API call to retrieve full content.
    Validates: Requirements 3.1
    """
    # Create mock services
    bigkinds_client = Mock()
    translation_service = Mock()
    cache_manager = Mock()
    
    # Generate article with full content
    article = Article(
        news_id=article_id,
        title="Test Article Title",
        content="Full article content goes here",
        published_at="2025-01-01T00:00:00.000+0900",
        provider="Test Provider",
        category="Test Category",
        byline="Test Reporter",
        original_link="https://example.com/article",
        images=[],
        images_caption=[]
    )
    
    # Mock BigKinds API to return article
    bigkinds_client.get_article_detail = AsyncMock(return_value=[article])
    
    # Mock translation service
    translation_service.translate = AsyncMock(side_effect=lambda text, **kwargs: f"Translated: {text}")
    
    # Mock cache manager (cache miss)
    cache_manager.get = AsyncMock(return_value=None)
    cache_manager.set = AsyncMock(return_value=True)
    cache_manager.generate_cache_key = Mock(side_effect=lambda aid, field, lang: f"{aid}:{field}:{lang}")
    
    # Create handler
    handler = ArticleHandler(bigkinds_client, translation_service, cache_manager)
    
    # Execute article detail request
    response = await handler.handle_article_detail(article_id)
    
    # Verify: BigKinds API was called with the article_id
    bigkinds_client.get_article_detail.assert_called_once()
    call_args = bigkinds_client.get_article_detail.call_args
    assert article_id in call_args.kwargs["news_ids"], \
        f"BigKinds API should be called with article_id {article_id}"
    
    # Verify: Response contains the article content
    assert response.news_id == article_id
    assert response.content is not None and len(response.content) > 0, \
        "Response should contain translated article content"


# Property 12: Translated articles include original links
# Feature: seodaily-eng, Property 12: Translated articles include original links
@pytest.mark.asyncio
@given(
    article_with_link=article_strategy()
)
@settings(max_examples=100)
async def test_translated_articles_include_original_links(article_with_link):
    """
    For any translated article display, the original article link should be present.
    Validates: Requirements 3.3
    """
    # Create mock services
    bigkinds_client = Mock()
    translation_service = Mock()
    cache_manager = Mock()
    
    # Mock BigKinds API to return article with original link
    bigkinds_client.get_article_detail = AsyncMock(return_value=[article_with_link])
    
    # Mock translation service
    translation_service.translate = AsyncMock(side_effect=lambda text, **kwargs: f"Translated: {text}")
    
    # Mock cache manager (cache miss)
    cache_manager.get = AsyncMock(return_value=None)
    cache_manager.set = AsyncMock(return_value=True)
    cache_manager.generate_cache_key = Mock(side_effect=lambda aid, field, lang: f"{aid}:{field}:{lang}")
    
    # Create handler
    handler = ArticleHandler(bigkinds_client, translation_service, cache_manager)
    
    # Execute article detail request
    response = await handler.handle_article_detail(article_with_link.news_id)
    
    # Verify: Response includes original link
    assert response.original_link == article_with_link.original_link, \
        "Translated article response should include the original article link"
    
    # If original article had a link, response should have it
    if article_with_link.original_link:
        assert response.original_link is not None, \
            "Original link should be preserved in response"
        assert response.original_link == article_with_link.original_link, \
            "Original link should match the source article link"


# Property 14: Article retrieval errors are displayed
# Feature: seodaily-eng, Property 14: Article retrieval errors are displayed
@pytest.mark.asyncio
@given(
    error_type=st.sampled_from(["not_found", "api_error", "validation_error", "translation_error"])
)
@settings(max_examples=100)
async def test_article_retrieval_errors_displayed(error_type):
    """
    For any article retrieval failure, an error message should be displayed to the user.
    Validates: Requirements 3.5
    """
    # Create mock services
    bigkinds_client = Mock()
    translation_service = Mock()
    cache_manager = Mock()
    
    # Mock cache manager
    cache_manager.get = AsyncMock(return_value=None)
    cache_manager.set = AsyncMock(return_value=True)
    cache_manager.generate_cache_key = Mock(side_effect=lambda aid, field, lang: f"{aid}:{field}:{lang}")
    
    # Configure mocks based on error type
    if error_type == "not_found":
        # Article not found
        bigkinds_client.get_article_detail = AsyncMock(return_value=[])
    elif error_type == "api_error":
        # API error
        bigkinds_client.get_article_detail = AsyncMock(side_effect=Exception("API connection failed"))
    elif error_type == "validation_error":
        # Validation error
        bigkinds_client.get_article_detail = AsyncMock(side_effect=ValidationError("Invalid article ID"))
    else:  # translation_error
        # Article retrieval succeeds but translation fails
        article = Article(
            news_id="test123",
            title="Test Title",
            content="Test Content",
            published_at="2025-01-01",
            provider="Provider",
            category="Category"
        )
        bigkinds_client.get_article_detail = AsyncMock(return_value=[article])
        translation_service.translate = AsyncMock(side_effect=TranslationError("Translation service unavailable"))
    
    # Create handler
    handler = ArticleHandler(bigkinds_client, translation_service, cache_manager)
    
    # Execute article detail request and expect error
    with pytest.raises(ArticleHandlerError) as exc_info:
        await handler.handle_article_detail("test_article_id")
    
    # Verify: Error message is user-friendly
    error_message = str(exc_info.value)
    
    # Should not contain technical details
    assert "Exception" not in error_message
    assert "Traceback" not in error_message
    assert "RuntimeError" not in error_message
    
    # Should contain helpful information
    assert len(error_message) > 0, "Error message should not be empty"
    
    # Verify error message is appropriate for error type
    if error_type == "not_found":
        assert "not found" in error_message.lower() or "invalid" in error_message.lower()
    elif error_type == "validation_error":
        assert "invalid" in error_message.lower()
    elif error_type == "translation_error":
        assert "translation" in error_message.lower() or "unavailable" in error_message.lower()
    else:  # api_error
        assert "try again" in error_message.lower() or "unavailable" in error_message.lower()


# Additional test: Cache hit avoids translation
@pytest.mark.asyncio
@given(
    article_id=article_id_strategy()
)
@settings(max_examples=100)
async def test_cache_hit_avoids_translation(article_id):
    """
    For any article that exists in cache, retrieving it should not trigger Translation Engine API calls.
    This validates caching behavior for article handler.
    """
    # Create mock services
    bigkinds_client = Mock()
    translation_service = Mock()
    cache_manager = Mock()
    
    # Generate article
    article = Article(
        news_id=article_id,
        title="Test Article Title",
        content="Full article content",
        published_at="2025-01-01",
        provider="Provider",
        category="Category",
        original_link="https://example.com/article"
    )
    
    # Mock BigKinds API
    bigkinds_client.get_article_detail = AsyncMock(return_value=[article])
    
    # Mock cache manager (cache hit for both title and content)
    async def mock_cache_get(key):
        if "title" in key:
            return "Cached Translated Title"
        elif "content" in key:
            return "Cached Translated Content"
        return None
    
    cache_manager.get = AsyncMock(side_effect=mock_cache_get)
    cache_manager.set = AsyncMock(return_value=True)
    cache_manager.generate_cache_key = Mock(side_effect=lambda aid, field, lang: f"{aid}:{field}:{lang}")
    
    # Mock translation service (should NOT be called)
    translation_service.translate = AsyncMock(side_effect=lambda text, **kwargs: f"Translated: {text}")
    
    # Create handler
    handler = ArticleHandler(bigkinds_client, translation_service, cache_manager)
    
    # Execute article detail request
    response = await handler.handle_article_detail(article_id)
    
    # Verify: Translation service was NOT called (cache hit)
    translation_service.translate.assert_not_called()
    
    # Verify: Response contains cached translations
    assert response.title == "Cached Translated Title"
    assert response.content == "Cached Translated Content"
    
    # Verify: Cache was checked
    assert cache_manager.get.call_count >= 2  # At least title and content


# Additional test: Cache miss triggers translation and storage
@pytest.mark.asyncio
@given(
    article_id=article_id_strategy()
)
@settings(max_examples=100)
async def test_cache_miss_triggers_translation_and_storage(article_id):
    """
    For any article not in cache, retrieving it should trigger translation and store result in cache.
    This validates cache storage behavior for article handler.
    """
    # Create mock services
    bigkinds_client = Mock()
    translation_service = Mock()
    cache_manager = Mock()
    
    # Generate article
    article = Article(
        news_id=article_id,
        title="Korean Title",
        content="Korean Content",
        published_at="2025-01-01",
        provider="Provider",
        category="Category"
    )
    
    # Mock BigKinds API
    bigkinds_client.get_article_detail = AsyncMock(return_value=[article])
    
    # Mock translation service
    translation_service.translate = AsyncMock(side_effect=lambda text, **kwargs: f"Translated: {text}")
    
    # Mock cache manager (cache miss)
    cache_manager.get = AsyncMock(return_value=None)
    cache_manager.set = AsyncMock(return_value=True)
    cache_manager.generate_cache_key = Mock(side_effect=lambda aid, field, lang: f"{aid}:{field}:{lang}")
    
    # Create handler
    handler = ArticleHandler(bigkinds_client, translation_service, cache_manager)
    
    # Execute article detail request
    response = await handler.handle_article_detail(article_id)
    
    # Verify: Translation service was called for both title and content
    assert translation_service.translate.call_count == 2
    
    # Verify: Translations were stored in cache
    assert cache_manager.set.call_count == 2
    
    # Verify: Cache keys were generated correctly
    cache_key_calls = [call.args for call in cache_manager.generate_cache_key.call_args_list]
    assert any(article_id in str(call) and "title" in str(call) for call in cache_key_calls)
    assert any(article_id in str(call) and "content" in str(call) for call in cache_key_calls)
