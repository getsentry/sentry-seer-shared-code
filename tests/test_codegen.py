"""
Tests for Pydantic v1 code review models.

Validates the structure of payloads sent from Sentry to Seer for code review.
These tests ensure backward compatibility and correct validation behavior.
"""

import pytest
from pydantic import ValidationError

from sentry_seer_types.v1.code_review import (
    BugPredictionSpecificInformation,
    CodegenPrReviewRequest,
    CodeReviewTaskRequest,
    PrReviewConfig,
    PrReviewFeature,
    PrReviewTrigger,
    RepoDefinition,
)


class TestBugPredictionSpecificInformation:
    """Test bug prediction configuration model."""

    def test_default_values(self) -> None:
        """Default values should be sensible for production use."""
        info = BugPredictionSpecificInformation()
        assert info.callback_url is None
        assert info.organization_id is None
        assert info.organization_slug is None
        assert info.warnings == []
        assert info.max_num_associations == 10
        assert info.max_num_issues_analyzed == 10
        assert info.should_post_to_overwatch is False
        assert info.should_publish_comments is False
        assert info.is_local_run is False

    def test_with_all_fields(self) -> None:
        """All fields should be accepted when provided."""
        info = BugPredictionSpecificInformation(
            callback_url="https://sentry.io/callback",
            organization_id=123,
            organization_slug="my-org",
            warnings=[{"file": "test.py", "line": 10, "message": "Unused variable"}],
            max_num_associations=20,
            max_num_issues_analyzed=15,
            should_post_to_overwatch=True,
            should_publish_comments=True,
            is_local_run=True,
        )
        assert info.organization_id == 123
        assert info.max_num_associations == 20
        assert info.should_post_to_overwatch is True

    def test_max_num_associations_must_be_positive(self) -> None:
        """max_num_associations must be >= 1."""
        with pytest.raises(ValidationError):
            BugPredictionSpecificInformation(max_num_associations=0)

    def test_max_num_associations_has_upper_limit(self) -> None:
        """max_num_associations should not exceed 100."""
        with pytest.raises(ValidationError):
            BugPredictionSpecificInformation(max_num_associations=101)

    def test_max_num_issues_analyzed_must_be_positive(self) -> None:
        """max_num_issues_analyzed must be >= 1."""
        with pytest.raises(ValidationError):
            BugPredictionSpecificInformation(max_num_issues_analyzed=0)

    def test_max_num_issues_analyzed_has_upper_limit(self) -> None:
        """max_num_issues_analyzed should not exceed 50."""
        with pytest.raises(ValidationError):
            BugPredictionSpecificInformation(max_num_issues_analyzed=51)


class TestPrReviewConfig:
    """Test PR review configuration model."""

    def test_default_vanilla_feature_enabled(self) -> None:
        """Default config should have vanilla feature enabled."""
        config = PrReviewConfig()
        assert config.features == {PrReviewFeature.VANILLA: True}
        assert config.is_feature_enabled(PrReviewFeature.VANILLA)

    def test_default_trigger(self) -> None:
        """Default trigger should be ON_COMMAND_PHRASE."""
        config = PrReviewConfig()
        assert config.trigger == PrReviewTrigger.ON_COMMAND_PHRASE

    def test_is_feature_enabled_returns_false_for_disabled(self) -> None:
        """Should return False for features not in config or explicitly disabled."""
        config = PrReviewConfig(
            features={
                PrReviewFeature.VANILLA: True,
                PrReviewFeature.BUG_PREDICTION: False,
            }
        )
        assert config.is_feature_enabled(PrReviewFeature.VANILLA)
        assert not config.is_feature_enabled(PrReviewFeature.BUG_PREDICTION)

    def test_with_trigger_metadata(self) -> None:
        """Trigger metadata fields should be accepted."""
        config = PrReviewConfig(
            trigger=PrReviewTrigger.ON_COMMAND_PHRASE,
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
        config = PrReviewConfig(
            trigger=PrReviewTrigger.ON_READY_FOR_REVIEW,
            trigger_user="pr-author",
            trigger_user_id=12345,
        )
        assert config.trigger == PrReviewTrigger.ON_READY_FOR_REVIEW
        assert config.trigger_comment_id is None
        assert config.trigger_comment_type is None




class TestCodegenPrReviewRequest:
    """Test full PR review request payload."""

    def test_minimal_pr_review_request(self) -> None:
        """PR review request with only required fields should be valid."""
        repo = RepoDefinition(
            provider="github",
            owner="getsentry",
            name="sentry",
            external_id="123",
        )
        request = CodegenPrReviewRequest(
            repo=repo,
            pr_id=42,
        )
        assert request.pr_id == 42
        assert request.bug_prediction_specific_information is None
        assert request.config is None

    def test_full_pr_review_request(self) -> None:
        """PR review request with all fields should be valid."""
        repo = RepoDefinition(
            provider="github",
            owner="getsentry",
            name="sentry",
            external_id="123",
            base_commit_sha="abc123",
        )
        bug_info = BugPredictionSpecificInformation(
            organization_id=789,
            organization_slug="my-company",
            should_publish_comments=True,
        )
        config = PrReviewConfig(
            features={PrReviewFeature.BUG_PREDICTION: True},
            trigger=PrReviewTrigger.ON_READY_FOR_REVIEW,
            trigger_user="developer",
            trigger_user_id=55555,
        )
        request = CodegenPrReviewRequest(
            repo=repo,
            pr_id=123,
            bug_prediction_specific_information=bug_info,
            config=config,
        )
        assert request.pr_id == 123
        assert request.bug_prediction_specific_information is not None
        assert request.bug_prediction_specific_information.organization_id == 789
        assert request.config is not None
        assert request.config.is_feature_enabled(PrReviewFeature.BUG_PREDICTION)


class TestCodeReviewTaskRequest:
    """Test complete code review task request wrapper."""

    def test_pr_review_task_request(self) -> None:
        """Complete PR review task request should validate correctly."""
        repo = RepoDefinition(
            provider="github",
            owner="getsentry",
            name="sentry",
            external_id="123456",
            base_commit_sha="def456",
        )
        pr_review_data = CodegenPrReviewRequest(
            repo=repo,
            pr_id=42,
            bug_prediction_specific_information=BugPredictionSpecificInformation(
                organization_id=999,
                organization_slug="test-org",
            ),
            config=PrReviewConfig(
                features={PrReviewFeature.BUG_PREDICTION: True},
                trigger=PrReviewTrigger.ON_COMMAND_PHRASE,
                trigger_comment_id=77777,
                trigger_user="reviewer",
            ),
        )
        task_request = CodeReviewTaskRequest(
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
        repo = RepoDefinition(
            provider="github",
            owner="test",
            name="repo",
            external_id="1",
        )
        pr_review_data = CodegenPrReviewRequest(
            repo=repo,
            pr_id=42,
        )
        task_request = CodeReviewTaskRequest(
            request_type="pr-review",
            external_owner_id="1",
            data=pr_review_data,
        )

        # Test serialization round-trip maintains structure
        serialized = task_request.dict()
        assert serialized["request_type"] == "pr-review"
        assert serialized["data"]["pr_id"] == 42

        # Test deserialization
        restored = CodeReviewTaskRequest.parse_obj(serialized)
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
        validated = CodeReviewTaskRequest.parse_obj(payload)
        assert validated.request_type == "pr-review"
        assert validated.data.pr_id == 42
        assert validated.data.config is not None
        assert validated.data.config.trigger == PrReviewTrigger.ON_READY_FOR_REVIEW
