"""
Type definitions and enums for code review features.

This module contains enums and type definitions used in the Sentry-Seer
code review integration.
"""

from enum import StrEnum
from typing import Final, Literal

# Type alias for valid Git providers
# Originally from getsentry/seer, now shared via sentry-seer-types
GitProvider = Literal["github", "github_enterprise", "gitlab"]

# Type alias for PR review request types
# Originally from getsentry/seer, now shared via sentry-seer-types
RequestType = Literal["pr-review", "pr-closed"]


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
