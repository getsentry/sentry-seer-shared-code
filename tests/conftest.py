"""Test configuration and fixtures."""

import sys

import pydantic
import pytest

# Determine pydantic version
PYDANTIC_VERSION = int(pydantic.VERSION.split(".")[0])

# Skip markers for version-specific tests
skip_if_pydantic_v1 = pytest.mark.skipif(
    PYDANTIC_VERSION < 2, reason="Test requires Pydantic v2"
)
skip_if_pydantic_v2 = pytest.mark.skipif(
    PYDANTIC_VERSION >= 2, reason="Test requires Pydantic v1"
)

# Add markers to pytest
def pytest_configure(config):
    config.addinivalue_line("markers", "pydantic_v1: mark test to run only with Pydantic v1")
    config.addinivalue_line("markers", "pydantic_v2: mark test to run only with Pydantic v2")


def pytest_ignore_collect(path, config):
    """Ignore collecting test files based on pydantic version."""
    path_str = str(path)
    
    # Don't collect v2 tests if pydantic v1 is installed
    if PYDANTIC_VERSION < 2:
        if "_v2.py" in path_str:
            return True
    
    # Don't collect v1-specific tests if pydantic v2 is installed
    # (test_base.py and test_codegen.py without _v2 suffix)
    if PYDANTIC_VERSION >= 2:
        if path_str.endswith("test_base.py") or path_str.endswith("test_codegen.py"):
            if "_v2.py" not in path_str and "test_types.py" not in path_str:
                return True
    
    return False
