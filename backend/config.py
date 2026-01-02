"""
Configuration management using environment variables
"""
import os
from typing import Optional


class Settings:
    """Application settings loaded from environment variables"""

    def __init__(self):
        # BigKinds API (Seoul Economic Daily only)
        self.bigkinds_api_key = os.environ.get('BIGKINDS_API_KEY', '')
        self.bigkinds_api_url = os.environ.get('BIGKINDS_API_URL', 'https://tools.kinds.or.kr')

        # Anthropic API (loaded from Secrets Manager in TranslationService)
        self.anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        self.anthropic_model_id = os.environ.get('ANTHROPIC_MODEL_ID', 'claude-opus-4-5-20251101')

        # AWS (kept for compatibility)
        self.region = os.environ.get('REGION', 'us-east-1')
        self.aws_region = os.environ.get('AWS_REGION', 'us-east-1')
        self.aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.bedrock_model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

        # Redis Cache
        self.redis_host = os.environ.get('REDIS_HOST', 'localhost')
        self.redis_port = int(os.environ.get('REDIS_PORT', '6379'))
        self.redis_password = os.environ.get('REDIS_PASSWORD')
        self.redis_db = int(os.environ.get('REDIS_DB', '0'))
        self.cache_ttl = int(os.environ.get('CACHE_TTL', '604800'))  # 7 days

        # DynamoDB
        self.dynamodb_table_articles = os.environ.get('DYNAMODB_TABLE_ARTICLES', 'seodaily-eng-articles-dev')

        # API Configuration
        self.api_host = os.environ.get('API_HOST', '0.0.0.0')
        self.api_port = int(os.environ.get('API_PORT', '8000'))
        self.log_level = os.environ.get('LOG_LEVEL', 'INFO')


settings = Settings()
