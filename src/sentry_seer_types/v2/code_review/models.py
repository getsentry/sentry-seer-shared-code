"""
Code review request and configuration models (Pydantic v2).

This module contains the Pydantic v2 models for Sentry→Seer code review API calls.
"""

from typing import Annotated, Any, Dict, List, Literal

from pydantic import BaseModel, Field, model_validator

from sentry_seer_types.v2.code_review.types import (
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

    organization_id: Annotated[
        int | None, Field(default=None, description="Sentry organization ID")
    ]
    integration_id: Annotated[
        str | None,
        Field(default=None, description="Integration ID for accessing the repository"),
    ]
    provider: Annotated[
        GitProvider,
        Field(description="Git provider type (github, github_enterprise, gitlab)"),
    ]
    owner: Annotated[str, Field(description="Repository owner (organization or user)")]
    name: Annotated[str, Field(description="Repository name")]
    external_id: Annotated[str, Field(description="External repository ID from the provider")]
    base_commit_sha: Annotated[
        str | None,
        Field(
            default=None,
            description="Base commit SHA for PR review (the HEAD of the PR)",
        ),
    ]
    provider_raw: Annotated[
        str | None,
        Field(
            default=None,
            description="Original provider string before normalization",
        ),
    ]

    @property
    def full_name(self) -> str:
        """Get the full repository name in 'owner/name' format."""
        return f"{self.owner}/{self.name}"

    @model_validator(mode="before")
    @classmethod
    def store_provider_raw(cls, data: Any) -> Any:
        """Store the original provider value before Pydantic validates it."""
        if isinstance(data, dict) and "provider" in data and "provider_raw" not in data:
            data["provider_raw"] = data["provider"]
        return data


class BugPredictionSpecificInformation(BaseModel):
    """
    Additional configuration for bug prediction features.

    Contains organization context and limits for AI-powered bug prediction
    during code review.
    """

    callback_url: Annotated[
        str | None,
        Field(
            default=None,
            description="URL to call back with results when analysis completes",
        ),
    ]
    organization_id: Annotated[
        int | None,
        Field(
            default=None,
            description="Sentry organization ID for context and billing",
        ),
    ]
    organization_slug: Annotated[
        str | None,
        Field(
            default=None,
            description="Sentry organization slug for display purposes",
        ),
    ]
    warnings: Annotated[
        list[dict[str, Any]],
        Field(
            default_factory=list,
            description="Static analysis warnings to incorporate into bug prediction",
        ),
    ]
    max_num_associations: Annotated[
        int,
        Field(
            default=10,
            ge=1,
            le=100,
            description="Maximum number of code associations to analyze per prediction",
        ),
    ]
    max_num_issues_analyzed: Annotated[
        int,
        Field(
            default=10,
            ge=1,
            le=50,
            description="Maximum number of issues to analyze in parallel",
        ),
    ]
    should_post_to_overwatch: Annotated[
        bool,
        Field(
            default=False,
            description="Whether to post results to Overwatch monitoring system",
        ),
    ]
    should_publish_comments: Annotated[
        bool,
        Field(
            default=False,
            description="Whether to publish findings as GitHub PR comments",
        ),
    ]
    is_local_run: Annotated[
        bool,
        Field(
            default=False,
            description="True if running in local development mode",
        ),
    ]


class PrReviewConfig(BaseModel):
    """
    Configuration for PR review execution.

    Controls which features are enabled, how the review was triggered,
    and metadata about the trigger event.
    """

    features: Annotated[
        dict[PrReviewFeature, bool],
        Field(
            default_factory=lambda: {PrReviewFeature.VANILLA: True},
            description="Map of feature names to enabled/disabled status",
        ),
    ]
    trigger: Annotated[
        PrReviewTrigger,
        Field(
            default=PrReviewTrigger.ON_COMMAND_PHRASE,
            description="Event that triggered this PR review",
        ),
    ]
    trigger_comment_id: Annotated[
        int | None,
        Field(
            default=None,
            description="GitHub comment ID that triggered review (if trigger was a comment)",
        ),
    ]
    trigger_comment_type: Annotated[
        Literal["issue_comment", "pull_request_review_comment"] | None,
        Field(
            default=None,
            description="Type of comment that triggered review",
        ),
    ]
    trigger_user: Annotated[
        str | None,
        Field(
            default=None,
            description="GitHub username of the user who triggered review",
        ),
    ]
    trigger_user_id: Annotated[
        int | None,
        Field(
            default=None,
            description="GitHub user ID of the user who triggered review",
        ),
    ]

    def is_feature_enabled(self, feature: PrReviewFeature) -> bool:
        """Check if a specific feature is enabled in this configuration."""
        return self.features.get(feature, False)


class CodegenPrReviewRequest(BaseModel):
    """
    Complete request payload for PR review operations.

    This is the primary model validated when Sentry sends a PR review request to Seer.
    """

    repo: Annotated[RepoDefinition, Field(description="Repository containing the code/PR to analyze")]
    pr_id: Annotated[int, Field(description="Pull request number", gt=0)]
    codecov_status: Annotated[
        dict[str, str] | None,
        Field(
            default=None,
            description="Codecov test coverage status for the PR",
        ),
    ]
    more_readable_repos: Annotated[
        list[RepoDefinition],
        Field(
            default_factory=list,
            description="Additional repositories accessible for code search and context",
        ),
    ]
    bug_prediction_specific_information: Annotated[
        BugPredictionSpecificInformation | None,
        Field(
            default=None,
            description="Bug prediction configuration (if feature is enabled)",
        ),
    ]
    config: Annotated[
        PrReviewConfig | None,
        Field(
            default=None,
            description="PR review execution configuration",
        ),
    ]


class CodeReviewTaskRequest(BaseModel):
    """
    Wrapper for code review task requests.

    This is the top-level payload structure sent to Seer's /v1/automation/overwatch-request
    endpoint. It wraps the actual request data with request type and authentication info.
    """

    request_type: Annotated[RequestType, Field(description="Type of code review operation to perform")]
    external_owner_id: Annotated[str, Field(description="External repository owner ID for authentication")]
    data: Annotated[CodegenPrReviewRequest, Field(description="The actual request data for the operation")]
