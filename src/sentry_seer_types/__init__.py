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
    - Use `sentry_seer_types.v2.*` for Pydantic v2 (pydantic>=2)
    
    By default, imports from the root use v2 (for Seer compatibility).

Examples:
    # In Seer (Pydantic v2)
    from sentry_seer_types import CodeReviewTaskRequest
    # or explicitly:
    from sentry_seer_types.v2 import CodeReviewTaskRequest
    
    # In Sentry (Pydantic v1)
    from sentry_seer_types.v1 import CodeReviewTaskRequest
"""

# Default to v2 for backward compatibility with Seer (if pydantic v2 is installed)
# Otherwise use v1
try:
    from sentry_seer_types.v2.code_review import (
        CommentSeverity,
        GitProvider,
        SeerCodeReviewFeature,
        SeerCodeReviewRequestType,
        SeerCodeReviewTrigger,
    )
except ImportError:
    # Fallback to v1 if pydantic v2 is not available
    from sentry_seer_types.v1.code_review import (  # type: ignore[assignment]
        BugPredictionSpecificInformation,
        CommentSeverity,
        GitProvider,
        RepoDefinition,
        SeerCodeReviewConfig,
        SeerCodeReviewFeature,
        SeerCodeReviewRequestForPrReview,
        SeerCodeReviewRequestType,
        SeerCodeReviewTaskRequestForPrReview,
        SeerCodeReviewTrigger,
    )

__version__ = "0.1.0"

__all__ = [
    # Models (only from v1, v2 doesn't have models yet)
    "BugPredictionSpecificInformation",
    "RepoDefinition",
    "SeerCodeReviewConfig",
    "SeerCodeReviewRequestForPrReview",
    "SeerCodeReviewTaskRequestForPrReview",
    # Types and enums
    "CommentSeverity",
    "GitProvider",
    "SeerCodeReviewFeature",
    "SeerCodeReviewRequestType",
    "SeerCodeReviewTrigger",
]
