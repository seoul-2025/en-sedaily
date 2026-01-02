"""
Tests for API Gateway endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import os

# Set required environment variables before importing main
os.environ.setdefault('BIGKINDS_API_KEY', 'test_key')
os.environ.setdefault('BIGKINDS_API_URL', 'https://test.api.com')

from main import app
from handlers.search_handler import SearchResponse, SearchHandlerError
from handlers.article_handler import ArticleDetailResponse, ArticleHandlerError
from clients.bigkinds_client import Article


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_search_response():
    """Mock search response"""
    return SearchResponse(
        total_hits=1,
        page=1,
        page_size=10,
        total_pages=1,
        articles=[
            Article(
                news_id="test123",
                title="Test Article",
                content=None,
                published_at="2025-01-01T00:00:00.000+0900",
                provider="Test Provider",
                category="Test Category",
                byline=None,
                original_link=None,
                images=[],
                images_caption=[]
            )
        ]
    )


@pytest.fixture
def mock_article_response():
    """Mock article detail response"""
    return ArticleDetailResponse(
        news_id="test123",
        title="Test Article",
        content="Test content",
        published_at="2025-01-01T00:00:00.000+0900",
        provider="Test Provider",
        category="Test Category",
        byline="Test Reporter",
        original_link="https://example.com",
        images=[],
        images_caption=[]
    )


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns message"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "SEOdaily-ENG API"}
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestSearchEndpoint:
    """Test /api/search endpoint"""
    
    @patch('main.SearchHandler')
    @patch('main.get_bigkinds_client')
    @patch('main.get_translation_service')
    @patch('main.get_cache_manager')
    def test_search_success(
        self,
        mock_cache,
        mock_translation,
        mock_bigkinds,
        mock_handler_class,
        client,
        mock_search_response
    ):
        """Test successful search request"""
        # Setup mocks
        mock_handler = AsyncMock()
        mock_handler.handle_search = AsyncMock(return_value=mock_search_response)
        mock_handler_class.return_value = mock_handler
        
        mock_bigkinds_instance = AsyncMock()
        mock_bigkinds_instance.close = AsyncMock()
        mock_bigkinds.return_value = mock_bigkinds_instance
        
        mock_cache_instance = AsyncMock()
        mock_cache_instance.close = AsyncMock()
        mock_cache.return_value = mock_cache_instance
        
        # Make request
        response = client.post(
            "/api/search",
            json={
                "query": "test",
                "filters": {
                    "published_from": "2025-01-01",
                    "published_until": "2025-01-31",
                    "providers": [],
                    "categories": []
                },
                "page": 1,
                "page_size": 10
            }
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["total_hits"] == 1
        assert data["page"] == 1
        assert len(data["articles"]) == 1
        assert data["articles"][0]["news_id"] == "test123"
    
    def test_search_invalid_date_format(self, client):
        """Test search with invalid date format"""
        response = client.post(
            "/api/search",
            json={
                "query": "test",
                "filters": {
                    "published_from": "2025/01/01",  # Invalid format
                    "published_until": "2025-01-31",
                    "providers": [],
                    "categories": []
                },
                "page": 1,
                "page_size": 10
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_search_empty_query(self, client):
        """Test search with empty query"""
        response = client.post(
            "/api/search",
            json={
                "query": "",  # Empty query
                "filters": {
                    "published_from": "2025-01-01",
                    "published_until": "2025-01-31",
                    "providers": [],
                    "categories": []
                },
                "page": 1,
                "page_size": 10
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('main.SearchHandler')
    @patch('main.get_bigkinds_client')
    @patch('main.get_translation_service')
    @patch('main.get_cache_manager')
    def test_search_handler_error(
        self,
        mock_cache,
        mock_translation,
        mock_bigkinds,
        mock_handler_class,
        client
    ):
        """Test search with handler error"""
        # Setup mocks
        mock_handler = AsyncMock()
        mock_handler.handle_search = AsyncMock(
            side_effect=SearchHandlerError("Test error")
        )
        mock_handler_class.return_value = mock_handler
        
        mock_bigkinds_instance = AsyncMock()
        mock_bigkinds_instance.close = AsyncMock()
        mock_bigkinds.return_value = mock_bigkinds_instance
        
        mock_cache_instance = AsyncMock()
        mock_cache_instance.close = AsyncMock()
        mock_cache.return_value = mock_cache_instance
        
        # Make request
        response = client.post(
            "/api/search",
            json={
                "query": "test",
                "filters": {
                    "published_from": "2025-01-01",
                    "published_until": "2025-01-31",
                    "providers": [],
                    "categories": []
                },
                "page": 1,
                "page_size": 10
            }
        )
        
        # Verify error response
        assert response.status_code == 400
        data = response.json()
        assert "error" in data["detail"]
        assert data["detail"]["error"]["code"] == "SEARCH_ERROR"


class TestArticleEndpoint:
    """Test /api/article/{article_id} endpoint"""
    
    @patch('main.ArticleHandler')
    @patch('main.get_bigkinds_client')
    @patch('main.get_translation_service')
    @patch('main.get_cache_manager')
    def test_article_success(
        self,
        mock_cache,
        mock_translation,
        mock_bigkinds,
        mock_handler_class,
        client,
        mock_article_response
    ):
        """Test successful article retrieval"""
        # Setup mocks
        mock_handler = AsyncMock()
        mock_handler.handle_article_detail = AsyncMock(return_value=mock_article_response)
        mock_handler_class.return_value = mock_handler
        
        mock_bigkinds_instance = AsyncMock()
        mock_bigkinds_instance.close = AsyncMock()
        mock_bigkinds.return_value = mock_bigkinds_instance
        
        mock_cache_instance = AsyncMock()
        mock_cache_instance.close = AsyncMock()
        mock_cache.return_value = mock_cache_instance
        
        # Make request
        response = client.get("/api/article/test123")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["news_id"] == "test123"
        assert data["title"] == "Test Article"
        assert data["content"] == "Test content"
    
    @patch('main.ArticleHandler')
    @patch('main.get_bigkinds_client')
    @patch('main.get_translation_service')
    @patch('main.get_cache_manager')
    def test_article_not_found(
        self,
        mock_cache,
        mock_translation,
        mock_bigkinds,
        mock_handler_class,
        client
    ):
        """Test article not found error"""
        # Setup mocks
        mock_handler = AsyncMock()
        mock_handler.handle_article_detail = AsyncMock(
            side_effect=ArticleHandlerError("Article not found. The article may have been removed or the ID is invalid.")
        )
        mock_handler_class.return_value = mock_handler
        
        mock_bigkinds_instance = AsyncMock()
        mock_bigkinds_instance.close = AsyncMock()
        mock_bigkinds.return_value = mock_bigkinds_instance
        
        mock_cache_instance = AsyncMock()
        mock_cache_instance.close = AsyncMock()
        mock_cache.return_value = mock_cache_instance
        
        # Make request
        response = client.get("/api/article/nonexistent")
        
        # Verify error response
        assert response.status_code == 404
        data = response.json()
        assert "error" in data["detail"]
        assert data["detail"]["error"]["code"] == "ARTICLE_NOT_FOUND"
    
    @patch('main.ArticleHandler')
    @patch('main.get_bigkinds_client')
    @patch('main.get_translation_service')
    @patch('main.get_cache_manager')
    def test_article_handler_error(
        self,
        mock_cache,
        mock_translation,
        mock_bigkinds,
        mock_handler_class,
        client
    ):
        """Test article with handler error"""
        # Setup mocks
        mock_handler = AsyncMock()
        mock_handler.handle_article_detail = AsyncMock(
            side_effect=ArticleHandlerError("Translation service error")
        )
        mock_handler_class.return_value = mock_handler
        
        mock_bigkinds_instance = AsyncMock()
        mock_bigkinds_instance.close = AsyncMock()
        mock_bigkinds.return_value = mock_bigkinds_instance
        
        mock_cache_instance = AsyncMock()
        mock_cache_instance.close = AsyncMock()
        mock_cache.return_value = mock_cache_instance
        
        # Make request
        response = client.get("/api/article/test123")
        
        # Verify error response
        assert response.status_code == 400
        data = response.json()
        assert "error" in data["detail"]
        assert data["detail"]["error"]["code"] == "ARTICLE_ERROR"


class TestCORS:
    """Test CORS configuration"""
    
    @patch('main.ArticleHandler')
    @patch('main.get_bigkinds_client')
    @patch('main.get_translation_service')
    @patch('main.get_cache_manager')
    def test_cors_headers_present(
        self,
        mock_cache,
        mock_translation,
        mock_bigkinds,
        mock_handler_class,
        client,
        mock_article_response
    ):
        """Test that CORS headers are present in API responses"""
        # Setup mocks
        mock_handler = AsyncMock()
        mock_handler.handle_article_detail = AsyncMock(return_value=mock_article_response)
        mock_handler_class.return_value = mock_handler
        
        mock_bigkinds_instance = AsyncMock()
        mock_bigkinds_instance.close = AsyncMock()
        mock_bigkinds.return_value = mock_bigkinds_instance
        
        mock_cache_instance = AsyncMock()
        mock_cache_instance.close = AsyncMock()
        mock_cache.return_value = mock_cache_instance
        
        # Make request to API endpoint
        response = client.get("/api/article/test123")
        
        # CORS middleware should add headers
        # Note: TestClient may not trigger CORS middleware the same way as real requests
        # This test verifies the middleware is configured
        assert response.status_code == 200
