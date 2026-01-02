"""
Property-based tests for environment configuration
Feature: seodaily-eng, Property 44: API keys are loaded from environment
"""
import pytest
import os
from hypothesis import given, strategies as st, settings
from unittest.mock import patch
import importlib
import sys


@given(
    bigkinds_key=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=10, max_size=100),
    aws_access_key=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=10, max_size=100),
    aws_secret_key=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=10, max_size=100)
)
@settings(max_examples=100)
def test_api_keys_loaded_from_environment(bigkinds_key, aws_access_key, aws_secret_key):
    """
    Feature: seodaily-eng, Property 44: API keys are loaded from environment
    
    For any API key usage, the key should be loaded from environment variables,
    not hardcoded.
    
    Validates: Requirements 10.3
    """
    # Set environment variables
    env_vars = {
        'BIGKINDS_API_KEY': bigkinds_key,
        'AWS_ACCESS_KEY_ID': aws_access_key,
        'AWS_SECRET_ACCESS_KEY': aws_secret_key,
        'BIGKINDS_API_URL': 'https://api.bigkinds.or.kr',
        'AWS_REGION': 'us-east-1',
        'REDIS_HOST': 'localhost',
        'REDIS_PORT': '6379'
    }
    
    with patch.dict(os.environ, env_vars, clear=False):
        # Import Settings class dynamically to avoid module-level instantiation issues
        if 'config' in sys.modules:
            del sys.modules['config']
        
        from config import Settings
        
        # Create a new Settings instance that will load from environment
        test_settings = Settings()
        
        # Verify that API keys are loaded from environment variables
        assert test_settings.bigkinds_api_key == bigkinds_key
        assert test_settings.aws_access_key_id == aws_access_key
        assert test_settings.aws_secret_access_key == aws_secret_key
        
        # Verify that the keys are not hardcoded (they match what we set in env)
        assert test_settings.bigkinds_api_key != ""
        assert test_settings.aws_access_key_id != ""
        assert test_settings.aws_secret_access_key != ""


def test_missing_required_api_key_raises_error():
    """
    Test that missing required API keys raise validation errors
    
    This test verifies that the Settings class requires API keys from environment
    """
    # Set minimal environment without required BIGKINDS_API_KEY
    env_vars = {
        'AWS_REGION': 'us-east-1',
        'REDIS_HOST': 'localhost',
        'REDIS_PORT': '6379'
    }
    
    # We need to test that Settings requires the key, but since config.py
    # instantiates settings at module level, we test by trying to import
    # the module without the required key set
    with patch.dict(os.environ, env_vars, clear=True):
        # Remove config module from cache to force re-import
        if 'config' in sys.modules:
            del sys.modules['config']
        
        # Attempting to import config without required key should raise error
        with pytest.raises(Exception):  # pydantic will raise ValidationError
            import config


@given(
    redis_host=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=5, max_size=50),
    redis_port=st.integers(min_value=1024, max_value=65535)
)
@settings(max_examples=100)
def test_service_configuration_loaded_from_environment(redis_host, redis_port):
    """
    Test that service configuration (Redis, etc.) is loaded from environment
    """
    env_vars = {
        'BIGKINDS_API_KEY': 'test_key_12345',
        'REDIS_HOST': redis_host,
        'REDIS_PORT': str(redis_port),
        'AWS_REGION': 'us-east-1'
    }
    
    with patch.dict(os.environ, env_vars, clear=False):
        # Import Settings class dynamically
        if 'config' in sys.modules:
            del sys.modules['config']
        
        from config import Settings
        
        test_settings = Settings()
        
        # Verify service configuration is loaded from environment
        assert test_settings.redis_host == redis_host
        assert test_settings.redis_port == redis_port


def test_no_hardcoded_secrets_in_config_module():
    """
    Test that the config module itself doesn't contain hardcoded secrets
    """
    import config
    import inspect
    
    # Get the source code of the config module
    source = inspect.getsource(config)
    
    # Check that there are no obvious hardcoded API keys or secrets
    # (This is a simple check - real secrets would be more complex)
    suspicious_patterns = [
        'api_key = "',
        'api_key="',
        "api_key = '",
        "api_key='",
        'secret = "',
        'secret="',
        "secret = '",
        "secret='",
        'password = "',
        'password="',
        "password = '",
        "password='"
    ]
    
    for pattern in suspicious_patterns:
        assert pattern not in source.lower(), f"Found suspicious hardcoded pattern: {pattern}"


@given(
    bedrock_model=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=10, max_size=100),
    aws_region=st.sampled_from(['us-east-1', 'us-west-2', 'eu-west-1', 'ap-northeast-1'])
)
@settings(max_examples=100)
def test_aws_configuration_loaded_from_environment(bedrock_model, aws_region):
    """
    Test that AWS-specific configuration is loaded from environment
    """
    env_vars = {
        'BIGKINDS_API_KEY': 'test_key_12345',
        'BEDROCK_MODEL_ID': bedrock_model,
        'AWS_REGION': aws_region,
        'REDIS_HOST': 'localhost',
        'REDIS_PORT': '6379'
    }
    
    with patch.dict(os.environ, env_vars, clear=False):
        # Import Settings class dynamically
        if 'config' in sys.modules:
            del sys.modules['config']
        
        from config import Settings
        
        test_settings = Settings()
        
        # Verify AWS configuration is loaded from environment
        assert test_settings.bedrock_model_id == bedrock_model
        assert test_settings.aws_region == aws_region
