"""
Error Handling Middleware
Centralized error handling for BigKinds API, Translation Engine, and other errors
"""
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import httpx
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class ErrorCode(Enum):
    """Error codes for different error types"""
    # BigKinds API errors
    BIGKINDS_API_ERROR = "BIGKINDS_API_ERROR"
    BIGKINDS_NOT_FOUND = "BIGKINDS_NOT_FOUND"
    BIGKINDS_RATE_LIMIT = "BIGKINDS_RATE_LIMIT"
    
    # Translation Engine errors
    TRANSLATION_ERROR = "TRANSLATION_ERROR"
    TRANSLATION_RATE_LIMIT = "TRANSLATION_RATE_LIMIT"
    
    # Network errors
    NETWORK_ERROR = "NETWORK_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    
    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    
    # Generic errors
    INTERNAL_ERROR = "INTERNAL_ERROR"


@dataclass
class ErrorResponse:
    """Standardized error response"""
    code: str
    message: str
    retry_possible: bool
    details: Optional[Dict[str, Any]] = None


class ErrorHandler:
    """
    Centralized error handler for all application errors
    Provides user-friendly error messages and proper logging
    """
    
    @staticmethod
    def _sanitize_log_message(message: str, sensitive_keys: list = None) -> str:
        """
        Remove sensitive information from log messages
        
        Args:
            message: Original message
            sensitive_keys: List of sensitive key patterns to redact
        
        Returns:
            Sanitized message
        """
        if sensitive_keys is None:
            sensitive_keys = [
                "api_key", "access_key", "secret", "password",
                "token", "authorization", "aws_access_key_id",
                "aws_secret_access_key"
            ]
        
        import re
        sanitized = message
        
        # Redact key-value pairs (e.g., "api_key=value" or "api_key: value")
        for key in sensitive_keys:
            # Pattern to match key followed by = or : and capture the value
            pattern = re.compile(
                rf'\b{re.escape(key)}\s*[=:]\s*\S+',
                re.IGNORECASE
            )
            sanitized = pattern.sub(f"{key}=[REDACTED]", sanitized)
        
        # Also redact just the key if it appears standalone
        for key in sensitive_keys:
            pattern = re.compile(rf'\b{re.escape(key)}\b', re.IGNORECASE)
            sanitized = pattern.sub("[REDACTED]", sanitized)
        
        return sanitized
    
    @staticmethod
    def handle_bigkinds_error(error: Exception) -> ErrorResponse:
        """
        Handle BigKinds API errors
        
        Args:
            error: Exception from BigKinds API
        
        Returns:
            ErrorResponse with user-friendly message
        """
        # Sanitize error message before logging
        error_str = str(error)
        sanitized_error = ErrorHandler._sanitize_log_message(error_str)
        logger.error(f"BigKinds API error: {sanitized_error}")
        
        # Check for specific error types
        if isinstance(error, httpx.HTTPStatusError):
            status_code = error.response.status_code
            
            if status_code == 404:
                return ErrorResponse(
                    code=ErrorCode.BIGKINDS_NOT_FOUND.value,
                    message="The requested article was not found. It may have been removed or the ID is invalid.",
                    retry_possible=False
                )
            elif status_code == 429:
                return ErrorResponse(
                    code=ErrorCode.BIGKINDS_RATE_LIMIT.value,
                    message="Too many requests. Please wait a moment and try again.",
                    retry_possible=True
                )
            elif status_code >= 500:
                return ErrorResponse(
                    code=ErrorCode.BIGKINDS_API_ERROR.value,
                    message="The news service is temporarily unavailable. Please try again in a few moments.",
                    retry_possible=True
                )
        
        # Generic BigKinds error
        return ErrorResponse(
            code=ErrorCode.BIGKINDS_API_ERROR.value,
            message="Unable to retrieve news articles at this time. Please try again later.",
            retry_possible=True
        )
    
    @staticmethod
    def handle_translation_error(error: Exception) -> ErrorResponse:
        """
        Handle Translation Engine errors
        
        Args:
            error: Exception from Translation Engine
        
        Returns:
            ErrorResponse with user-friendly message
        """
        # Sanitize error message before logging
        error_str = str(error)
        sanitized_error = ErrorHandler._sanitize_log_message(error_str)
        logger.error(f"Translation Engine error: {sanitized_error}")
        
        # Check for specific error types
        if isinstance(error, ClientError):
            error_code = error.response.get("Error", {}).get("Code", "")
            
            if error_code == "ThrottlingException":
                return ErrorResponse(
                    code=ErrorCode.TRANSLATION_RATE_LIMIT.value,
                    message="Translation service is experiencing high demand. Please try again in a few moments.",
                    retry_possible=True
                )
            elif error_code in ["ServiceUnavailable", "InternalServerError"]:
                return ErrorResponse(
                    code=ErrorCode.TRANSLATION_ERROR.value,
                    message="Translation service is temporarily unavailable. Please try again later.",
                    retry_possible=True
                )
        
        # Generic translation error
        return ErrorResponse(
            code=ErrorCode.TRANSLATION_ERROR.value,
            message="Translation service is temporarily unavailable. Please try again later.",
            retry_possible=True
        )
    
    @staticmethod
    def handle_network_error(error: Exception) -> ErrorResponse:
        """
        Handle network connectivity errors
        
        Args:
            error: Network-related exception
        
        Returns:
            ErrorResponse with user-friendly message
        """
        # Sanitize error message before logging
        error_str = str(error)
        sanitized_error = ErrorHandler._sanitize_log_message(error_str)
        logger.error(f"Network error: {sanitized_error}")
        
        # Check for specific network error types
        if isinstance(error, httpx.ConnectError):
            return ErrorResponse(
                code=ErrorCode.NETWORK_ERROR.value,
                message="Unable to connect to the service. Please check your internet connection and try again.",
                retry_possible=True
            )
        elif isinstance(error, httpx.TimeoutException):
            return ErrorResponse(
                code=ErrorCode.TIMEOUT_ERROR.value,
                message="The request timeout occurred. Please try again.",
                retry_possible=True
            )
        elif isinstance(error, (httpx.NetworkError, httpx.RemoteProtocolError)):
            return ErrorResponse(
                code=ErrorCode.NETWORK_ERROR.value,
                message="A network error occurred. Please check your connection and try again.",
                retry_possible=True
            )
        
        # Generic network error
        return ErrorResponse(
            code=ErrorCode.NETWORK_ERROR.value,
            message="A connection error occurred. Please try again later.",
            retry_possible=True
        )
    
    @staticmethod
    def handle_validation_error(error: Exception) -> ErrorResponse:
        """
        Handle validation errors
        
        Args:
            error: Validation exception
        
        Returns:
            ErrorResponse with user-friendly message
        """
        # Validation errors are user-facing, so we can include the message
        # But still sanitize just in case
        error_str = str(error)
        sanitized_error = ErrorHandler._sanitize_log_message(error_str)
        logger.warning(f"Validation error: {sanitized_error}")
        
        return ErrorResponse(
            code=ErrorCode.VALIDATION_ERROR.value,
            message=sanitized_error,
            retry_possible=False
        )
    
    @staticmethod
    def handle_unexpected_error(error: Exception) -> ErrorResponse:
        """
        Handle unexpected errors with logging
        
        Args:
            error: Unexpected exception
        
        Returns:
            ErrorResponse with generic user-friendly message
        """
        # Log full error details (sanitized) for debugging
        error_str = str(error)
        sanitized_error = ErrorHandler._sanitize_log_message(error_str)
        logger.error(
            f"Unexpected error: {sanitized_error}",
            exc_info=True,
            extra={"error_type": type(error).__name__}
        )
        
        # Return generic message to user
        return ErrorResponse(
            code=ErrorCode.INTERNAL_ERROR.value,
            message="An unexpected error occurred. Please try again later.",
            retry_possible=True
        )
    
    @staticmethod
    def handle_error(error: Exception) -> ErrorResponse:
        """
        Main error handler that routes to specific handlers
        
        Args:
            error: Any exception
        
        Returns:
            ErrorResponse with appropriate message
        """
        # Import here to avoid circular dependencies
        from clients.bigkinds_client import ValidationError as BigKindsValidationError
        from clients.translation_service import (
            TranslationError,
            ValidationError as TranslationValidationError
        )
        from clients.response_validator import ResponseValidationError
        
        # Route to specific handlers based on error type
        if isinstance(error, (BigKindsValidationError, TranslationValidationError, ResponseValidationError)):
            return ErrorHandler.handle_validation_error(error)
        
        elif isinstance(error, TranslationError) or isinstance(error, ClientError):
            return ErrorHandler.handle_translation_error(error)
        
        elif isinstance(error, httpx.HTTPStatusError):
            # Check if it's a rate limit error
            if error.response.status_code == 429:
                return ErrorResponse(
                    code=ErrorCode.BIGKINDS_RATE_LIMIT.value,
                    message="Too many requests. Please wait a moment and try again.",
                    retry_possible=True
                )
            return ErrorHandler.handle_bigkinds_error(error)
        
        elif isinstance(error, (
            httpx.ConnectError,
            httpx.TimeoutException,
            httpx.NetworkError,
            httpx.RemoteProtocolError
        )):
            return ErrorHandler.handle_network_error(error)
        
        else:
            return ErrorHandler.handle_unexpected_error(error)
    
    @staticmethod
    def to_lambda_response(error_response: ErrorResponse, status_code: int = 400) -> Dict[str, Any]:
        """
        Convert ErrorResponse to Lambda API Gateway response format
        
        Args:
            error_response: ErrorResponse object
            status_code: HTTP status code (default: 400)
        
        Returns:
            Lambda response dict
        """
        response = {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": {
                "error": {
                    "code": error_response.code,
                    "message": error_response.message,
                    "retry_possible": error_response.retry_possible
                }
            }
        }
        
        if error_response.details:
            response["body"]["error"]["details"] = error_response.details
        
        return response
