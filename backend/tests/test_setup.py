"""
Test to verify pytest and hypothesis are properly configured
"""
import pytest
from hypothesis import given, strategies as st


def test_basic_pytest():
    """Basic pytest test to verify setup"""
    assert True


@given(st.integers())
def test_hypothesis_setup(x):
    """
    Basic hypothesis test to verify property-based testing setup
    Property: Any integer is equal to itself
    """
    assert x == x


def test_fastapi_import():
    """Verify FastAPI can be imported"""
    from main import app
    assert app is not None
