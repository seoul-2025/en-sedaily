"""
Unit tests for slug_generator utility

Tests slug generation algorithm for SEO-friendly URLs.
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.slug_generator import (
    generate_slug,
    validate_slug,
    _generate_fallback_slug
)


class TestSlugGeneration:
    """Test basic slug generation functionality"""

    def test_basic_slug_generation(self):
        """Test normal title conversion"""
        title = "Samsung Reports Strong Q4 Earnings"
        slug = generate_slug(title, "2025-12-22T00:00:00", "finance")
        assert slug == "samsung-reports-strong-q4-earnings"

    def test_special_characters_removal(self):
        """Test special character handling"""
        title = "S.Korea's GDP Grows 2.5% in 2025!"
        slug = generate_slug(title, "2025-12-22T00:00:00", "finance")
        # Should convert % to -percent and remove special chars
        assert "s-korea" in slug
        assert "gdp" in slug
        assert "percent" in slug
        assert "!" not in slug
        assert "." not in slug

    def test_long_title_truncation(self):
        """Test truncation at word boundary"""
        title = "This is a very long title that exceeds the maximum character limit and should be truncated at word boundary to ensure readability"
        slug = generate_slug(title, "2025-12-22T00:00:00", "technology", max_length=60)

        assert len(slug) <= 60
        assert not slug.endswith('-')  # Should not end with hyphen
        # Should truncate at word boundary
        assert slug == "this-is-a-very-long-title-that-exceeds-the-maximum"

    def test_unicode_normalization(self):
        """Test unicode character normalization"""
        title = "Café Reopens with New Façade"
        slug = generate_slug(title, "2025-12-22T00:00:00", "culture")
        # Unicode chars should be converted to ASCII
        assert slug == "cafe-reopens-with-new-facade"

    def test_empty_title_fallback(self):
        """Test fallback slug for empty title"""
        title = ""
        slug = generate_slug(title, "2025-12-22T00:00:00", "finance")
        # Should use fallback format: article-{category}-{date}
        assert slug.startswith("article-")
        assert "finance" in slug
        assert "20251222" in slug

    def test_consecutive_hyphens_removed(self):
        """Test removal of consecutive hyphens"""
        title = "Breaking---News: Major  Announcement"
        slug = generate_slug(title, "2025-12-22T00:00:00", "news")
        # Multiple hyphens and spaces should become single hyphen
        assert "--" not in slug
        assert slug == "breaking-news-major-announcement"

    def test_percent_conversion(self):
        """Test percentage sign conversion"""
        title = "Economy Grows 3.5% This Quarter"
        slug = generate_slug(title, "2025-12-22T00:00:00", "finance")
        assert "percent" in slug
        assert "%" not in slug
        assert slug == "economy-grows-3-5-percent-this-quarter"

    def test_leading_trailing_hyphens(self):
        """Test removal of leading/trailing hyphens"""
        title = "---Test Title---"
        slug = generate_slug(title, "2025-12-22T00:00:00", "news")
        assert not slug.startswith('-')
        assert not slug.endswith('-')

    def test_very_short_title(self):
        """Test very short titles (< 3 chars)"""
        title = "OK"
        slug = generate_slug(title, "2025-12-22T00:00:00", "news")
        # Should use fallback for very short slugs
        assert len(slug) >= 3


class TestSlugValidation:
    """Test slug validation functionality"""

    def test_valid_slug(self):
        """Test validation of valid slugs"""
        valid_slugs = [
            "samsung-q4-earnings",
            "korea-gdp-growth",
            "article-finance-20251222",
            "test-123",
        ]
        for slug in valid_slugs:
            assert validate_slug(slug) == True

    def test_invalid_slug_special_chars(self):
        """Test rejection of slugs with special characters"""
        invalid_slugs = [
            "samsung@earnings",
            "korea's-gdp",
            "test!news",
            "article_finance",  # underscore not allowed
        ]
        for slug in invalid_slugs:
            assert validate_slug(slug) == False

    def test_invalid_slug_uppercase(self):
        """Test rejection of uppercase slugs"""
        assert validate_slug("Samsung-Earnings") == False

    def test_invalid_slug_leading_trailing_hyphen(self):
        """Test rejection of slugs with leading/trailing hyphens"""
        assert validate_slug("-samsung-earnings") == False
        assert validate_slug("samsung-earnings-") == False

    def test_invalid_slug_consecutive_hyphens(self):
        """Test rejection of slugs with consecutive hyphens"""
        assert validate_slug("samsung--earnings") == False

    def test_invalid_slug_length(self):
        """Test rejection of slugs that are too short or too long"""
        assert validate_slug("ab") == False  # Too short
        assert validate_slug("a" * 101) == False  # Too long

    def test_invalid_slug_empty(self):
        """Test rejection of empty slugs"""
        assert validate_slug("") == False
        assert validate_slug(None) == False


class TestFallbackSlug:
    """Test fallback slug generation"""

    def test_fallback_format(self):
        """Test fallback slug format"""
        slug = _generate_fallback_slug("2025-12-22T00:00:00", "finance")
        assert slug.startswith("article-")
        assert "finance" in slug
        assert "20251222" in slug

    def test_fallback_invalid_category(self):
        """Test fallback with invalid category"""
        slug = _generate_fallback_slug("2025-12-22T00:00:00", "경제")
        # Should still generate valid slug
        assert slug.startswith("article-")
        assert "20251222" in slug


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_numbers_only_title(self):
        """Test title with only numbers"""
        title = "123456789"
        slug = generate_slug(title, "2025-12-22T00:00:00", "news")
        assert slug == "123456789"
        assert validate_slug(slug) == True

    def test_mixed_language_title(self):
        """Test title with mixed Korean and English (Korean should be removed)"""
        title = "Samsung 삼성 Q4 Earnings"
        slug = generate_slug(title, "2025-12-22T00:00:00", "finance")
        # Korean characters should be removed during normalization
        assert "samsung" in slug
        assert "q4" in slug
        assert "earnings" in slug

    def test_all_special_chars(self):
        """Test title with all special characters"""
        title = "!@#$%^&*()"
        slug = generate_slug(title, "2025-12-22T00:00:00", "news")
        # Should fallback to date-based slug
        assert "article" in slug
        assert "20251222" in slug

    def test_invalid_date_format(self):
        """Test with invalid date format"""
        title = "Test Article"
        # Should still work even with invalid date
        slug = generate_slug(title, "invalid-date", "news")
        assert slug == "test-article"

    def test_none_inputs(self):
        """Test with None inputs"""
        slug = generate_slug(None, "2025-12-22T00:00:00", "news")
        # Should use fallback
        assert "article" in slug


class TestRealWorldExamples:
    """Test with real article titles from Seoul Economic Daily"""

    def test_samsung_earnings_article(self):
        """Real article: Samsung earnings report"""
        title = "Samsung Electronics Reports Record Q4 Earnings, Beating Analyst Expectations"
        slug = generate_slug(title, "2025-12-22T00:00:00", "finance")
        assert slug == "samsung-electronics-reports-record-q4-earnings-beating"
        assert validate_slug(slug) == True

    def test_korea_economy_article(self):
        """Real article: Korea economy growth"""
        title = "South Korea's Economy Grows 2.8% in Q4, Exceeding Forecasts"
        slug = generate_slug(title, "2025-12-22T00:00:00", "finance")
        assert "south-korea" in slug or "korea" in slug
        assert "economy" in slug
        assert validate_slug(slug) == True

    def test_tech_innovation_article(self):
        """Real article: Technology innovation"""
        title = "SK Hynix Unveils Next-Gen AI Chips for Data Centers"
        slug = generate_slug(title, "2025-12-22T00:00:00", "technology")
        assert slug == "sk-hynix-unveils-next-gen-ai-chips-for-data-centers"
        assert validate_slug(slug) == True

    def test_political_article(self):
        """Real article: Political news"""
        title = "National Assembly Passes 2025 Budget Bill After Months of Debate"
        slug = generate_slug(title, "2025-12-22T00:00:00", "politics")
        assert slug == "national-assembly-passes-2025-budget-bill-after-months"
        assert validate_slug(slug) == True


# Run tests if executed directly
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
