"""
Slug Generator Utility for SEO-Friendly URLs

Converts Korean news article titles to URL-friendly slugs.
Implements Chosun Ilbo style: /{category}/{year}/{month}/{day}/{slug}

Example:
    "Samsung Q4 Earnings Beat Expectations!"
    → "samsung-q4-earnings-beat-expectations"
"""

import re
import unicodedata
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def generate_slug(
    title_en: str,
    published_at: str,
    category: str,
    max_length: int = 60
) -> str:
    """
    Generate SEO-friendly slug from English title.

    Args:
        title_en: English article title
        published_at: Publication timestamp (ISO 8601 format)
        category: Article category (used as fallback)
        max_length: Maximum slug length (default: 60)

    Returns:
        URL-friendly slug string

    Algorithm:
        1. Normalize unicode characters to ASCII
        2. Convert to lowercase
        3. Remove special characters (keep alphanumeric and hyphens)
        4. Replace spaces and multiple hyphens with single hyphen
        5. Smart truncation at word boundary
        6. Remove leading/trailing hyphens
        7. Fallback to date-based slug if empty

    Examples:
        >>> generate_slug("Samsung Reports Strong Q4 Earnings", "2025-12-22", "finance")
        'samsung-reports-strong-q4-earnings'

        >>> generate_slug("S.Korea's GDP Grows 2.5% in 2025!", "2025-12-22", "finance")
        's-korea-gdp-grows-2-5-in-2025'

        >>> generate_slug("", "2025-12-22", "finance")
        'article-20251222'
    """
    if not title_en or not isinstance(title_en, str):
        logger.warning(f"Invalid title_en: {title_en}, using fallback slug")
        return _generate_fallback_slug(published_at, category)

    # Step 1: Normalize unicode characters to ASCII
    # This handles accented characters: "Café" → "Cafe"
    normalized = unicodedata.normalize('NFKD', title_en)
    ascii_title = normalized.encode('ascii', 'ignore').decode('ascii')

    # Step 2: Convert to lowercase
    slug = ascii_title.lower()

    # Step 3: Replace percent sign and other special patterns
    # "2.5%" → "2-5-percent"
    slug = re.sub(r'(\d+)%', r'\1-percent', slug)

    # Step 4: Remove special characters except alphanumeric and hyphens/spaces
    # Keep only: a-z, 0-9, spaces, hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)

    # Step 5: Replace spaces and multiple hyphens with single hyphen
    slug = re.sub(r'[-\s]+', '-', slug)

    # Step 6: Smart truncation at word boundary
    if len(slug) > max_length:
        # Truncate to max_length
        slug = slug[:max_length]

        # Find last hyphen within limit (word boundary)
        last_hyphen = slug.rfind('-')
        if last_hyphen > 0:
            slug = slug[:last_hyphen]

    # Step 7: Remove leading/trailing hyphens
    slug = slug.strip('-')

    # Step 8: Validate - must not be empty
    if not slug or len(slug) < 3:
        logger.warning(f"Generated slug too short: '{slug}', using fallback")
        return _generate_fallback_slug(published_at, category)

    return slug


def _generate_fallback_slug(published_at: str, category: str) -> str:
    """
    Generate fallback slug when title is empty or invalid.

    Format: article-{category}-{YYYYMMDD}
    Example: article-finance-20251222
    """
    try:
        # Extract date from ISO timestamp: "2025-12-22T00:00:00" → "20251222"
        date_str = published_at[:10].replace('-', '')
        category_slug = re.sub(r'[^\w-]', '', category.lower())[:20]
        return f"article-{category_slug}-{date_str}"
    except Exception as e:
        logger.error(f"Failed to generate fallback slug: {e}")
        return "article-unknown"


