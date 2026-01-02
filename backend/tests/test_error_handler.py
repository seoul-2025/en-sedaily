"""
Property-based tests for error handling middleware
Tests error handling for BigKinds API, Translation Engine, network, rate limits, and logging
"""
import pytest
from hypothesis import given, strategies as st
import httpx
from botocore.exceptions import ClientError
from unittest.mock import Mock, patch, AsyncMock
import logging

from handlers.error_handler import ErrorHandler, ErrorCode, ErrorResponse
from clients.bigkinds_client import ValidationError as BigKindsValidationError
from clients.translation_service import TranslationError, ValidationError as TranslationValidationError


# Test Property 3: Translation failure preserves state
@given(st.text(min_size=1, max_size=100))
@pytest.mark.asyncio
async def test_translation_failure_preserves_state(query):
    """
    Feature: seodaily-eng, Property 3: Translation failure preserves state
    For any system state, when translation fails, the system should maintain 
    the current state and display an error message.
    Validates: Requirements 1.3
    """
    # Create a translation error
    translation_error = TranslationError("Translation service unavailable")
    
    # Handle the error
    error_response = ErrorHandler.handle_translation_error(translation_error)
    
    # Verify error response is created (state preserved by returning error instead of crashing)
    assert error_response is not None
    assert isinstance(error_response, ErrorResponse)
    assert error_response.code == ErrorCode.TRANSLATION_ERROR.value
    assert "temporarily unavailable" in error_response.message.lower()
    assert error_response.retry_possible is True


# Test Property 24: Network errors are handled gracefully
@given(st.sampled_from([
    httpx.ConnectError,
    httpx.TimeoutException,
    httpx.NetworkError,
    httpx.RemoteProtocolError
]))
def test_network_errors_handled_gracefully(error_class):
    """
    Feature: seodaily-eng, Property 24: Network errors are handled gracefully
    For any network connectivity failure, a message indicating connection issues 
    should be displayed.
    Validates: Requirements 6.3
    """
    # Create a network error
    if error_class == httpx.ConnectError:
        error = error_class("Connection refused")
    elif error_class == httpx.TimeoutException:
        error = error_class("Request timeout")
    elif error_class == httpx.NetworkError:
        error = error_class("Network error")
    else:  # RemoteProtocolError
        error = error_class("Protocol error")
    
    # Handle the error
    error_response = ErrorHandler.handle_network_error(error)
    
    # Verify graceful handling
    assert error_response is not None
    assert isinstance(error_response, ErrorResponse)
    assert error_response.code in [ErrorCode.NETWORK_ERROR.value, ErrorCode.TIMEOUT_ERROR.value]
    assert any(keyword in error_response.message.lower() for keyword in ["connection", "network", "timeout"])
    assert error_response.retry_possible is True


# Test Property 25: Rate limit errors provide guidance
@given(st.integers(min_value=1, max_value=1000))
def test_rate_limit_errors_provide_guidance(status_code_base):
    """
    Feature: seodaily-eng, Property 25: Rate limit errors provide guidance
    For any API rate limit error, a message asking the user to try again later 
    should be displayed.
    Validates: Requirements 6.4
    """
    # Create a mock HTTP response with 429 status
    mock_request = Mock()
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.text = "Rate limit exceeded"
    
    # Create HTTPStatusError for rate limit
    error = httpx.HTTPStatusError(
        "Rate limit exceeded",
        request=mock_request,
        response=mock_response
    )
    
    # Handle the error
    error_response = ErrorHandler.handle_error(error)
    
    # Verify guidance is provided
    assert error_response is not None
    assert isinstance(error_response, ErrorResponse)
    assert error_response.code in [ErrorCode.BIGKINDS_RATE_LIMIT.value, ErrorCode.TRANSLATION_RATE_LIMIT.value]
    assert any(keyword in error_response.message.lower() for keyword in ["wait", "try again", "moment"])
    assert error_response.retry_possible is True


# Test Property 26: Unexpected errors are logged and communicated
@given(st.text(min_size=5, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))))
def test_unexpected_errors_logged_and_communicated(error_message):
    """
    Feature: seodaily-eng, Property 26: Unexpected errors are logged and communicated
    For any unexpected error, the system should log error details and display 
    a generic error message.
    Validates: Requirements 6.5
    """
    # Create an unexpected error
    unexpected_error = RuntimeError(error_message)
    
    # Capture logs
    with patch('handlers.error_handler.logger') as mock_logger:
        # Handle the error
        error_response = ErrorHandler.handle_unexpected_error(unexpected_error)
        
        # Verify logging occurred
        assert mock_logger.error.called
        call_args = mock_logger.error.call_args
        assert call_args is not None
        
        # Verify error was logged with exc_info
        assert call_args[1].get('exc_info') is True
    
    # Verify user-friendly message
    assert error_response is not None
    assert isinstance(error_response, ErrorResponse)
    assert error_response.code == ErrorCode.INTERNAL_ERROR.value
    assert "unexpected error" in error_response.message.lower()
    assert error_response.retry_possible is True
    
    # Verify the actual error message is NOT exposed to user (for meaningful messages)
    # Only check if the error message is substantial (more than just punctuation)
    if len(error_message.strip()) > 3 and not all(c in '.,;:!? ' for c in error_message):
        assert error_message not in error_response.message


