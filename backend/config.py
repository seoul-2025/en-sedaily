"""
Configuration management using pydantic-settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # BigKinds API (Seoul Economic Daily only)
    bigkinds_api_key: str
    bigkinds_api_url: str = "https://tools.kinds.or.kr"
    
    # Anthropic API
    anthropic_api_key: str
    anthropic_model_id: str = "claude-opus-4-5-20251101"
    
    # AWS (kept for compatibility)
    region: str = "us-east-1"
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    # Redis Cache
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0
    cache_ttl: int = 604800  # 7 days
    
    # DynamoDB
    dynamodb_table_articles: str = "seodaily-eng-articles-dev"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
