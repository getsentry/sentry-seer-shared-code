"""
Pydantic v2 compatible models for Sentry-Seer integration.

Use these models when working with Pydantic v2 (pydantic>=2).
For example, in Seer which uses Pydantic v2.

Example:
    from sentry_seer_types.v2.code_review import CodeReviewTaskRequest
    from sentry_seer_types.v2.code_review import PrReviewFeature
"""

from sentry_seer_types.v2.code_review import (
    BugPredictionSpecificInformation,
    CodegenPrReviewRequest,
    CodeReviewTaskRequest,
    CommentSeverity,
    GitProvider,
    PrReviewConfig,
    PrReviewFeature,
    PrReviewTrigger,
    RepoDefinition,
    RequestType,
)

__all__ = [
    # Models
    "BugPredictionSpecificInformation",
    "CodegenPrReviewRequest",
    "CodeReviewTaskRequest",
    "PrReviewConfig",
    "RepoDefinition",
    # Types and enums
    "CommentSeverity",
    "GitProvider",
    "PrReviewFeature",
    "PrReviewTrigger",
    "RequestType",
]
