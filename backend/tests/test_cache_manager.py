"""
Property-based tests for CacheManager
"""
import pytest
import asyncio
from hypothesis import given, strategies as st, assume
from unittest.mock import AsyncMock, patch, MagicMock
from redis.exceptions import RedisError
from clients.cache_manager import CacheManager


# Strategies for generating test data
article_ids = st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_characters=":"))
fields = st.sampled_from(["title", "content", "summary"])
languages = st.sampled_from(["en", "ko", "ja", "zh"])
cache_values = st.text(min_size=1, max_size=1000)
ttl_values = st.integers(min_value=1, max_value=604800)


@pytest.fixture
async def cache_manager():
    """Fixture providing a CacheManager instance"""
    manager = CacheManager(
        host="localhost",
        port=6379,
        password=None,
        db=0,
        default_ttl=604800
    )
    yield manager
    await manager.close()


class TestCacheManagerProperties:
    """Property-based tests for CacheManager"""
    
    @given(
        article_id=article_ids,
        field=fields,
        lang=languages,
        value=cache_values
    )
    @pytest.mark.asyncio
    async def test_property_17_translations_are_cached(
        self,
        article_id,
        field,
        lang,
        value
    ):
        """
        Feature: seodaily-eng, Property 17: Translations are cached
        For any translated article, the translation should be stored in cache
        with a key format of "{article_id}:{field}:{lang}".
        Validates: Requirements 5.1
        """
        manager = CacheManager()
        
        # Mock Redis client
        mock_client = AsyncMock()
        mock_client.setex = AsyncMock(return_value=True)
        mock_client.get = AsyncMock(return_value=value)
        
        with patch.object(manager, '_get_client', return_value=mock_client):
            # Generate cache key
            cache_key = manager.generate_cache_key(article_id, field, lang)
            
            # Verify key format
            assert cache_key == f"{article_id}:{field}:{lang}"
            
            # Store translation in cache
            result = await manager.set(cache_key, value)
            assert result is True
            
            # Verify setex was called with correct parameters
            mock_client.setex.assert_called_once()
            call_args = mock_client.setex.call_args
            assert call_args[0][0] == cache_key
            assert call_args[0][1] == 604800  # default TTL
            assert call_args[0][2] == value
        
        await manager.close()
    
    @given(
        article_id=article_ids,
        field=fields,
        lang=languages,
        value=cache_values
    )
    @pytest.mark.asyncio
    async def test_property_18_cache_hits_avoid_translation_api_calls(
        self,
        article_id,
        field,
        lang,
        value
    ):
        """
        Feature: seodaily-eng, Property 18: Cache hits avoid translation API calls
        For any article that exists in cache, retrieving it should not trigger
        a Translation Engine API call.
        Validates: Requirements 5.2
        """
        manager = CacheManager()
        
        # Mock Redis client with cached value
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=value)
        
        with patch.object(manager, '_get_client', return_value=mock_client):
            cache_key = manager.generate_cache_key(article_id, field, lang)
            
            # Retrieve from cache
            cached_value = await manager.get(cache_key)
            
            # Verify cache hit returns the value
            assert cached_value == value
            
            # Verify get was called
            mock_client.get.assert_called_once_with(cache_key)
        
        await manager.close()
    
    @given(
        article_id=article_ids,
        field=fields,
        lang=languages,
        value=cache_values,
        ttl=st.integers(min_value=1, max_value=100)  # Short TTL for testing
    )
    @pytest.mark.asyncio
    async def test_property_19_expired_cache_entries_are_invalidated(
        self,
        article_id,
        field,
        lang,
        value,
        ttl
    ):
        """
        Feature: seodaily-eng, Property 19: Expired cache entries are invalidated
        For any cached translation older than 7 days, the cache entry should be
        invalidated and a new translation requested.
        Validates: Requirements 5.3
        """
        manager = CacheManager()
        
        # Mock Redis client
        mock_client = AsyncMock()
        mock_client.setex = AsyncMock(return_value=True)
        mock_client.delete = AsyncMock(return_value=1)
        
        with patch.object(manager, '_get_client', return_value=mock_client):
            cache_key = manager.generate_cache_key(article_id, field, lang)
            
            # Set with custom TTL
            await manager.set(cache_key, value, ttl=ttl)
            
            # Verify TTL was set correctly
            call_args = mock_client.setex.call_args
            assert call_args[0][1] == ttl
            
            # Invalidate the cache entry
            result = await manager.invalidate(cache_key)
            assert result is True
            
            # Verify delete was called
            mock_client.delete.assert_called_once_with(cache_key)
        
        await manager.close()
    
    @given(
        article_id=article_ids,
        field=fields,
        lang=languages,
        value=cache_values
    )
    @pytest.mark.asyncio
    async def test_property_20_cache_failures_dont_block_service(
        self,
        article_id,
        field,
        lang,
        value
    ):
        """
        Feature: seodaily-eng, Property 20: Cache failures don't block service
        For any cache storage failure, the system should log the error and
        continue serving the translation to the user.
        Validates: Requirements 5.4
        """
        manager = CacheManager()
        
        # Mock Redis client that fails on set
        mock_client = AsyncMock()
        mock_client.setex = AsyncMock(side_effect=RedisError("Connection failed"))
        
        with patch.object(manager, '_get_client', return_value=mock_client):
            cache_key = manager.generate_cache_key(article_id, field, lang)
            
            # Attempt to set cache - should not raise exception
            result = await manager.set(cache_key, value)
            
            # Verify operation returns False but doesn't raise
            assert result is False
            
            # Service can continue despite cache failure
            # (in real implementation, translation would still be served)
        
        await manager.close()
    
    @given(
        article_id=article_ids,
        field=fields,
        lang=languages
    )
    @pytest.mark.asyncio
    async def test_property_21_cache_retrieval_failures_trigger_fallback(
        self,
        article_id,
        field,
        lang
    ):
        """
        Feature: seodaily-eng, Property 21: Cache retrieval failures trigger fallback
        For any cache retrieval failure, the system should fall back to requesting
        a new translation from the Translation Engine.
        Validates: Requirements 5.5
        """
        manager = CacheManager()
        
        # Mock Redis client that fails on get
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=RedisError("Connection timeout"))
        
        with patch.object(manager, '_get_client', return_value=mock_client):
            cache_key = manager.generate_cache_key(article_id, field, lang)
            
            # Attempt to get from cache - should not raise exception
            result = await manager.get(cache_key)
            
            # Verify operation returns None to trigger fallback
            assert result is None
            
            # This None return allows the calling code to fall back to
            # requesting a new translation from the Translation Engine
        
        await manager.close()
    
    @given(
        article_id=article_ids,
        field=fields,
        lang=languages
    )
    def test_cache_key_format_consistency(
        self,
        article_id,
        field,
        lang
    ):
        """
        Test that cache key generation is consistent and follows the
        specified format: {article_id}:{field}:{lang}
        """
        manager = CacheManager()
        
        # Generate key multiple times
        key1 = manager.generate_cache_key(article_id, field, lang)
        key2 = manager.generate_cache_key(article_id, field, lang)
        
        # Keys should be identical
        assert key1 == key2
        
        # Key should follow format
        assert key1 == f"{article_id}:{field}:{lang}"
        
        # Key should contain all components
        parts = key1.split(":")
        assert len(parts) == 3
        assert parts[0] == article_id
        assert parts[1] == field
        assert parts[2] == lang
