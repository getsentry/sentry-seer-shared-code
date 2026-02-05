"""
Pydantic v2 compatible models for Sentry-Seer integration.

Use these models when working with Pydantic v2 (pydantic>=2).
For example, in Seer which uses Pydantic v2.

Example:
    from sentry_seer_types.v2.codegen import CodeReviewTaskRequest
    from sentry_seer_types.v2.types import PrReviewFeature
"""

from sentry_seer_types.v2.base import BranchOverride, FileChange, FileChangeError, RepoDefinition
from sentry_seer_types.v2.codegen import (
    BugPredictionSpecificInformation,
    CodegenBaseRequest,
    CodegenPrReviewRequest,
    CodeReviewTaskRequest,
    PrReviewConfig,
)
from sentry_seer_types.v2.types import (
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
