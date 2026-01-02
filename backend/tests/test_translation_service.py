"""
Property-based tests for Translation Service
Tests translation functionality, validation, and error handling
"""
import pytest
from hypothesis import given, strategies as st
from unittest.mock import Mock, patch, AsyncMock
import json
from botocore.exceptions import ClientError

from clients.translation_service import TranslationService, TranslationError, ValidationError


# Test fixtures
@pytest.fixture
def mock_bedrock_client():
    """Create a mock Bedrock client"""
    mock_client = Mock()
    mock_client.meta.endpoint_url = "https://bedrock-runtime.us-east-1.amazonaws.com"
    return mock_client


@pytest.fixture
def translation_service(mock_bedrock_client):
    """Create a TranslationService instance with mocked Bedrock client"""
    with patch("boto3.Session") as mock_session:
        mock_session.return_value.client.return_value = mock_bedrock_client
        service = TranslationService(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            region="us-east-1"
        )
        return service


# Property 2: All article titles are translated
# Feature: seodaily-eng, Property 2: All article titles are translated
@pytest.mark.asyncio
@given(st.lists(st.text(min_size=1, max_size=200), min_size=1, max_size=10))
async def test_all_article_titles_are_translated(titles):
    """
    For any list of article titles, all titles should be translated to English
    Validates: Requirements 1.2
    """
    # Filter out whitespace-only strings
    valid_titles = [t for t in titles if t.strip()]
    if not valid_titles:
        return
    
    with patch("boto3.Session") as mock_session:
        mock_client = Mock()
        mock_client.meta.endpoint_url = "https://bedrock-runtime.us-east-1.amazonaws.com"
        
        # Mock successful translation responses
        def mock_invoke_model(**kwargs):
            body = json.loads(kwargs["body"])
            original_text = body["messages"][0]["content"]
            
            # Simulate translation by adding "[TRANSLATED]" prefix
            response_body = {
                "content": [
                    {"text": f"[TRANSLATED] {original_text}"}
                ]
            }
            
            mock_response = {
                "body": Mock()
            }
            mock_response["body"].read = Mock(return_value=json.dumps(response_body).encode())
            return mock_response
        
        mock_client.invoke_model = mock_invoke_model
        mock_session.return_value.client.return_value = mock_client
        
        service = TranslationService()
        
        # Translate all titles
        translated_titles = await service.translate_batch(valid_titles)
        
        # Verify all titles were translated
        assert len(translated_titles) == len(valid_titles)
        for translated in translated_titles:
            assert translated is not None
            assert len(translated) > 0
            assert "[TRANSLATED]" in translated


# Property 11: Full article translation is complete
# Feature: seodaily-eng, Property 11: Full article translation is complete
@pytest.mark.asyncio
@given(
    st.text(min_size=1, max_size=200),
    st.text(min_size=10, max_size=1000)
)
async def test_full_article_translation_is_complete(title, content):
    """
    For any article with title and content, both should be translated to English
    Validates: Requirements 3.2
    """
    # Filter out whitespace-only strings
    if not title.strip() or not content.strip():
        return
    
    with patch("boto3.Session") as mock_session:
        mock_client = Mock()
        mock_client.meta.endpoint_url = "https://bedrock-runtime.us-east-1.amazonaws.com"
        
        # Mock successful translation responses
        def mock_invoke_model(**kwargs):
            body = json.loads(kwargs["body"])
            original_text = body["messages"][0]["content"]
            
            response_body = {
                "content": [
                    {"text": f"[TRANSLATED] {original_text}"}
                ]
            }
            
            mock_response = {
                "body": Mock()
            }
            mock_response["body"].read = Mock(return_value=json.dumps(response_body).encode())
            return mock_response
        
        mock_client.invoke_model = mock_invoke_model
        mock_session.return_value.client.return_value = mock_client
        
        service = TranslationService()
        
        # Translate both title and content
        translated_title = await service.translate(title)
        translated_content = await service.translate(content)
        
        # Verify both were translated
        assert translated_title is not None
        assert len(translated_title) > 0
        assert "[TRANSLATED]" in translated_title
        
        assert translated_content is not None
        assert len(translated_content) > 0
        assert "[TRANSLATED]" in translated_content


