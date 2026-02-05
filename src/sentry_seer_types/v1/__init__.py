"""
Pydantic v1 compatible models for Sentry-Seer integration.

Use these models when working with Pydantic v1 (pydantic<2).
For example, in Sentry which currently uses Pydantic v1.

Example:
    from sentry_seer_types.v1.code_review import CodeReviewTaskRequest
    from sentry_seer_types.v1.code_review import PrReviewFeature
"""

from sentry_seer_types.v1.code_review import (
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

__all__ = [
    # Models
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
