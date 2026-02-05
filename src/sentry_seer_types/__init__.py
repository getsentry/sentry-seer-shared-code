"""
Shared Pydantic models for Sentry and Seer code review integration.

This package provides type-safe data models for validating payloads sent from
Sentry to Seer's code review API. Using shared models ensures:
- Tests catch schema mismatches
- Runtime validation prevents invalid requests
- IDEs provide autocomplete and type checking

Pydantic Version Support:
    This package supports both Pydantic v1 and v2:
    
    - Use `sentry_seer_types.v1.*` for Pydantic v1 (pydantic<2)
    - Use `sentry_seer_types.v2.*` for Pydantic v2 (pydantic>=2) - reserved for future use
    
    Currently, all models are in v1 which works with both Pydantic versions.

Examples:
    # In Sentry (Pydantic v1)
    from sentry_seer_types.v1 import SeerCodeReviewConfig
    
    # In Seer (Pydantic v2) - use v1 models for now
    from sentry_seer_types.v1 import SeerCodeReviewConfig
"""

from sentry_seer_types.v1.code_review import (
    BugPredictionSpecificInformation,
    GitProvider,
    RepoDefinition,
    SeerCodeReviewConfig,
    SeerCodeReviewFeature,
    SeerCodeReviewRequestForPrClosed,
    SeerCodeReviewRequestForPrReview,
    SeerCodeReviewRequestType,
    SeerCodeReviewTaskRequestForPrClosed,
    SeerCodeReviewTaskRequestForPrReview,
    SeerCodeReviewTrigger,
)

__version__ = "0.1.0"

__all__ = [
    # Models
    "BugPredictionSpecificInformation",
    "RepoDefinition",
    "SeerCodeReviewConfig",
    "SeerCodeReviewRequestForPrClosed",
    "SeerCodeReviewRequestForPrReview",
    "SeerCodeReviewTaskRequestForPrClosed",
    "SeerCodeReviewTaskRequestForPrReview",
    # Types and enums
    "GitProvider",
    "SeerCodeReviewFeature",
    "SeerCodeReviewRequestType",
    "SeerCodeReviewTrigger",
]
