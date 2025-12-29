"""
Property-based tests for validation utilities
Tests validation functions using Hypothesis for comprehensive coverage
"""
import pytest
from hypothesis import given, strategies as st, assume
from clients.validation import (
    validate_query,
    validate_date_format,
    validate_api_key,
    validate_translation_text,
    ValidationError
)
from clients.bigkinds_client import BigKindsClient
from clients.translation_service import TranslationService
from datetime import datetime, timedelta
import re


# ============================================================================
# Property 4: Empty queries are rejected
# ============================================================================

@given(st.text())
def test_property_4_empty_queries_rejected(query: str):
    """
    Feature: seodaily-eng, Property 4: Empty queries are rejected
    
    For any string composed entirely of whitespace, the search should be 
    prevented and a validation message should be displayed.
    
    Validates: Requirements 1.4
    """
    result = validate_query(query)
    
    # If query is empty or only whitespace, it should be rejected
    if not query or not query.strip():
        assert result is False, f"Empty/whitespace query should be rejected: {repr(query)}"
    else:
        # Non-empty queries with actual content should pass
        assert result is True, f"Valid query should be accepted: {repr(query)}"


@given(st.text(min_size=1).filter(lambda x: x.strip()))
def test_property_4_non_empty_queries_accepted(query: str):
    """
    Feature: seodaily-eng, Property 4: Empty queries are rejected (inverse)
    
    For any non-empty query with actual content, validation should pass.
    
    Validates: Requirements 1.4
    """
    result = validate_query(query)
    assert result is True, f"Non-empty query should be accepted: {repr(query)}"


# ============================================================================
# Property 35: Validation failures prevent API calls
# ============================================================================

@pytest.mark.asyncio
@given(
    api_key=st.one_of(st.none(), st.just(""), st.text().filter(lambda x: not x.strip()))
)
async def test_property_35_invalid_api_key_prevents_bigkinds_call(api_key):
    """
    Feature: seodaily-eng, Property 35: Validation failures prevent API calls
    
    For any validation failure, no external API call should be made.
    Tests that invalid API keys prevent BigKinds client initialization.
    
    Validates: Requirements 8.4
    """
    # Invalid API key should prevent client creation
    with pytest.raises(Exception) as exc_info:
        client = BigKindsClient(api_key=api_key or "")
    
    # Should raise ValidationError (imported from bigkinds_client)
    assert "ValidationError" in str(type(exc_info.value).__name__) or "API key" in str(exc_info.value)


@pytest.mark.asyncio
@given(
    date_str=st.text().filter(lambda x: not re.match(r'^\d{4}-\d{2}-\d{2}$', x))
)
async def test_property_35_invalid_date_prevents_api_call(date_str):
    """
    Feature: seodaily-eng, Property 35: Validation failures prevent API calls
    
    For any validation failure, no external API call should be made.
    Tests that invalid date formats are rejected before API calls.
    
    Validates: Requirements 8.4
    """
    # Invalid date format should be rejected
    result = validate_date_format(date_str)
    assert result is False, f"Invalid date format should be rejected: {repr(date_str)}"


@pytest.mark.asyncio
@given(
    text=st.one_of(st.just(""), st.text().filter(lambda x: not x.strip()))
)
async def test_property_35_empty_translation_text_rejected(text):
    """
    Feature: seodaily-eng, Property 35: Validation failures prevent API calls
    
    For any validation failure, no external API call should be made.
    Tests that empty translation text is rejected.
    
    Validates: Requirements 8.4
    """
    # Empty or whitespace-only text should be rejected
    result = validate_translation_text(text)
    assert result is False, f"Empty/whitespace text should be rejected: {repr(text)}"


# ============================================================================
# Property 36: Valid requests proceed to API
# ============================================================================

