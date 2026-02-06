"""
Tests for Pydantic v1 code review models.

Validates the structure of payloads sent from Sentry to Seer for code review.
These tests ensure backward compatibility and correct validation behavior.
"""

import pytest
from pydantic import ValidationError

from sentry_seer_shared_code.v1.code_review import (
    BugPredictionSpecificInformation,
    SeerCodeReviewConfig,
    SeerCodeReviewFeature,
    SeerCodeReviewRequestForPrReview,
    SeerCodeReviewTaskRequestForPrReview,
    SeerCodeReviewTrigger,
    SeerRepoDefinition,
)


class TestBugPredictionSpecificInformation:
    """Test bug prediction configuration model."""

    def test_required_fields(self) -> None:
        """organization_id and organization_slug are required."""
        info = BugPredictionSpecificInformation(
            organization_id=123,
            organization_slug="my-org",
        )
        assert info.organization_id == 123
        assert info.organization_slug == "my-org"

    def test_with_all_fields(self) -> None:
        """All fields should be accepted when provided."""
        info = BugPredictionSpecificInformation(
            organization_id=456,
            organization_slug="other-org",
        )
        assert info.organization_id == 456
        assert info.organization_slug == "other-org"

    def test_missing_organization_id_raises(self) -> None:
        """organization_id is required."""
        with pytest.raises(ValidationError):
            BugPredictionSpecificInformation(organization_slug="my-org")

    def test_missing_organization_slug_raises(self) -> None:
        """organization_slug is required."""
        with pytest.raises(ValidationError):
            BugPredictionSpecificInformation(organization_id=123)


class TestSeerCodeReviewConfig:
    """Test PR review configuration model."""

    def test_default_features_empty(self) -> None:
        """Default config should have empty features dict."""
        config = SeerCodeReviewConfig(trigger=SeerCodeReviewTrigger.ON_COMMAND_PHRASE)
        assert config.features == {}
        assert not config.is_feature_enabled(SeerCodeReviewFeature.BUG_PREDICTION)

    def test_default_trigger(self) -> None:
        """Trigger is required; ON_COMMAND_PHRASE is a valid value."""
        config = SeerCodeReviewConfig(trigger=SeerCodeReviewTrigger.ON_COMMAND_PHRASE)
        assert config.trigger == SeerCodeReviewTrigger.ON_COMMAND_PHRASE

    def test_is_feature_enabled_returns_false_for_disabled(self) -> None:
        """Should return False for features not in config or explicitly disabled."""
        config = SeerCodeReviewConfig(
            features={SeerCodeReviewFeature.BUG_PREDICTION: False},
            trigger=SeerCodeReviewTrigger.ON_COMMAND_PHRASE,
        )
        assert not config.is_feature_enabled(SeerCodeReviewFeature.BUG_PREDICTION)

    def test_is_feature_enabled_returns_true_when_enabled(self) -> None:
        """Should return True for features explicitly enabled."""
        config = SeerCodeReviewConfig(
            features={SeerCodeReviewFeature.BUG_PREDICTION: True},
            trigger=SeerCodeReviewTrigger.ON_COMMAND_PHRASE,
        )
        assert config.is_feature_enabled(SeerCodeReviewFeature.BUG_PREDICTION)

    def test_with_trigger_metadata(self) -> None:
        """Trigger metadata fields should be accepted."""
        config = SeerCodeReviewConfig(
            features={},
            trigger=SeerCodeReviewTrigger.ON_COMMAND_PHRASE,
            trigger_comment_id=123456,
            trigger_comment_type="issue_comment",
            trigger_user="octocat",
            trigger_user_id=99999,
        )
        assert config.trigger_comment_id == 123456
        assert config.trigger_user == "octocat"
        assert config.trigger_user_id == 99999

    def test_ready_for_review_trigger(self) -> None:
        """ON_READY_FOR_REVIEW trigger should have no comment metadata."""
        config = SeerCodeReviewConfig(
            features={},
            trigger=SeerCodeReviewTrigger.ON_READY_FOR_REVIEW,
            trigger_user="pr-author",
            trigger_user_id=12345,
        )
        assert config.trigger == SeerCodeReviewTrigger.ON_READY_FOR_REVIEW
        assert config.trigger_comment_id is None
        assert config.trigger_comment_type is None


