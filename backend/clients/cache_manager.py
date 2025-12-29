"""
Cache Manager for translation caching using Redis
"""
import logging
from typing import Optional
import redis.asyncio as redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages caching of translations using Redis.
    Provides get, set, invalidate operations with error handling and fallback logic.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: Optional[str] = None,
        db: int = 0,
        default_ttl: int = 604800  # 7 days in seconds
    ):
        """
        Initialize CacheManager with Redis connection parameters.
        
        Args:
            host: Redis host address
            port: Redis port number
            password: Redis password (optional)
            db: Redis database number
            default_ttl: Default time-to-live in seconds (7 days)
        """
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.default_ttl = default_ttl
        self._client: Optional[redis.Redis] = None
    
    async def _get_client(self) -> redis.Redis:
        """
        Get or create Redis client connection.
        
        Returns:
            Redis client instance
        """
        if self._client is None:
            self._client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
        return self._client
    
    async def get(self, key: str) -> Optional[str]:
        """
        Retrieve value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found, None otherwise
            
        Note:
            Returns None on cache failures to allow fallback logic
        """
        try:
            client = await self._get_client()
            value = await client.get(key)
            if value:
                logger.debug(f"Cache hit for key: {key}")
            else:
                logger.debug(f"Cache miss for key: {key}")
            return value
        except RedisError as e:
            logger.warning(f"Cache retrieval failed for key {key}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during cache retrieval for key {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Store value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default_ttl if not specified)
            
        Returns:
            True if successful, False otherwise
            
        Note:
            Failures are logged but don't raise exceptions to allow service continuity
        """
        try:
            client = await self._get_client()
            ttl_seconds = ttl if ttl is not None else self.default_ttl
            await client.setex(key, ttl_seconds, value)
            logger.debug(f"Cache set for key: {key} with TTL: {ttl_seconds}s")
            return True
        except RedisError as e:
            logger.warning(f"Cache storage failed for key {key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during cache storage for key {key}: {e}")
            return False
    
    async def invalidate(self, key: str) -> bool:
        """
        Invalidate (delete) cache entry.
        
        Args:
            key: Cache key to invalidate
            
        Returns:
            True if key was deleted, False otherwise
        """
        try:
            client = await self._get_client()
            result = await client.delete(key)
            if result > 0:
                logger.debug(f"Cache invalidated for key: {key}")
                return True
            else:
                logger.debug(f"Cache key not found for invalidation: {key}")
                return False
        except RedisError as e:
            logger.warning(f"Cache invalidation failed for key {key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during cache invalidation for key {key}: {e}")
            return False
    
    def generate_cache_key(
        self,
        article_id: str,
        field: str,
        lang: str
    ) -> str:
        """
        Generate cache key in standardized format.
        
        Args:
            article_id: Article identifier
            field: Field name (e.g., 'title', 'content')
            lang: Language code (e.g., 'en', 'ko')
            
        Returns:
            Cache key in format "{article_id}:{field}:{lang}"
        """
        return f"{article_id}:{field}:{lang}"
    
    async def close(self):
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
