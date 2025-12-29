"""
Response Validation Module
Validates API response integrity before processing
"""
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ResponseValidationError(Exception):
    """Raised when response validation fails"""
    pass


class ResponseValidator:
    """
    Validates API responses for integrity and structure
    Ensures responses are well-formed before processing
    """
    
    @staticmethod
    def validate_bigkinds_search_response(response_data: Dict[str, Any]) -> None:
        """
        Validate BigKinds search API response structure
        
        Args:
            response_data: Parsed JSON response from BigKinds search API
        
        Raises:
            ResponseValidationError: If response structure is invalid
        """
        if not isinstance(response_data, dict):
            raise ResponseValidationError("Response must be a dictionary")
        
        # Check for return_object
        if "return_object" not in response_data:
            raise ResponseValidationError("Response missing 'return_object' field")
        
        return_object = response_data["return_object"]
        if not isinstance(return_object, dict):
            raise ResponseValidationError("'return_object' must be a dictionary")
        
        # Check for required fields in return_object
        if "total_hits" not in return_object:
            raise ResponseValidationError("Response missing 'total_hits' field")
        
        if not isinstance(return_object["total_hits"], int):
            raise ResponseValidationError("'total_hits' must be an integer")
        
        if return_object["total_hits"] < 0:
            raise ResponseValidationError("'total_hits' cannot be negative")
        
        # Check for documents field
        if "documents" not in return_object:
            raise ResponseValidationError("Response missing 'documents' field")
        
        if not isinstance(return_object["documents"], list):
            raise ResponseValidationError("'documents' must be a list")
        
        # Validate each document structure
        for idx, doc in enumerate(return_object["documents"]):
            if not isinstance(doc, dict):
                raise ResponseValidationError(f"Document at index {idx} must be a dictionary")
            
            # Check for required document fields
            if "news_id" not in doc:
                raise ResponseValidationError(f"Document at index {idx} missing 'news_id' field")
            
            if not isinstance(doc["news_id"], str):
                raise ResponseValidationError(f"Document at index {idx} 'news_id' must be a string")
    
    @staticmethod
    def validate_bigkinds_detail_response(response_data: Dict[str, Any]) -> None:
        """
        Validate BigKinds article detail API response structure
        
        Args:
            response_data: Parsed JSON response from BigKinds detail API
        
        Raises:
            ResponseValidationError: If response structure is invalid
        """
        if not isinstance(response_data, dict):
            raise ResponseValidationError("Response must be a dictionary")
        
        # Check for return_object
        if "return_object" not in response_data:
            raise ResponseValidationError("Response missing 'return_object' field")
        
        return_object = response_data["return_object"]
        if not isinstance(return_object, dict):
            raise ResponseValidationError("'return_object' must be a dictionary")
        
        # Check for documents field
        if "documents" not in return_object:
            raise ResponseValidationError("Response missing 'documents' field")
        
        if not isinstance(return_object["documents"], list):
            raise ResponseValidationError("'documents' must be a list")
        
        # Validate each document structure
        for idx, doc in enumerate(return_object["documents"]):
            if not isinstance(doc, dict):
                raise ResponseValidationError(f"Document at index {idx} must be a dictionary")
            
            # Check for required document fields
            if "news_id" not in doc:
                raise ResponseValidationError(f"Document at index {idx} missing 'news_id' field")
            
            if not isinstance(doc["news_id"], str):
                raise ResponseValidationError(f"Document at index {idx} 'news_id' must be a string")
    
    @staticmethod
    def validate_translation_response(response_data: Dict[str, Any]) -> None:
        """
        Validate Translation Engine (Bedrock Claude) response structure
        
        Args:
            response_data: Parsed JSON response from Bedrock Claude API
        
        Raises:
            ResponseValidationError: If response structure is invalid
        """
        if not isinstance(response_data, dict):
            raise ResponseValidationError("Response must be a dictionary")
        
        # Check for content field
        if "content" not in response_data:
            raise ResponseValidationError("Response missing 'content' field")
        
        content = response_data["content"]
        if not isinstance(content, list):
            raise ResponseValidationError("'content' must be a list")
        
        if len(content) == 0:
            raise ResponseValidationError("'content' list is empty")
        
        # Validate first content item
        first_content = content[0]
        if not isinstance(first_content, dict):
            raise ResponseValidationError("Content item must be a dictionary")
        
        if "text" not in first_content:
            raise ResponseValidationError("Content item missing 'text' field")
        
        if not isinstance(first_content["text"], str):
            raise ResponseValidationError("'text' field must be a string")
        
        # Validate that text is not empty
        if not first_content["text"].strip():
            raise ResponseValidationError("Translation text is empty")
    
    @staticmethod
    def validate_and_sanitize_bigkinds_search(response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize BigKinds search response
        
        Args:
            response_data: Raw response data
        
        Returns:
            Validated and sanitized response data
        
        Raises:
            ResponseValidationError: If validation fails
        """
        ResponseValidator.validate_bigkinds_search_response(response_data)
        
        # Sanitize: ensure all expected fields exist with defaults
        return_object = response_data["return_object"]
        
        sanitized = {
            "return_object": {
                "total_hits": return_object["total_hits"],
                "documents": []
            }
        }
        
        for doc in return_object["documents"]:
            sanitized_doc = {
                "news_id": doc.get("news_id", ""),
                "title": doc.get("title", ""),
                "content": doc.get("content"),
                "published_at": doc.get("published_at", ""),
                "provider_name": doc.get("provider_name", ""),
                "category": doc.get("category", ""),
                "byline": doc.get("byline"),
                "news_url": doc.get("news_url"),
                "images": doc.get("images", []),
                "images_caption": doc.get("images_caption", [])
            }
            sanitized["return_object"]["documents"].append(sanitized_doc)
        
        return sanitized
    
    @staticmethod
    def validate_and_sanitize_bigkinds_detail(response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize BigKinds detail response
        
        Args:
            response_data: Raw response data
        
        Returns:
            Validated and sanitized response data
        
        Raises:
            ResponseValidationError: If validation fails
        """
        ResponseValidator.validate_bigkinds_detail_response(response_data)
        
        # Sanitize: ensure all expected fields exist with defaults
        return_object = response_data["return_object"]
        
        sanitized = {
            "return_object": {
                "documents": []
            }
        }
        
        for doc in return_object["documents"]:
            sanitized_doc = {
                "news_id": doc.get("news_id", ""),
                "title": doc.get("title", ""),
                "content": doc.get("content"),
                "published_at": doc.get("published_at", ""),
                "provider_name": doc.get("provider_name", ""),
                "category": doc.get("category", ""),
                "byline": doc.get("byline"),
                "news_url": doc.get("news_url"),
                "provider_link_page": doc.get("provider_link_page"),
                "images": doc.get("images", []),
                "images_caption": doc.get("images_caption", [])
            }
            sanitized["return_object"]["documents"].append(sanitized_doc)
        
        return sanitized
    
    @staticmethod
    def validate_and_sanitize_translation(response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize translation response
        
        Args:
            response_data: Raw response data
        
        Returns:
            Validated and sanitized response data
        
        Raises:
            ResponseValidationError: If validation fails
        """
        ResponseValidator.validate_translation_response(response_data)
        
        # Return as-is since structure is already validated
        return response_data