# Test Property 45: Logs exclude sensitive information
@given(st.sampled_from([
    "api_key=secret123",
    "access_key: mykey456",
    "password=pass789",
    "token=bearer_abc",
    "authorization: Basic xyz",
    "aws_access_key_id=AKIAIOSFODNN7EXAMPLE",
    "aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "API_KEY=test_key",
    "SECRET=my_secret"
]))
def test_logs_exclude_sensitive_information(sensitive_message):
    """
    Feature: seodaily-eng, Property 45: Logs exclude sensitive information
    For any log entry, sensitive information such as API keys should not be present.
    Validates: Requirements 10.4
    """
    # Sanitize the message
    sanitized = ErrorHandler._sanitize_log_message(sensitive_message)
    
    # Verify sensitive patterns are redacted
    sensitive_keywords = [
        "api_key", "access_key", "secret", "password",
        "token", "authorization", "aws_access_key_id",
        "aws_secret_access_key"
    ]
    
    # Check that the sanitized message contains [REDACTED]
    assert "[REDACTED]" in sanitized
    
    # Verify that sensitive values are not in the sanitized message
    # Extract potential sensitive values (anything after = or :)
    import re
    potential_values = re.findall(r'[=:]\s*(\S+)', sensitive_message)
    for value in potential_values:
        if len(value) > 3:  # Only check meaningful values
            assert value not in sanitized or value == "[REDACTED]"


# Additional test: Verify BigKinds errors are handled
@given(st.integers(min_value=400, max_value=599))
def test_bigkinds_api_errors_handled(status_code):
    """
    Test that BigKinds API errors produce user-friendly messages
    """
    # Create a mock HTTP response
    mock_request = Mock()
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.text = f"HTTP {status_code} error"
    
    # Create HTTPStatusError
    error = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=mock_request,
        response=mock_response
    )
    
    # Handle the error
    error_response = ErrorHandler.handle_bigkinds_error(error)
    
    # Verify user-friendly message
    assert error_response is not None
    assert isinstance(error_response, ErrorResponse)
    assert error_response.message  # Non-empty message
    assert "HTTP" not in error_response.message or "error" in error_response.message.lower()
    
    # Verify retry_possible is set appropriately
    if status_code == 404:
        assert error_response.retry_possible is False
    else:
        assert error_response.retry_possible is True


# Additional test: Verify validation errors are handled
@given(st.text(min_size=1, max_size=100))
def test_validation_errors_handled(error_message):
    """
    Test that validation errors are handled appropriately
    """
    # Create a validation error
    validation_error = BigKindsValidationError(error_message)
    
    # Handle the error
    error_response = ErrorHandler.handle_validation_error(validation_error)
    
    # Verify error response
    assert error_response is not None
    assert isinstance(error_response, ErrorResponse)
    assert error_response.code == ErrorCode.VALIDATION_ERROR.value
    assert error_response.retry_possible is False


# Additional test: Verify error routing works correctly
@given(st.sampled_from([
    BigKindsValidationError("Invalid input"),
    TranslationError("Translation failed"),
    RuntimeError("Unexpected error")
]))
def test_error_routing(error):
    """
    Test that handle_error routes to appropriate handlers
    """
    # Handle the error
    error_response = ErrorHandler.handle_error(error)
    
    # Verify appropriate handling
    assert error_response is not None
    assert isinstance(error_response, ErrorResponse)
    assert error_response.code  # Has an error code
    assert error_response.message  # Has a message
    assert isinstance(error_response.retry_possible, bool)


# Additional test: Verify Lambda response format
@given(
    st.text(min_size=1, max_size=50),
    st.text(min_size=10, max_size=100),
    st.booleans()
)
def test_lambda_response_format(error_code, error_message, retry_possible):
    """
    Test that ErrorResponse converts to proper Lambda response format
    """
    # Create an error response
    error_response = ErrorResponse(
        code=error_code,
        message=error_message,
        retry_possible=retry_possible
    )
    
    # Convert to Lambda response
    lambda_response = ErrorHandler.to_lambda_response(error_response)
    
    # Verify structure
    assert "statusCode" in lambda_response
    assert "headers" in lambda_response
    assert "body" in lambda_response
    assert "error" in lambda_response["body"]
    
    # Verify error details
    error_body = lambda_response["body"]["error"]
    assert error_body["code"] == error_code
    assert error_body["message"] == error_message
    assert error_body["retry_possible"] == retry_possible
    
    # Verify CORS headers
    assert lambda_response["headers"]["Access-Control-Allow-Origin"] == "*"


# Additional test: Verify AWS ClientError handling
def test_aws_client_error_handling():
    """
    Test that AWS Bedrock ClientError is handled appropriately
    """
    # Create a mock ClientError
    error_response = {
        "Error": {
            "Code": "ThrottlingException",
            "Message": "Rate exceeded"
        }
    }
    client_error = ClientError(error_response, "invoke_model")
    
    # Handle the error
    error_response_obj = ErrorHandler.handle_translation_error(client_error)
    
    # Verify handling
    assert error_response_obj is not None
    assert error_response_obj.code == ErrorCode.TRANSLATION_RATE_LIMIT.value
    assert "high demand" in error_response_obj.message.lower() or "try again" in error_response_obj.message.lower()
    assert error_response_obj.retry_possible is True
