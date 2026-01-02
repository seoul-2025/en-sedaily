"""
Property-based tests for SearchHandler
Tests filtering, pagination, and error handling properties
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import AsyncMock, Mock
import math

from handlers.search_handler import SearchHandler, SearchFilters, SearchHandlerError
from clients.bigkinds_client import Article, SearchResult, ValidationError
from clients.translation_service import TranslationError


# Test data generators
@st.composite
def article_strategy(draw, provider=None, category=None):
    """Generate random Article objects"""
    news_id = draw(st.text(min_size=10, max_size=30, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"))))
    title = draw(st.text(min_size=5, max_size=100))
    published_at = draw(st.text(min_size=10, max_size=30))
    
    # Use provided provider/category or generate random
    article_provider = provider if provider else draw(st.text(min_size=3, max_size=20))
    article_category = category if category else draw(st.text(min_size=3, max_size=20))
    
    return Article(
        news_id=news_id,
        title=title,
        published_at=published_at,
        provider=article_provider,
        category=article_category
    )


@st.composite
def search_filters_strategy(draw, providers=None, categories=None):
    """Generate random SearchFilters"""
    year = draw(st.integers(min_value=2020, max_value=2025))
    month_from = draw(st.integers(min_value=1, max_value=12))
    month_until = draw(st.integers(min_value=month_from, max_value=12))
    
    published_from = f"{year}-{month_from:02d}-01"
    published_until = f"{year}-{month_until:02d}-28"
    
    filter_providers = providers if providers is not None else draw(st.lists(st.text(min_size=3, max_size=20), max_size=5))
    filter_categories = categories if categories is not None else draw(st.lists(st.text(min_size=3, max_size=20), max_size=5))
    
    return SearchFilters(
        published_from=published_from,
        published_until=published_until,
        providers=filter_providers,
        categories=filter_categories
    )


# Property 6: Provider filtering is accurate
# Feature: seodaily-eng, Property 6: Provider filtering is accurate
@pytest.mark.asyncio
@given(
    selected_providers=st.lists(st.text(min_size=3, max_size=20), min_size=1, max_size=3, unique=True),
    num_articles=st.integers(min_value=1, max_value=20)
)
@settings(max_examples=100)
async def test_provider_filtering_accuracy(selected_providers, num_articles):
    """
    For any set of selected news providers, all returned articles should be from those providers only.
    Validates: Requirements 2.2
    """
    # Create mock services
    bigkinds_client = Mock()
    translation_service = Mock()
    cache_manager = Mock()
    
    # Generate articles from selected providers only
    articles = []
    for i in range(num_articles):
        provider = selected_providers[i % len(selected_providers)]
        article = Article(
            news_id=f"article_{i}",
            title=f"Title {i}",
            published_at="2025-01-01",
            provider=provider,
            category="Category"
        )
        articles.append(article)
    
    # Mock BigKinds API response
    search_result = SearchResult(total_hits=num_articles, documents=articles)
    bigkinds_client.search_news = AsyncMock(return_value=search_result)
    
    # Mock translation service
    translation_service.translate = AsyncMock(side_effect=lambda text, **kwargs: f"Translated: {text}")
    
    # Mock cache manager
    cache_manager.get = AsyncMock(return_value=None)
    cache_manager.set = AsyncMock(return_value=True)
    cache_manager.generate_cache_key = Mock(side_effect=lambda aid, field, lang: f"{aid}:{field}:{lang}")
    
    # Create handler
    handler = SearchHandler(bigkinds_client, translation_service, cache_manager)
    
    # Create filters with selected providers
    filters = SearchFilters(
        published_from="2025-01-01",
        published_until="2025-01-31",
        providers=selected_providers,
        categories=[]
    )
    
    # Execute search
    response = await handler.handle_search("test query", filters, page=1, page_size=10)
    
    # Verify: All returned articles should be from selected providers
    for article in response.articles:
        assert article.provider in selected_providers, \
            f"Article provider '{article.provider}' not in selected providers {selected_providers}"
    
    # Verify: BigKinds API was called with correct provider filter
    bigkinds_client.search_news.assert_called_once()
    call_kwargs = bigkinds_client.search_news.call_args.kwargs
    assert call_kwargs["providers"] == selected_providers


# Property 7: Category filtering is accurate
# Feature: seodaily-eng, Property 7: Category filtering is accurate
@pytest.mark.asyncio
@given(
    selected_categories=st.lists(st.text(min_size=3, max_size=20), min_size=1, max_size=3, unique=True),
    num_articles=st.integers(min_value=1, max_value=20)
)
@settings(max_examples=100)
async def test_category_filtering_accuracy(selected_categories, num_articles):
    """
    For any set of selected categories, all returned articles should belong to those categories only.
    Validates: Requirements 2.3
    """
    # Create mock services
    bigkinds_client = Mock()
    translation_service = Mock()
    cache_manager = Mock()
    
    # Generate articles from selected categories only
    articles = []
    for i in range(num_articles):
        category = selected_categories[i % len(selected_categories)]
        article = Article(
            news_id=f"article_{i}",
            title=f"Title {i}",
            published_at="2025-01-01",
            provider="Provider",
            category=category
        )
        articles.append(article)
    
    # Mock BigKinds API response
    search_result = SearchResult(total_hits=num_articles, documents=articles)
    bigkinds_client.search_news = AsyncMock(return_value=search_result)
    
    # Mock translation service
    translation_service.translate = AsyncMock(side_effect=lambda text, **kwargs: f"Translated: {text}")
    
    # Mock cache manager
    cache_manager.get = AsyncMock(return_value=None)
    cache_manager.set = AsyncMock(return_value=True)
    cache_manager.generate_cache_key = Mock(side_effect=lambda aid, field, lang: f"{aid}:{field}:{lang}")
    
    # Create handler
    handler = SearchHandler(bigkinds_client, translation_service, cache_manager)
    
    # Create filters with selected categories
    filters = SearchFilters(
        published_from="2025-01-01",
        published_until="2025-01-31",
        providers=[],
        categories=selected_categories
    )
    
    # Execute search
    response = await handler.handle_search("test query", filters, page=1, page_size=10)
    
    # Verify: All returned articles should belong to selected categories
    for article in response.articles:
        assert article.category in selected_categories, \
            f"Article category '{article.category}' not in selected categories {selected_categories}"
    
    # Verify: BigKinds API was called with correct category filter
    bigkinds_client.search_news.assert_called_once()
    call_kwargs = bigkinds_client.search_news.call_args.kwargs
    assert call_kwargs["categories"] == selected_categories


# Property 8: Multiple filters combine correctly
# Feature: seodaily-eng, Property 8: Multiple filters combine correctly
@pytest.mark.asyncio
@given(
    selected_providers=st.lists(st.text(min_size=3, max_size=20), min_size=1, max_size=3, unique=True),
    selected_categories=st.lists(st.text(min_size=3, max_size=20), min_size=1, max_size=3, unique=True),
    num_articles=st.integers(min_value=1, max_value=20)
)
@settings(max_examples=100)
async def test_multiple_filters_combine_correctly(selected_providers, selected_categories, num_articles):
    """
    For any combination of filters (date, provider, category), the API request should include all selected filters.
    Validates: Requirements 2.4
    """
    # Create mock services
    bigkinds_client = Mock()
    translation_service = Mock()
    cache_manager = Mock()
    
    # Generate articles matching all filters
    articles = []
    for i in range(num_articles):
        provider = selected_providers[i % len(selected_providers)]
        category = selected_categories[i % len(selected_categories)]
        article = Article(
            news_id=f"article_{i}",
            title=f"Title {i}",
            published_at="2025-01-15",
            provider=provider,
            category=category
        )
        articles.append(article)
    
    # Mock BigKinds API response
    search_result = SearchResult(total_hits=num_articles, documents=articles)
    bigkinds_client.search_news = AsyncMock(return_value=search_result)
    
    # Mock translation service
    translation_service.translate = AsyncMock(side_effect=lambda text, **kwargs: f"Translated: {text}")
    
    # Mock cache manager
    cache_manager.get = AsyncMock(return_value=None)
    cache_manager.set = AsyncMock(return_value=True)
    cache_manager.generate_cache_key = Mock(side_effect=lambda aid, field, lang: f"{aid}:{field}:{lang}")
    
    # Create handler
    handler = SearchHandler(bigkinds_client, translation_service, cache_manager)
    
    # Create filters with multiple filter types
    filters = SearchFilters(
        published_from="2025-01-01",
        published_until="2025-01-31",
        providers=selected_providers,
        categories=selected_categories
    )
    
    # Execute search
    response = await handler.handle_search("test query", filters, page=1, page_size=10)
    
    # Verify: BigKinds API was called with ALL filters
    bigkinds_client.search_news.assert_called_once()
    call_kwargs = bigkinds_client.search_news.call_args.kwargs
    
    # Check date filters
    assert call_kwargs["published_from"] == "2025-01-01"
    assert call_kwargs["published_until"] == "2025-01-31"
    
    # Check provider filter
    assert call_kwargs["providers"] == selected_providers
    
    # Check category filter
    assert call_kwargs["categories"] == selected_categories
    
    # Verify: All returned articles match ALL filters
    for article in response.articles:
        assert article.provider in selected_providers
        assert article.category in selected_categories
        # Date is within range (simplified check)
        assert "2025-01" in article.published_at


# Property 15: Large result sets are paginated
# Feature: seodaily-eng, Property 15: Large result sets are paginated
@pytest.mark.asyncio
@given(
    total_results=st.integers(min_value=11, max_value=100),
    page_size=st.integers(min_value=5, max_value=20),
    page_number=st.integers(min_value=1, max_value=10)
)
@settings(max_examples=100)
async def test_large_result_sets_paginated(total_results, page_size, page_number):
    """
    For any search result with more than page_size articles, the results should be divided into pages correctly.
    Validates: Requirements 4.1
    """
    # Calculate expected total pages
    expected_total_pages = math.ceil(total_results / page_size)
    
    # Skip if page_number exceeds total pages
    assume(page_number <= expected_total_pages)
    
    # Create mock services
    bigkinds_client = Mock()
    translation_service = Mock()
    cache_manager = Mock()
    
    # Calculate how many articles should be on this page
    expected_return_from = (page_number - 1) * page_size
    articles_on_page = min(page_size, total_results - expected_return_from)
    
    # Generate articles for this page
    articles = []
    for i in range(articles_on_page):
        article = Article(
            news_id=f"article_{expected_return_from + i}",
            title=f"Title {expected_return_from + i}",
            published_at="2025-01-01",
            provider="Provider",
            category="Category"
        )
        articles.append(article)
    
    # Mock BigKinds API response
    search_result = SearchResult(total_hits=total_results, documents=articles)
    bigkinds_client.search_news = AsyncMock(return_value=search_result)
    
    # Mock translation service
    translation_service.translate = AsyncMock(side_effect=lambda text, **kwargs: f"Translated: {text}")
    
    # Mock cache manager
    cache_manager.get = AsyncMock(return_value=None)
    cache_manager.set = AsyncMock(return_value=True)
    cache_manager.generate_cache_key = Mock(side_effect=lambda aid, field, lang: f"{aid}:{field}:{lang}")
    
    # Create handler
    handler = SearchHandler(bigkinds_client, translation_service, cache_manager)
    
    # Create filters
    filters = SearchFilters(
        published_from="2025-01-01",
        published_until="2025-01-31",
        providers=[],
        categories=[]
    )
    
    # Execute search with pagination
    response = await handler.handle_search("test query", filters, page=page_number, page_size=page_size)
    
    # Verify pagination metadata
    assert response.total_hits == total_results
    assert response.page == page_number
    assert response.page_size == page_size
    assert response.total_pages == expected_total_pages
    
    # Verify correct number of articles returned
    assert len(response.articles) == articles_on_page
    
    # Verify BigKinds API was called with correct pagination parameters
    bigkinds_client.search_news.assert_called_once()
    call_kwargs = bigkinds_client.search_news.call_args.kwargs
    assert call_kwargs["return_from"] == expected_return_from
    assert call_kwargs["return_size"] == page_size


# Property 22: API errors produce user-friendly messages
# Feature: seodaily-eng, Property 22: API errors produce user-friendly messages
@pytest.mark.asyncio
@given(
    error_type=st.sampled_from(["network", "validation", "unexpected"])
)
@settings(max_examples=100)
async def test_api_errors_produce_user_friendly_messages(error_type):
    """
    For any BigKinds API error response, a user-friendly error message should be displayed.
    Validates: Requirements 6.1
    """
    # Create mock services
    bigkinds_client = Mock()
    translation_service = Mock()
    cache_manager = Mock()
    
    # Mock translation service (successful)
    translation_service.translate = AsyncMock(return_value="Translated query")
    
    # Mock cache manager
    cache_manager.get = AsyncMock(return_value=None)
    cache_manager.set = AsyncMock(return_value=True)
    cache_manager.generate_cache_key = Mock(side_effect=lambda aid, field, lang: f"{aid}:{field}:{lang}")
    
    # Mock BigKinds API to raise different error types
    if error_type == "network":
        bigkinds_client.search_news = AsyncMock(side_effect=Exception("Network timeout"))
    elif error_type == "validation":
        bigkinds_client.search_news = AsyncMock(side_effect=ValidationError("Invalid date format"))
    else:  # unexpected
        bigkinds_client.search_news = AsyncMock(side_effect=RuntimeError("Unexpected error"))
    
    # Create handler
    handler = SearchHandler(bigkinds_client, translation_service, cache_manager)
    
    # Create filters
    filters = SearchFilters(
        published_from="2025-01-01",
        published_until="2025-01-31",
        providers=[],
        categories=[]
    )
    
    # Execute search and expect error
    with pytest.raises(SearchHandlerError) as exc_info:
        await handler.handle_search("test query", filters, page=1, page_size=10)
    
    # Verify error message is user-friendly (not technical)
    error_message = str(exc_info.value)
    
    # Should not contain technical details like stack traces or internal error codes
    assert "Exception" not in error_message
    assert "RuntimeError" not in error_message
    assert "Traceback" not in error_message
    
    # Should contain helpful guidance
    if error_type == "validation":
        assert "Invalid" in error_message or "parameters" in error_message
    else:
        assert "try again" in error_message.lower() or "unavailable" in error_message.lower()
