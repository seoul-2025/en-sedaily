"""
BigKinds API Client
Handles communication with the BigKinds news API
"""
import aiohttp
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import re
from .response_validator import ResponseValidator, ResponseValidationError


@dataclass
class Article:
    """Article data model"""
    news_id: str
    title: str
    content: Optional[str] = None
    published_at: str = ""
    provider: str = ""
    category: str = ""
    byline: Optional[str] = None
    original_link: Optional[str] = None
    images: List[str] = field(default_factory=list)
    images_caption: List[str] = field(default_factory=list)


@dataclass
class SearchResult:
    """Search result data model"""
    total_hits: int
    documents: List[Article]


class ValidationError(Exception):
    """Raised when request validation fails"""
    pass


class BigKindsClient:
    """
    Client for BigKinds API
    Handles news search and article detail retrieval
    """
    
    def __init__(self, api_key: str, base_url: str = "https://tools.kinds.or.kr"):
        """
        Initialize BigKinds client
        
        Args:
            api_key: BigKinds API access key
            base_url: Base URL for BigKinds API (must use HTTPS)
        
        Raises:
            ValidationError: If API key is missing or base_url doesn't use HTTPS
        """
        if not api_key or not api_key.strip():
            raise ValidationError("API key is required")
        
        if not base_url.startswith("https://"):
            raise ValidationError("Base URL must use HTTPS protocol")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        timeout = aiohttp.ClientTimeout(total=30.0)
        self.session = aiohttp.ClientSession(timeout=timeout)
    
    def _validate_date_format(self, date_str: str) -> bool:
        """
        Validate date format is YYYY-MM-DD
        
        Args:
            date_str: Date string to validate
        
        Returns:
            True if valid, False otherwise
        """
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(pattern, date_str):
            return False
        
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    async def search_news(
        self,
        query: str,
        published_from: str,
        published_until: str,
        providers: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        return_from: int = 0,
        return_size: int = 10,
        fields: Optional[List[str]] = None
    ) -> SearchResult:
        """
        Search news articles using BigKinds API
        
        Args:
            query: Search query (Korean text)
            published_from: Start date in YYYY-MM-DD format
            published_until: End date in YYYY-MM-DD format
            providers: List of news provider names to filter
            categories: List of categories to filter
            return_from: Starting index for pagination
            return_size: Number of results to return
        
        Returns:
            SearchResult containing total hits and list of articles
        
        Raises:
            ValidationError: If validation fails
            httpx.HTTPError: If API request fails
        """
        if not self.api_key or not self.api_key.strip():
            raise ValidationError("API key is required")
        
        if not self._validate_date_format(published_from):
            raise ValidationError(f"Invalid date format for published_from: {published_from}. Expected YYYY-MM-DD")
        
        if not self._validate_date_format(published_until):
            raise ValidationError(f"Invalid date format for published_until: {published_until}. Expected YYYY-MM-DD")
        
        # Use provided fields or default minimal fields
        if fields is None:
            fields = ["news_id", "published_at"]
        
        payload = {
            "access_key": self.api_key,
            "argument": {
                "query": query,
                "published_at": {
                    "from": published_from,
                    "until": published_until
                },
                "return_from": return_from,
                "return_size": return_size,
                "sort": {"date": "desc"},
                "fields": fields
            }
        }
        
        if providers:
            payload["argument"]["provider"] = providers
        
        if categories:
            payload["argument"]["category"] = categories
        
        url = f"{self.base_url}/search/news"
        async with self.session.post(url, json=payload) as response:
            response.raise_for_status()
            data = await response.json()
        
        # Check BigKinds API result code
        if data.get("result") != 0:
            error_msg = data.get("message", "Unknown error")
            raise ValidationError(f"BigKinds API error: {error_msg} (result={data.get('result')})")
        
        try:
            data = ResponseValidator.validate_and_sanitize_bigkinds_search(data)
        except ResponseValidationError as e:
            raise ValidationError(f"Invalid API response structure: {str(e)}")
        
        total_hits = data.get("return_object", {}).get("total_hits", 0)
        documents_data = data.get("return_object", {}).get("documents", [])
        
        articles = []
        for doc in documents_data:
            original_link = doc.get("provider_link_page") or doc.get("news_url")
            if original_link and original_link.startswith("http://"):
                original_link = original_link.replace("http://", "https://", 1)
            
            article = Article(
                news_id=doc.get("news_id", ""),
                title=doc.get("title", ""),
                content=doc.get("content"),
                published_at=doc.get("published_at", ""),
                provider=doc.get("provider", "") or doc.get("provider_name", ""),
                category=doc.get("category", "") or doc.get("category_name", ""),
                byline=doc.get("byline"),
                original_link=original_link,
                images=doc.get("images", []),
                images_caption=doc.get("images_caption", [])
            )
            articles.append(article)
        
        return SearchResult(total_hits=total_hits, documents=articles)
    
    async def get_article_detail(
        self,
        news_ids: List[str],
        fields: Optional[List[str]] = None
    ) -> List[Article]:
        """
        Get detailed article information by news IDs
        
        Args:
            news_ids: List of news IDs to retrieve
            fields: Optional list of fields to return
        
        Returns:
            List of Article objects with detailed information
        
        Raises:
            ValidationError: If validation fails
            httpx.HTTPError: If API request fails
        """
        if not self.api_key or not self.api_key.strip():
            raise ValidationError("API key is required")
        
        if not news_ids:
            raise ValidationError("At least one news_id is required")
        
        if fields is None:
            fields = [
                "news_id", "title", "content", "published_at",
                "provider_name", "category", "byline", "news_url",
                "images", "images_caption", "provider_link_page"
            ]
        
        payload = {
            "access_key": self.api_key,
            "argument": {
                "news_ids": news_ids,
                "fields": fields
            }
        }
        
        url = f"{self.base_url}/search/news"
        
        # Add delay to respect API rate limits
        import asyncio
        await asyncio.sleep(1)
        
        async with self.session.post(url, json=payload) as response:
            response.raise_for_status()
            data = await response.json()
        
        # Check BigKinds API result code
        if data.get("result") != 0:
            error_msg = data.get("message", "Unknown error")
            raise ValidationError(f"BigKinds API error: {error_msg} (result={data.get('result')})")
        
        try:
            data = ResponseValidator.validate_and_sanitize_bigkinds_detail(data)
        except ResponseValidationError as e:
            raise ValidationError(f"Invalid API response structure: {str(e)}")
        
        documents_data = data.get("return_object", {}).get("documents", [])
        
        articles = []
        for doc in documents_data:
            # ONLY use provider_link_page (short link format)
            original_link = doc.get("provider_link_page")
            
            # Convert http to https if link exists
            if original_link and original_link.startswith("http://"):
                original_link = original_link.replace("http://", "https://", 1)
            
            article = Article(
                news_id=doc.get("news_id", ""),
                title=doc.get("title", ""),
                content=doc.get("content"),
                published_at=doc.get("published_at", ""),
                provider=doc.get("provider_name", ""),
                category=doc.get("category", ""),
                byline=doc.get("byline"),
                original_link=original_link,
                images=doc.get("images", []),
                images_caption=doc.get("images_caption", [])
            )
            articles.append(article)
        
        return articles
    
    async def close(self):
        """Close the HTTP session"""
        await self.session.close()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