@given(
    query=st.text(min_size=1).filter(lambda x: x.strip()),
    api_key=st.text(min_size=1).filter(lambda x: x.strip())
)
def test_property_36_valid_query_and_api_key_pass_validation(query: str, api_key: str):
    """
    Feature: seodaily-eng, Property 36: Valid requests proceed to API
    
    For any request that passes all validations, the API call should proceed.
    Tests that valid queries and API keys pass validation.
    
    Validates: Requirements 8.5
    """
    # Valid query should pass
    query_result = validate_query(query)
    assert query_result is True, f"Valid query should pass: {repr(query)}"
    
    # Valid API key should pass
    api_key_result = validate_api_key(api_key)
    assert api_key_result is True, f"Valid API key should pass: {repr(api_key)}"


@given(
    year=st.integers(min_value=2000, max_value=2100),
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=28)  # Use 28 to avoid invalid dates
)
def test_property_36_valid_dates_pass_validation(year: int, month: int, day: int):
    """
    Feature: seodaily-eng, Property 36: Valid requests proceed to API
    
    For any request that passes all validations, the API call should proceed.
    Tests that valid date formats pass validation.
    
    Validates: Requirements 8.5
    """
    # Construct valid date string
    date_str = f"{year:04d}-{month:02d}-{day:02d}"
    
    # Valid date should pass
    result = validate_date_format(date_str)
    assert result is True, f"Valid date should pass: {date_str}"


@given(
    text=st.text(min_size=1).filter(lambda x: x.strip())
)
def test_property_36_valid_translation_text_passes(text: str):
    """
    Feature: seodaily-eng, Property 36: Valid requests proceed to API
    
    For any request that passes all validations, the API call should proceed.
    Tests that valid translation text passes validation.
    
    Validates: Requirements 8.5
    """
    # Valid text should pass
    result = validate_translation_text(text)
    assert result is True, f"Valid translation text should pass: {repr(text)}"


# ============================================================================
# Additional edge case tests
# ============================================================================

def test_date_validation_edge_cases():
    """Test specific edge cases for date validation"""
    # Valid dates
    assert validate_date_format("2025-01-01") is True
    assert validate_date_format("2025-12-31") is True
    assert validate_date_format("2024-02-29") is True  # Leap year
    
    # Invalid dates
    assert validate_date_format("2025-13-01") is False  # Invalid month
    assert validate_date_format("2025-02-30") is False  # Invalid day
    assert validate_date_format("2023-02-29") is False  # Not a leap year
    assert validate_date_format("2025/01/01") is False  # Wrong separator
    assert validate_date_format("01-01-2025") is False  # Wrong order
    assert validate_date_format("2025-1-1") is False    # Missing leading zeros
    assert validate_date_format("invalid") is False
    assert validate_date_format("") is False


def test_query_validation_edge_cases():
    """Test specific edge cases for query validation"""
    # Valid queries
    assert validate_query("hello") is True
    assert validate_query("  hello  ") is True
    assert validate_query("a") is True
    assert validate_query("123") is True
    assert validate_query("한글") is True
    
    # Invalid queries
    assert validate_query("") is False
    assert validate_query("   ") is False
    assert validate_query("\t\n") is False
    assert validate_query("\r\n  \t") is False


def test_api_key_validation_edge_cases():
    """Test specific edge cases for API key validation"""
    # Valid API keys
    assert validate_api_key("key123") is True
    assert validate_api_key("  key123  ") is True
    assert validate_api_key("a") is True
    
    # Invalid API keys
    assert validate_api_key("") is False
    assert validate_api_key("   ") is False
    assert validate_api_key(None) is False
    assert validate_api_key("\t\n") is False


def test_translation_text_validation_edge_cases():
    """Test specific edge cases for translation text validation"""
    # Valid text
    assert validate_translation_text("Hello") is True
    assert validate_translation_text("  Hello  ") is True
    assert validate_translation_text("한글") is True
    
    # Invalid text
    assert validate_translation_text("") is False
    assert validate_translation_text("   ") is False
    assert validate_translation_text("\t\n") is False
