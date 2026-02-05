"""
Pydantic v1 compatible models for Sentry-Seer integration.

Use these models when working with Pydantic v1 (pydantic<2).
For example, in Sentry which currently uses Pydantic v1.

Example:
    from sentry_seer_types.v1.codegen import CodeReviewTaskRequest
    from sentry_seer_types.v1.types import PrReviewFeature
"""

from sentry_seer_types.v1.base import BranchOverride, FileChange, FileChangeError, RepoDefinition
from sentry_seer_types.v1.codegen import (
    BugPredictionSpecificInformation,
    CodegenBaseRequest,
    CodegenPrReviewRequest,
    CodeReviewTaskRequest,
    PrReviewConfig,
)
from sentry_seer_types.v1.types import (
    ChangeType,
    CommentSeverity,
    GitProvider,
    PrReviewFeature,
    PrReviewTrigger,
    RequestType,
)

__all__ = [
    # Base models
    "BranchOverride",
    "FileChange",
    "FileChangeError",
    "RepoDefinition",
    # Codegen models
    "BugPredictionSpecificInformation",
    "CodegenBaseRequest",
    "CodegenPrReviewRequest",
    "CodeReviewTaskRequest",
    "PrReviewConfig",
    # Types and enums
    "ChangeType",
    "CommentSeverity",
    "GitProvider",
    "PrReviewFeature",
    "PrReviewTrigger",
    "RequestType",
]
