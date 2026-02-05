"""
Code review request and configuration models (Pydantic v1).

This module contains the Pydantic v1 models for Sentry→Seer code review API calls.
All types, enums, and models are defined here to match the original Sentry structure.
"""

from enum import StrEnum
from typing import Any, Dict, Final, List, Literal, Optional

from pydantic import BaseModel, Field, root_validator


# =============================================================================
# Type Aliases
# =============================================================================

# Originally from: getsentry/sentry - src/sentry/seer/code_review/models.py
# Type alias for valid Git providers
GitProvider = Literal["github", "github_enterprise", "gitlab"]

# Originally from: getsentry/sentry - src/sentry/seer/code_review/models.py
# Type alias for PR review request types
RequestType = Literal["pr-review", "pr-closed"]


# =============================================================================
# Enums
# =============================================================================

# Originally from: getsentry/sentry - src/sentry/seer/code_review/models.py
class CommentSeverity(StrEnum):
    """
    Severity levels for code review comments using LOGAF classification.

    LOGAF (Low, Medium, High, Critical) is used to categorize the importance
    of issues found during code review.

    Originally defined in: getsentry/seer (Seer codebase)
    Ported to Sentry: src/sentry/seer/code_review/models.py (Jan 2026)
    Now maintained in: sentry-seer-types as the shared source of truth
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def meets_minimum(self, minimum_severity: "CommentSeverity") -> bool:
        """
        Check if this severity meets a given minimum severity threshold.

        Args:
            minimum_severity: The minimum severity level required

        Returns:
            True if this severity is at least as severe as the minimum
        """
        severity_rankings: Final[dict[str, int]] = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }
        return severity_rankings[self.value] >= severity_rankings[minimum_severity.value]


# Originally from: getsentry/sentry - src/sentry/seer/code_review/models.py
class PrReviewFeature(StrEnum):
    """
    Features available in PR review.

    Controls which AI-powered features are enabled for a given PR review run.

    Originally defined in: getsentry/seer (Seer codebase)
    Ported to Sentry: src/sentry/seer/code_review/models.py (Jan 2026)
    Now maintained in: sentry-seer-types as the shared source of truth
    """

    VANILLA = "vanilla"
    """Basic PR review without advanced features"""

    BUG_PREDICTION = "bug_prediction"
    """AI-powered bug prediction using static analysis and ML models"""


# Originally from: getsentry/sentry - src/sentry/seer/code_review/models.py
class PrReviewTrigger(StrEnum):
    """
    Events that trigger PR review execution.

    Determines what action caused Seer to start analyzing a PR.

    Originally defined in: getsentry/seer (Seer codebase)
    Ported to Sentry: src/sentry/seer/code_review/models.py (Jan 2026)
    Now maintained in: sentry-seer-types as the shared source of truth
    """

    UNKNOWN = "unknown"
    """Trigger source could not be determined"""

    ON_COMMAND_PHRASE = "on_command_phrase"
    """Triggered by a user comment containing a command phrase (e.g., '@sentry review')"""

    ON_READY_FOR_REVIEW = "on_ready_for_review"
    """Triggered when a PR moves from draft to ready for review"""

    ON_NEW_COMMIT = "on_new_commit"
    """Triggered when new commits are pushed to the PR"""

    @classmethod
    def _missing_(cls, value: object) -> "PrReviewTrigger":
        """
        Handle unknown trigger values gracefully.

        When an unknown trigger value is encountered, return UNKNOWN instead
        of raising a ValueError. This ensures backward compatibility when new
        triggers are added.
        """
        return cls.UNKNOWN


# =============================================================================
# Pydantic Models
# =============================================================================

# Originally from: getsentry/sentry - src/sentry/seer/code_review/models.py
class RepoDefinition(BaseModel):
    """
    Complete definition of a repository for code review operations.

    Contains all necessary information to identify and access a repository.

    Originally defined in: getsentry/seer (Seer codebase)
    Ported to Sentry: src/sentry/seer/code_review/models.py (Jan 2026)
    Now maintained in: sentry-seer-types as the shared source of truth
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


# Originally from: getsentry/sentry - src/sentry/seer/code_review/models.py
class BugPredictionSpecificInformation(BaseModel):
    """
    Additional configuration for bug prediction features.

    Contains organization context and limits for AI-powered bug prediction
    during code review.

    Originally defined in: getsentry/seer (Seer codebase)
    Ported to Sentry: src/sentry/seer/code_review/models.py (Jan 2026)
    Now maintained in: sentry-seer-types as the shared source of truth
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


# Originally from: getsentry/sentry - src/sentry/seer/code_review/models.py
class PrReviewConfig(BaseModel):
    """
    Configuration for PR review execution.

    Controls which features are enabled, how the review was triggered,
    and metadata about the trigger event.

    Originally defined in: getsentry/seer (Seer codebase)
    Ported to Sentry: src/sentry/seer/code_review/models.py (Jan 2026)
    Now maintained in: sentry-seer-types as the shared source of truth
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


# Originally from: getsentry/sentry - src/sentry/seer/code_review/models.py
class CodegenPrReviewRequest(BaseModel):
    """
    Complete request payload for PR review operations.

    This is the primary model validated when Sentry sends a PR review request to Seer.

    Originally defined in: getsentry/seer (Seer codebase)
    Ported to Sentry: src/sentry/seer/code_review/models.py (Jan 2026)
    Now maintained in: sentry-seer-types as the shared source of truth
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


# Originally from: getsentry/sentry - src/sentry/seer/code_review/models.py
class CodeReviewTaskRequest(BaseModel):
    """
    Wrapper for code review task requests.

    This is the top-level payload structure sent to Seer's /v1/automation/overwatch-request
    endpoint. It wraps the actual request data with request type and authentication info.

    Originally defined in: getsentry/seer (Seer codebase)
    Ported to Sentry: src/sentry/seer/code_review/models.py (Jan 2026)
    Now maintained in: sentry-seer-types as the shared source of truth
    """

    request_type: RequestType = Field(description="Type of code review operation to perform")
    external_owner_id: str = Field(
        description="External repository owner ID for authentication"
    )
    data: CodegenPrReviewRequest = Field(description="The actual request data for the operation")
