"""
Pytest configuration and fixtures
"""
import pytest
from hypothesis import settings as hypothesis_settings

# Configure Hypothesis for all tests
hypothesis_settings.register_profile(
    "default",
    max_examples=100,
    deadline=None
)
hypothesis_settings.load_profile("default")
