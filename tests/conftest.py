"""Test configuration and fixtures."""

import pydantic
import pytest

# Determine pydantic version
PYDANTIC_VERSION = int(pydantic.VERSION.split(".")[0])

# Skip markers for version-specific tests
skip_if_pydantic_v1 = pytest.mark.skipif(PYDANTIC_VERSION < 2, reason="Test requires Pydantic v2")
skip_if_pydantic_v2 = pytest.mark.skipif(PYDANTIC_VERSION >= 2, reason="Test requires Pydantic v1")


# Add markers to pytest
def pytest_configure(config):
    config.addinivalue_line("markers", "pydantic_v1: mark test to run only with Pydantic v1")
    config.addinivalue_line("markers", "pydantic_v2: mark test to run only with Pydantic v2")


def pytest_ignore_collect(collection_path, config):
    """Ignore collecting test files based on pydantic version."""
    path_str = str(collection_path)
    # Don't collect v2-only tests if pydantic v1 is installed
    return PYDANTIC_VERSION < 2 and "_v2.py" in path_str