class TestSeerCodeReviewRequestForPrReview:
    """Test full PR review request payload."""

    def test_minimal_pr_review_request(self) -> None:
        """PR review request with only required fields should be valid."""
        repo = SeerRepoDefinition(
            provider="github",
            owner="getsentry",
            name="sentry",
            external_id="123",
        )
        request = SeerCodeReviewRequestForPrReview(
            repo=repo,
            pr_id=42,
        )
        assert request.pr_id == 42
        assert request.bug_prediction_specific_information is None
        assert request.config is None

    def test_full_pr_review_request(self) -> None:
        """PR review request with all fields should be valid."""
        repo = SeerRepoDefinition(
            provider="github",
            owner="getsentry",
            name="sentry",
            external_id="123",
            base_commit_sha="abc123",
        )
        bug_info = BugPredictionSpecificInformation(
            organization_id=789,
            organization_slug="my-company",
        )
        config = SeerCodeReviewConfig(
            features={SeerCodeReviewFeature.BUG_PREDICTION: True},
            trigger=SeerCodeReviewTrigger.ON_READY_FOR_REVIEW,
            trigger_user="developer",
            trigger_user_id=55555,
        )
        request = SeerCodeReviewRequestForPrReview(
            repo=repo,
            pr_id=123,
            bug_prediction_specific_information=bug_info,
            config=config,
        )
        assert request.pr_id == 123
        assert request.bug_prediction_specific_information is not None
        assert request.bug_prediction_specific_information.organization_id == 789
        assert request.config is not None
        assert request.config.is_feature_enabled(SeerCodeReviewFeature.BUG_PREDICTION)


class TestSeerCodeReviewTaskRequestForPrReview:
    """Test complete code review task request wrapper."""

    def test_pr_review_task_request(self) -> None:
        """Complete PR review task request should validate correctly."""
        repo = SeerRepoDefinition(
            provider="github",
            owner="getsentry",
            name="sentry",
            external_id="123456",
            base_commit_sha="def456",
        )
        pr_review_data = SeerCodeReviewRequestForPrReview(
            repo=repo,
            pr_id=42,
            bug_prediction_specific_information=BugPredictionSpecificInformation(
                organization_id=999,
                organization_slug="test-org",
            ),
            config=SeerCodeReviewConfig(
                features={SeerCodeReviewFeature.BUG_PREDICTION: True},
                trigger=SeerCodeReviewTrigger.ON_COMMAND_PHRASE,
                trigger_comment_id=77777,
                trigger_user="reviewer",
            ),
        )
        task_request = SeerCodeReviewTaskRequestForPrReview(
            request_type="pr-review",
            external_owner_id="123456",
            data=pr_review_data,
        )

        assert task_request.request_type == "pr-review"
        assert task_request.external_owner_id == "123456"
        assert task_request.data.pr_id == 42
        assert task_request.data.repo.full_name == "getsentry/sentry"

    def test_task_request_validates_nested_models(self) -> None:
        """Validation errors in nested models should be caught."""
        repo = SeerRepoDefinition(
            provider="github",
            owner="test",
            name="repo",
            external_id="1",
        )
        pr_review_data = SeerCodeReviewRequestForPrReview(
            repo=repo,
            pr_id=42,
        )
        task_request = SeerCodeReviewTaskRequestForPrReview(
            request_type="pr-review",
            external_owner_id="1",
            data=pr_review_data,
        )

        # Test serialization round-trip maintains structure
        serialized = task_request.dict()
        assert serialized["request_type"] == "pr-review"
        assert serialized["data"]["pr_id"] == 42

        # Test deserialization
        restored = SeerCodeReviewTaskRequestForPrReview.parse_obj(serialized)
        assert restored.data.pr_id == 42

    def test_task_request_with_dict_payload(self) -> None:
        """Should be able to validate from dictionary (Sentry use case)."""
        payload = {
            "request_type": "pr-review",
            "external_owner_id": "123456",
            "data": {
                "repo": {
                    "provider": "github",
                    "owner": "getsentry",
                    "name": "sentry",
                    "external_id": "123456",
                    "base_commit_sha": "abc123",
                },
                "pr_id": 42,
                "bug_prediction_specific_information": {
                    "organization_id": 789,
                    "organization_slug": "test-org",
                },
                "config": {
                    "features": {"bug_prediction": True},
                    "trigger": "on_ready_for_review",
                    "trigger_user": "developer",
                    "trigger_user_id": 12345,
                },
            },
        }

        # This is the critical test - validating Sentry's payload
        validated = SeerCodeReviewTaskRequestForPrReview.parse_obj(payload)
        assert validated.request_type == "pr-review"
        assert validated.data.pr_id == 42
        assert validated.data.config is not None
        assert validated.data.config.trigger == SeerCodeReviewTrigger.ON_READY_FOR_REVIEW
