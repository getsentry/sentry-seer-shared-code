"""
Shared Pydantic models for Sentry and Seer code review integration.

This package provides type-safe data models for validating payloads sent from
Sentry to Seer's code review API. Using shared models ensures:
- Tests catch schema mismatches
- Runtime validation prevents invalid requests
- IDEs provide autocomplete and type checking
"""

from sentry_seer_types.codegen import CodeReviewTaskRequest

__version__ = "0.1.0"

__all__ = [
    "CodeReviewTaskRequest",
]
