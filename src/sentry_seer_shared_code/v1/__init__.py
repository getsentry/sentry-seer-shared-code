"""
Pydantic v1 compatible models for Sentry-Seer integration.

Use these models when working with Pydantic v1 (pydantic<2).
For example, in Sentry which currently uses Pydantic v1.

Example:
    from sentry_seer_shared_code.v1.code_review import SeerCodeReviewTaskRequestForPrReview
    from sentry_seer_shared_code.v1.code_review import SeerCodeReviewFeature
"""

from sentry_seer_shared_code.v1.code_review import (
    BugPredictionSpecificInformation,
    GitProvider,
    SeerCodeReviewConfig,
    SeerCodeReviewFeature,
    SeerCodeReviewRequestForPrClosed,
    SeerCodeReviewRequestForPrReview,
    SeerCodeReviewRequestType,
    SeerCodeReviewTaskRequestForPrClosed,
    SeerCodeReviewTaskRequestForPrReview,
    SeerCodeReviewTrigger,
    SeerRepoDefinition,
)

__all__ = [
    "BugPredictionSpecificInformation",
    "GitProvider",
    "SeerCodeReviewConfig",
    "SeerCodeReviewFeature",
    "SeerCodeReviewRequestForPrClosed",
    "SeerCodeReviewRequestForPrReview",
    "SeerCodeReviewRequestType",
    "SeerCodeReviewTaskRequestForPrClosed",
    "SeerCodeReviewTaskRequestForPrReview",
    "SeerCodeReviewTrigger",
    "SeerRepoDefinition",
]
