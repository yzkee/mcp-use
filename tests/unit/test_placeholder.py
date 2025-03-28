"""
Basic test placeholder to ensure CI pipeline passes.
"""

import pytest


def test_placeholder():
    """Simple test that always passes to ensure CI pipeline works."""
    assert True


@pytest.mark.asyncio
async def test_async_placeholder():
    """Simple async test that always passes to test the async test configuration."""
    assert True
