"""
Code review request and configuration models (Pydantic v1).

This module contains the Pydantic v1 models for Sentry→Seer code review API calls.
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, root_validator

from sentry_seer_types.v1.code_review.types import (
    GitProvider,
    PrReviewFeature,
    PrReviewTrigger,
    RequestType,
)


class RepoDefinition(BaseModel):
    """
    Complete definition of a repository for code review operations.

    Contains all necessary information to identify and access a repository.
    """

    organization_id: Optional[int] = Field(default=None, description="Sentry organization ID")
    integration_id: Optional[str] = Field(
        default=None, description="Integration ID for accessing the repository"
    )
    provider: GitProvider = Field(
        description="Git provider type (github, github_enterprise, gitlab)"
    )
    owner: str = Field(description="Repository owner (organization or user)")
    name: str = Field(description="Repository name")
    external_id: str = Field(description="External repository ID from the provider")
    base_commit_sha: Optional[str] = Field(
        default=None,
        description="Base commit SHA for PR review (the HEAD of the PR)",
    )
    provider_raw: Optional[str] = Field(
        default=None,
        description="Original provider string before normalization",
    )

    @property
    def full_name(self) -> str:
        """Get the full repository name in 'owner/name' format."""
        return f"{self.owner}/{self.name}"

    @root_validator(pre=True)
    def store_provider_raw(cls, values: Any) -> Any:
        """Store the original provider value before Pydantic validates it."""
        if isinstance(values, dict) and "provider" in values and "provider_raw" not in values:
            values["provider_raw"] = values["provider"]
        return values


class BugPredictionSpecificInformation(BaseModel):
    """
    Additional configuration for bug prediction features.

    Contains organization context and limits for AI-powered bug prediction
    during code review.
    """

    callback_url: Optional[str] = Field(
        default=None,
        description="URL to call back with results when analysis completes",
    )
    organization_id: Optional[int] = Field(
        default=None,
        description="Sentry organization ID for context and billing",
    )
    organization_slug: Optional[str] = Field(
        default=None,
        description="Sentry organization slug for display purposes",
    )
    warnings: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Static analysis warnings to incorporate into bug prediction",
    )
    max_num_associations: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of code associations to analyze per prediction",
    )
    max_num_issues_analyzed: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of issues to analyze in parallel",
    )
    should_post_to_overwatch: bool = Field(
        default=False,
        description="Whether to post results to Overwatch monitoring system",
    )
    should_publish_comments: bool = Field(
        default=False,
        description="Whether to publish findings as GitHub PR comments",
    )
    is_local_run: bool = Field(
        default=False,
        description="True if running in local development mode",
    )


class PrReviewConfig(BaseModel):
    """
    Configuration for PR review execution.

    Controls which features are enabled, how the review was triggered,
    and metadata about the trigger event.
    """

    features: Dict[PrReviewFeature, bool] = Field(
        default_factory=lambda: {PrReviewFeature.VANILLA: True},
        description="Map of feature names to enabled/disabled status",
    )
    trigger: PrReviewTrigger = Field(
        default=PrReviewTrigger.ON_COMMAND_PHRASE,
        description="Event that triggered this PR review",
    )
    trigger_comment_id: Optional[int] = Field(
        default=None,
        description="GitHub comment ID that triggered review (if trigger was a comment)",
    )
    trigger_comment_type: Optional[Literal["issue_comment", "pull_request_review_comment"]] = Field(
        default=None,
        description="Type of comment that triggered review",
    )
    trigger_user: Optional[str] = Field(
        default=None,
        description="GitHub username of the user who triggered review",
    )
    trigger_user_id: Optional[int] = Field(
        default=None,
        description="GitHub user ID of the user who triggered review",
    )

    def is_feature_enabled(self, feature: PrReviewFeature) -> bool:
        """Check if a specific feature is enabled in this configuration."""
        return self.features.get(feature, False)


class CodegenPrReviewRequest(BaseModel):
    """
    Complete request payload for PR review operations.

    This is the primary model validated when Sentry sends a PR review request to Seer.
    """

    repo: RepoDefinition = Field(description="Repository containing the code/PR to analyze")
    pr_id: int = Field(description="Pull request number", gt=0)
    codecov_status: Optional[Dict[str, str]] = Field(
        default=None,
        description="Codecov test coverage status for the PR",
    )
    more_readable_repos: List[RepoDefinition] = Field(
        default_factory=list,
        description="Additional repositories accessible for code search and context",
    )
    bug_prediction_specific_information: Optional[BugPredictionSpecificInformation] = Field(
        default=None,
        description="Bug prediction configuration (if feature is enabled)",
    )
    config: Optional[PrReviewConfig] = Field(
        default=None,
        description="PR review execution configuration",
    )


class CodeReviewTaskRequest(BaseModel):
    """
    Wrapper for code review task requests.

    This is the top-level payload structure sent to Seer's /v1/automation/overwatch-request
    endpoint. It wraps the actual request data with request type and authentication info.
    """

    request_type: RequestType = Field(description="Type of code review operation to perform")
    external_owner_id: str = Field(
        description="External repository owner ID for authentication"
    )
    data: CodegenPrReviewRequest = Field(description="The actual request data for the operation")
