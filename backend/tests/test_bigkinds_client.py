"""
Property-based tests for BigKinds API client
Tests validation, HTTPS enforcement, and API request construction
"""
import pytest
from hypothesis import given, strategies as st, assume
from datetime import datetime, timedelta
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from clients.bigkinds_client import BigKindsClient, ValidationError, SearchResult, Article


# Custom strategies for date generation
@st.composite
def valid_date_string(draw):
    """Generate valid date strings in YYYY-MM-DD format"""
    year = draw(st.integers(min_value=2000, max_value=2030))
    month = draw(st.integers(min_value=1, max_value=12))
    day = draw(st.integers(min_value=1, max_value=28))  # Safe for all months
    return f"{year:04d}-{month:02d}-{day:02d}"


@st.composite
def invalid_date_string(draw):
    """Generate invalid date strings"""
    formats = [
        st.just("2025/01/01"),  # Wrong separator
        st.just("01-01-2025"),  # Wrong order
        st.just("2025-1-1"),    # Missing leading zeros
        st.just("not-a-date"),  # Invalid format
        st.just("2025-13-01"),  # Invalid month
        st.just("2025-01-32"),  # Invalid day
        st.just(""),            # Empty string
    ]
    return draw(st.one_of(*formats))


class TestBigKindsClientProperties:
    """Property-based tests for BigKinds client"""
    
    @given(st.text(min_size=1).filter(lambda x: x.strip()))
    def test_property_32_api_key_validation(self, api_key):
        """
        Feature: seodaily-eng, Property 32: API requests validate access key presence
        For any BigKinds API request construction, the access key must be present
        Validates: Requirements 8.1
        """
        # Valid API key should create client successfully
        client = BigKindsClient(api_key=api_key)
        assert client.api_key == api_key
    
    def test_property_32_empty_api_key_rejected(self):
        """
        Feature: seodaily-eng, Property 32: API requests validate access key presence
        Empty or whitespace-only API keys should be rejected
        Validates: Requirements 8.1
        """
        # Empty string
        with pytest.raises(ValidationError, match="API key is required"):
            BigKindsClient(api_key="")
        
        # Whitespace only
        with pytest.raises(ValidationError, match="API key is required"):
            BigKindsClient(api_key="   ")
    
    @given(valid_date_string(), valid_date_string())
    async def test_property_33_valid_date_format_accepted(self, date_from, date_until):
        """
        Feature: seodaily-eng, Property 33: Date format validation is enforced
        Valid dates in YYYY-MM-DD format should be accepted
        Validates: Requirements 8.2
        """
        client = BigKindsClient(api_key="test_key")
        
        # Mock the HTTP client
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "return_object": {
                "total_hits": 0,
                "documents": []
            }
        }
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            # Should not raise ValidationError
            result = await client.search_news(
                query="test",
                published_from=date_from,
                published_until=date_until
            )
            
            # Verify the request was made
            assert mock_post.called
            call_args = mock_post.call_args
            payload = call_args.kwargs['json']
            
            # Verify dates are included in the request
            assert payload['argument']['published_at']['from'] == date_from
            assert payload['argument']['published_at']['until'] == date_until
        
        await client.close()
    
    @given(invalid_date_string())
    async def test_property_33_invalid_date_format_rejected(self, invalid_date):
        """
        Feature: seodaily-eng, Property 33: Date format validation is enforced
        Invalid date formats should be rejected
        Validates: Requirements 8.2
        """
        client = BigKindsClient(api_key="test_key")
        
        # Test with invalid published_from
        with pytest.raises(ValidationError, match="Invalid date format"):
            await client.search_news(
                query="test",
                published_from=invalid_date,
                published_until="2025-01-01"
            )
        
        # Test with invalid published_until
        with pytest.raises(ValidationError, match="Invalid date format"):
            await client.search_news(
                query="test",
                published_from="2025-01-01",
                published_until=invalid_date
            )
        
        await client.close()
    
    @given(st.text())
    def test_property_42_https_enforcement(self, base_url_suffix):
        """
        Feature: seodaily-eng, Property 42: BigKinds API uses HTTPS
        For any BigKinds API request, the URL scheme should be "https"
        Validates: Requirements 10.1
        """
        # HTTPS URLs should be accepted
        https_url = f"https://api.example.com/{base_url_suffix}"
        client = BigKindsClient(api_key="test_key", base_url=https_url)
        assert client.base_url.startswith("https://")
    
    @given(st.text(min_size=1))
    def test_property_42_http_rejected(self, path):
        """
        Feature: seodaily-eng, Property 42: BigKinds API uses HTTPS
        HTTP (non-secure) URLs should be rejected
        Validates: Requirements 10.1
        """
        # HTTP URLs should be rejected
        http_url = f"http://api.example.com/{path}"
        with pytest.raises(ValidationError, match="must use HTTPS"):
            BigKindsClient(api_key="test_key", base_url=http_url)
    
    @given(
        st.text(min_size=1, max_size=100),
        valid_date_string(),
        valid_date_string()
    )
    async def test_property_1_query_triggers_search(self, query, date_from, date_until):
        """
        Feature: seodaily-eng, Property 1: Query translation triggers BigKinds search
        For any valid search query, the system should make a BigKinds API call
        Validates: Requirements 1.1
        """
        client = BigKindsClient(api_key="test_key")
        
        # Mock the HTTP client
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "return_object": {
                "total_hits": 5,
                "documents": [
                    {
                        "news_id": "test123",
                        "title": "Test Article",
                        "published_at": "2025-01-01",
                        "provider_name": "Test Provider",
                        "category": "Test Category"
                    }
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            # Execute search
            result = await client.search_news(
                query=query,
                published_from=date_from,
                published_until=date_until
            )
            
            # Verify API was called
            assert mock_post.called
            assert mock_post.call_count == 1
            
            # Verify the query was included in the request
            call_args = mock_post.call_args
            payload = call_args.kwargs['json']
            assert payload['argument']['query'] == query
            
            # Verify URL uses HTTPS
            called_url = call_args.args[0]
            assert called_url.startswith("https://")
        
        await client.close()
    
    @given(
        st.text(min_size=1, max_size=100),
        valid_date_string(),
        valid_date_string(),
        st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=5),
        st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=5)
    )
    async def test_property_5_date_filters_included(
        self, query, date_from, date_until, providers, categories
    ):
        """
        Feature: seodaily-eng, Property 5: Date filters are included in API requests
        For any valid date range selection, the BigKinds API request should include date filters
        Validates: Requirements 2.1
        """
        client = BigKindsClient(api_key="test_key")
        
        # Mock the HTTP client
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "return_object": {
                "total_hits": 0,
                "documents": []
            }
        }
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            # Execute search with filters
            result = await client.search_news(
                query=query,
                published_from=date_from,
                published_until=date_until,
                providers=providers,
                categories=categories
            )
            
            # Verify API was called
            assert mock_post.called
            
            # Verify date filters are included
            call_args = mock_post.call_args
            payload = call_args.kwargs['json']
            
            assert 'published_at' in payload['argument']
            assert payload['argument']['published_at']['from'] == date_from
            assert payload['argument']['published_at']['until'] == date_until
            
            # Verify optional filters are included when provided
            assert payload['argument']['provider'] == providers
            assert payload['argument']['category'] == categories
        
        await client.close()
    
    @given(st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10))
    async def test_get_article_detail_validates_api_key(self, news_ids):
        """
        Feature: seodaily-eng, Property 32: API requests validate access key presence
        Article detail requests should validate API key presence
        Validates: Requirements 8.1
        """
        client = BigKindsClient(api_key="test_key")
        
        # Mock the HTTP client
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "return_object": {
                "documents": []
            }
        }
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            # Execute article detail request
            result = await client.get_article_detail(news_ids=news_ids)
            
            # Verify API was called with access key
            assert mock_post.called
            call_args = mock_post.call_args
            payload = call_args.kwargs['json']
            assert 'access_key' in payload
            assert payload['access_key'] == "test_key"
        
        await client.close()
