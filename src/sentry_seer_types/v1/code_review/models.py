"""
Code review request and configuration models (Pydantic v1).

This module contains the Pydantic v1 models for Sentry→Seer code review API calls.
All types, enums, and models are defined here to match the original Sentry structure.

Unless otherwise stated, all classes are from: getsentry/sentry - src/sentry/seer/code_review/models.py
"""
import datetime
from __future__ import annotations
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, root_validator


# =============================================================================
# Type Aliases
# =============================================================================


# Type alias for valid Git providers
GitProvider = Literal["github", "github_enterprise", "gitlab"]


# Type alias for PR review request types
SeerCodeReviewRequestType = Literal["pr-review", "pr-closed"]


# =============================================================================
# Enums
# =============================================================================


class SeerCodeReviewFeature(StrEnum):
    BUG_PREDICTION = "bug_prediction"



class SeerCodeReviewTrigger(StrEnum):
    UNKNOWN = "unknown"
    ON_COMMAND_PHRASE = "on_command_phrase"
    ON_READY_FOR_REVIEW = "on_ready_for_review"
    ON_NEW_COMMIT = "on_new_commit"

    @classmethod
    def _missing_(cls: type[SeerCodeReviewTrigger], value: object) -> SeerCodeReviewTrigger:
        return cls.UNKNOWN


# =============================================================================
# Pydantic Models
# =============================================================================



class BugPredictionSpecificInformation(BaseModel):
    """Information specific to bug prediction feature."""

    organization_id: int
    organization_slug: str



class SeerCodeReviewConfig(BaseModel):
    features: dict[SeerCodeReviewFeature, bool] = Field(default_factory=lambda: {})
    trigger: SeerCodeReviewTrigger
    trigger_comment_id: int | None = None
    trigger_comment_type: Literal["issue_comment"] | None = None
    trigger_user: str | None = None
    trigger_user_id: int | None = None
    trigger_at: datetime | None = None  # When the trigger event occurred on GitHub
    sentry_received_trigger_at: datetime | None = None  # When Sentry received the webhook

    def is_feature_enabled(self, feature: SeerCodeReviewFeature) -> bool:
        return self.features.get(feature, False)



class SeerCodeReviewRequestForPrReview(BaseModel):
    """
    Complete request payload for PR review operations.

    This is the primary model validated when Sentry sends a PR review request to Seer.

    Originally defined in: getsentry/seer (Seer codebase)
    Ported to Sentry: src/sentry/seer/code_review/models.py (Jan 2026)
    Now maintained in: sentry-seer-types as the shared source of truth
    """

    repo: RepoDefinition = Field(description="Repository containing the code/PR to analyze")
    pr_id: int = Field(description="Pull request number", gt=0)
    codecov_status: Dict[str, str] | None = Field(
        default=None,
        description="Codecov test coverage status for the PR",
    )
    more_readable_repos: List[RepoDefinition] = Field(
        default_factory=list,
        description="Additional repositories accessible for code search and context",
    )
    bug_prediction_specific_information: BugPredictionSpecificInformation | None = Field(
        default=None,
        description="Bug prediction configuration (if feature is enabled)",
    )
    config: SeerCodeReviewConfig | None = Field(
        default=None,
        description="PR review execution configuration",
    )



class SeerCodeReviewTaskRequestForPrReview(BaseModel):
    """
    Wrapper for code review task requests.

    This is the top-level payload structure sent to Seer's /v1/automation/overwatch-request
    endpoint. It wraps the actual request data with request type and authentication info.

    Originally defined in: getsentry/seer (Seer codebase)
    Ported to Sentry: src/sentry/seer/code_review/models.py (Jan 2026)
    Now maintained in: sentry-seer-types as the shared source of truth
    """

    request_type: SeerCodeReviewRequestType = Field(description="Type of code review operation to perform")
    external_owner_id: str = Field(
        description="External repository owner ID for authentication"
    )
    data: SeerCodeReviewRequestForPrReview = Field(description="The actual request data for the operation")



class SeerCodeReviewRequestForPrClosed(BaseModel):
    """
    Request payload for PR closed operations.

    Similar to PrReview but for when a PR is closed, used for metrics and cleanup.

    Originally defined in: getsentry/sentry - src/sentry/seer/code_review/models.py
    """

    repo: RepoDefinition = Field(description="Repository containing the closed PR")
    pr_id: int = Field(description="Pull request number", gt=0)
    more_readable_repos: List[RepoDefinition] = Field(
        default_factory=list,
        description="Additional repositories accessible for code search and context",
    )
    bug_prediction_specific_information: BugPredictionSpecificInformation | None = Field(
        default=None,
        description="Bug prediction configuration (if feature is enabled)",
    )
    config: SeerCodeReviewConfig | None = Field(
        default=None,
        description="PR review execution configuration",
    )



class SeerCodeReviewTaskRequestForPrClosed(BaseModel):
    """
    Wrapper for PR closed task requests.

    This is sent when a PR is closed to trigger cleanup or final metrics collection.

    Originally defined in: getsentry/sentry - src/sentry/seer/code_review/models.py
    """

    request_type: SeerCodeReviewRequestType = Field(description="Type of code review operation to perform")
    external_owner_id: str = Field(
        description="External repository owner ID for authentication"
    )
    data: SeerCodeReviewRequestForPrClosed = Field(description="The actual request data for the operation")