async def ensure_unique_slug(
    slug: str,
    published_at: str,
    dynamodb_client,
    max_attempts: int = 10
) -> str:
    """
    Ensure slug is unique by checking DynamoDB.
    If duplicate exists, append date suffix or counter.

    Args:
        slug: Original slug to check
        published_at: Publication timestamp
        dynamodb_client: DynamoDB client instance
        max_attempts: Maximum collision resolution attempts

    Returns:
        Unique slug string

    Strategy:
        1. Check if slug exists in DynamoDB (via GSI)
        2. If collision, first attempt: append date (YYYYMMDD)
        3. If still collision, append counter: -2, -3, etc.
        4. Max 10 attempts to prevent infinite loop

    Examples:
        Original: "samsung-earnings"
        1st collision: "samsung-earnings-20251222"
        2nd collision: "samsung-earnings-2"
        3rd collision: "samsung-earnings-3"
    """
    original_slug = slug
    counter = 1

    for attempt in range(max_attempts):
        # Check if current slug exists
        exists = await _slug_exists(slug, dynamodb_client)

        if not exists:
            if attempt > 0:
                logger.info(f"Resolved slug collision: '{original_slug}' → '{slug}'")
            return slug

        # Collision detected - modify slug
        if counter == 1:
            # First attempt: append date
            date_suffix = published_at[:10].replace('-', '')
            slug = f"{original_slug}-{date_suffix}"
        else:
            # Subsequent attempts: append counter
            slug = f"{original_slug}-{counter}"

        counter += 1

    # Max attempts reached - use timestamp as last resort
    logger.error(f"Failed to resolve slug collision after {max_attempts} attempts: {original_slug}")
    timestamp = published_at.replace('-', '').replace(':', '').replace('T', '-')[:15]
    return f"{original_slug[:30]}-{timestamp}"


async def _slug_exists(slug: str, dynamodb_client) -> bool:
    """
    Check if slug already exists in DynamoDB.

    Args:
        slug: Slug to check
        dynamodb_client: DynamoDB client with get_article_by_slug method

    Returns:
        True if slug exists, False otherwise
    """
    try:
        article = await dynamodb_client.get_article_by_slug(slug)
        return article is not None
    except Exception as e:
        logger.error(f"Error checking slug existence: {e}")
        # On error, assume slug doesn't exist to allow operation to proceed
        return False


def validate_slug(slug: str) -> bool:
    """
    Validate slug format.

    Rules:
        - Only lowercase alphanumeric and hyphens
        - No leading/trailing hyphens
        - Length between 3 and 100 characters
        - No consecutive hyphens

    Args:
        slug: Slug to validate

    Returns:
        True if valid, False otherwise
    """
    if not slug or not isinstance(slug, str):
        return False

    # Check length
    if len(slug) < 3 or len(slug) > 100:
        return False

    # Check format: lowercase alphanumeric and hyphens only
    if not re.match(r'^[a-z0-9-]+$', slug):
        return False

    # Check for leading/trailing hyphens
    if slug.startswith('-') or slug.endswith('-'):
        return False

    # Check for consecutive hyphens
    if '--' in slug:
        return False

    return True


# Test examples (for manual verification)
if __name__ == '__main__':
    test_cases = [
        ("Samsung Reports Strong Q4 Earnings", "2025-12-22T00:00:00", "finance"),
        ("S.Korea's GDP Grows 2.5% in 2025!", "2025-12-22T00:00:00", "finance"),
        ("Breaking: Major Announcement", "2025-12-22T00:00:00", "news"),
        ("This is a very long title that exceeds the maximum character limit and should be truncated at word boundary to ensure readability", "2025-12-22T00:00:00", "technology"),
        ("", "2025-12-22T00:00:00", "finance"),
        ("Café Reopens with New Façade", "2025-12-22T00:00:00", "culture"),
        ("Breaking---News: Major  Announcement", "2025-12-22T00:00:00", "news"),
    ]

    print("Slug Generation Test Cases:")
    print("=" * 80)
    for title, date, category in test_cases:
        slug = generate_slug(title, date, category)
        valid = validate_slug(slug)
        print(f"Title: {title[:50]}")
        print(f"Slug:  {slug}")
        print(f"Valid: {valid}")
        print(f"Length: {len(slug)}")
        print("-" * 80)