# Property 23: Translation errors are communicated clearly
# Feature: seodaily-eng, Property 23: Translation errors are communicated clearly
@pytest.mark.asyncio
@given(st.text(min_size=1, max_size=200))
async def test_translation_errors_are_communicated_clearly(text):
    """
    For any Translation Engine error, a clear message should be displayed
    Validates: Requirements 6.2
    """
    if not text.strip():
        return
    
    with patch("boto3.Session") as mock_session:
        mock_client = Mock()
        mock_client.meta.endpoint_url = "https://bedrock-runtime.us-east-1.amazonaws.com"
        
        # Mock API error
        error_response = {
            "Error": {
                "Code": "ThrottlingException",
                "Message": "Rate limit exceeded"
            }
        }
        mock_client.invoke_model = Mock(
            side_effect=ClientError(error_response, "InvokeModel")
        )
        
        mock_session.return_value.client.return_value = mock_client
        
        service = TranslationService()
        
        # Attempt translation and verify error message
        with pytest.raises(TranslationError) as exc_info:
            await service.translate(text)
        
        # Verify error message is user-friendly and mentions unavailability
        error_message = str(exc_info.value)
        assert "temporarily unavailable" in error_message.lower() or "failed" in error_message.lower()
        assert len(error_message) > 0


# Property 34: Translation text is validated as non-empty
# Feature: seodaily-eng, Property 34: Translation text is validated as non-empty
@pytest.mark.asyncio
@given(st.text(max_size=100).filter(lambda x: not x.strip()))
async def test_translation_text_validated_as_non_empty(whitespace_text):
    """
    For any string composed entirely of whitespace, translation should be rejected
    Validates: Requirements 8.3
    """
    with patch("boto3.Session") as mock_session:
        mock_client = Mock()
        mock_client.meta.endpoint_url = "https://bedrock-runtime.us-east-1.amazonaws.com"
        mock_session.return_value.client.return_value = mock_client
        
        service = TranslationService()
        
        # Attempt to translate whitespace-only text
        with pytest.raises(ValidationError) as exc_info:
            await service.translate(whitespace_text)
        
        # Verify validation error message
        error_message = str(exc_info.value)
        assert "non-empty" in error_message.lower() or "whitespace" in error_message.lower()


# Property 43: Translation Engine uses HTTPS
# Feature: seodaily-eng, Property 43: Translation Engine uses HTTPS
def test_translation_engine_uses_https():
    """
    For any Translation Engine request, the URL scheme should be "https"
    Validates: Requirements 10.2
    """
    with patch("boto3.Session") as mock_session:
        mock_client = Mock()
        # AWS Bedrock always uses HTTPS
        mock_client.meta.endpoint_url = "https://bedrock-runtime.us-east-1.amazonaws.com"
        mock_session.return_value.client.return_value = mock_client
        
        service = TranslationService()
        
        # Verify the endpoint uses HTTPS
        endpoint_url = service.bedrock_runtime.meta.endpoint_url
        assert endpoint_url.startswith("https://")


# Additional test: Verify HTTPS enforcement in initialization
def test_https_enforcement_in_initialization():
    """
    Verify that non-HTTPS endpoints are rejected during initialization
    """
    with patch("boto3.Session") as mock_session:
        mock_client = Mock()
        # Try to use HTTP endpoint (should be rejected)
        mock_client.meta.endpoint_url = "http://insecure-endpoint.com"
        mock_session.return_value.client.return_value = mock_client
        
        # Should raise ValidationError for non-HTTPS endpoint
        with pytest.raises(ValidationError) as exc_info:
            TranslationService()
        
        error_message = str(exc_info.value)
        assert "https" in error_message.lower()


# Additional test: Batch translation with empty list
@pytest.mark.asyncio
async def test_batch_translation_empty_list():
    """
    Verify that batch translation handles empty list correctly
    """
    with patch("boto3.Session") as mock_session:
        mock_client = Mock()
        mock_client.meta.endpoint_url = "https://bedrock-runtime.us-east-1.amazonaws.com"
        mock_session.return_value.client.return_value = mock_client
        
        service = TranslationService()
        
        # Translate empty list
        result = await service.translate_batch([])
        
        # Should return empty list
        assert result == []


# Additional test: Batch translation validates all texts
@pytest.mark.asyncio
async def test_batch_translation_validates_all_texts():
    """
    Verify that batch translation validates all texts in the list
    """
    with patch("boto3.Session") as mock_session:
        mock_client = Mock()
        mock_client.meta.endpoint_url = "https://bedrock-runtime.us-east-1.amazonaws.com"
        mock_session.return_value.client.return_value = mock_client
        
        service = TranslationService()
        
        # Try to translate list with whitespace-only text
        texts = ["valid text", "   ", "another valid text"]
        
        with pytest.raises(ValidationError) as exc_info:
            await service.translate_batch(texts)
        
        # Should indicate which text failed validation
        error_message = str(exc_info.value)
        assert "index" in error_message.lower() or "invalid" in error_message.lower()

