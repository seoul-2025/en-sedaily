"""
Validation utilities for API requests
Provides validation functions for queries, dates, and API keys
"""
import re
from datetime import datetime
from typing import Optional


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


def validate_query(query: str) -> bool:
    """
    Validate search query is non-empty and not just whitespace
    
    Args:
        query: Search query string to validate
    
    Returns:
        True if query is valid, False otherwise
    
    Examples:
        >>> validate_query("artificial intelligence")
        True
        >>> validate_query("")
        False
        >>> validate_query("   ")
        False
        >>> validate_query("  hello  ")
        True
    """
    if not query or not query.strip():
        return False
    return True


def validate_date_format(date_str: str) -> bool:
    """
    Validate date format is YYYY-MM-DD
    
    Args:
        date_str: Date string to validate
    
    Returns:
        True if valid YYYY-MM-DD format, False otherwise
    
    Examples:
        >>> validate_date_format("2025-01-01")
        True
        >>> validate_date_format("2025/01/01")
        False
        >>> validate_date_format("invalid")
        False
        >>> validate_date_format("2025-13-01")
        False
    """
    # Check format pattern
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False
    
    # Validate it's a real date
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_api_key(api_key: Optional[str]) -> bool:
    """
    Validate API key is present and not empty
    
    Args:
        api_key: API key to validate
    
    Returns:
        True if API key is present and non-empty, False otherwise
    
    Examples:
        >>> validate_api_key("my-api-key-123")
        True
        >>> validate_api_key("")
        False
        >>> validate_api_key(None)
        False
        >>> validate_api_key("   ")
        False
    """
    if not api_key or not api_key.strip():
        return False
    return True


def validate_translation_text(text: str) -> bool:
    """
    Validate translation text is non-empty and not just whitespace
    
    Args:
        text: Text to validate for translation
    
    Returns:
        True if text is valid, False otherwise
    
    Examples:
        >>> validate_translation_text("Hello world")
        True
        >>> validate_translation_text("")
        False
        >>> validate_translation_text("   ")
        False
    """
    if not text or not text.strip():
        return False
    return True
