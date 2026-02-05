"""
Tests for type definitions and enums.

Validates that enums behave correctly and maintain backward compatibility.
Types are shared between v1 and v2, so we test the v1 version.
"""

from sentry_seer_types.v1.code_review import CommentSeverity, PrReviewFeature, PrReviewTrigger


class TestCommentSeverity:
    """Test CommentSeverity enum and severity comparison logic."""

    def test_all_severity_values_exist(self) -> None:
        """Ensure all LOGAF severity levels are defined."""
        assert CommentSeverity.LOW == "low"
        assert CommentSeverity.MEDIUM == "medium"
        assert CommentSeverity.HIGH == "high"
        assert CommentSeverity.CRITICAL == "critical"

    def test_meets_minimum_same_severity(self) -> None:
        """Same severity should meet minimum threshold."""
        assert CommentSeverity.MEDIUM.meets_minimum(CommentSeverity.MEDIUM)
        assert CommentSeverity.CRITICAL.meets_minimum(CommentSeverity.CRITICAL)

    def test_meets_minimum_higher_severity(self) -> None:
        """Higher severity should meet lower minimum threshold."""
        assert CommentSeverity.HIGH.meets_minimum(CommentSeverity.LOW)
        assert CommentSeverity.HIGH.meets_minimum(CommentSeverity.MEDIUM)
        assert CommentSeverity.CRITICAL.meets_minimum(CommentSeverity.HIGH)
        assert CommentSeverity.CRITICAL.meets_minimum(CommentSeverity.LOW)

    def test_meets_minimum_lower_severity(self) -> None:
        """Lower severity should not meet higher minimum threshold."""
        assert not CommentSeverity.LOW.meets_minimum(CommentSeverity.MEDIUM)
        assert not CommentSeverity.LOW.meets_minimum(CommentSeverity.HIGH)
        assert not CommentSeverity.MEDIUM.meets_minimum(CommentSeverity.HIGH)
        assert not CommentSeverity.MEDIUM.meets_minimum(CommentSeverity.CRITICAL)

    def test_severity_ordering_complete(self) -> None:
        """All severity pairs should have defined ordering."""
        severities = [
            CommentSeverity.LOW,
            CommentSeverity.MEDIUM,
            CommentSeverity.HIGH,
            CommentSeverity.CRITICAL,
        ]

        for i, sev1 in enumerate(severities):
            for j, sev2 in enumerate(severities):
                if i >= j:
                    assert sev1.meets_minimum(sev2)
                else:
                    assert not sev1.meets_minimum(sev2)


class TestPrReviewFeature:
    """Test PR review feature flags."""

    def test_vanilla_feature_exists(self) -> None:
        """Basic vanilla review should always be available."""
        assert PrReviewFeature.VANILLA == "vanilla"

    def test_bug_prediction_feature_exists(self) -> None:
        """Bug prediction feature should be defined."""
        assert PrReviewFeature.BUG_PREDICTION == "bug_prediction"

    def test_feature_string_values_match_names(self) -> None:
        """Feature string values should match lowercase names."""
        assert str(PrReviewFeature.VANILLA) == "vanilla"
        assert str(PrReviewFeature.BUG_PREDICTION) == "bug_prediction"


class TestPrReviewTrigger:
    """Test PR review trigger types and backward compatibility."""

    def test_all_triggers_exist(self) -> None:
        """All known trigger types should be defined."""
        assert PrReviewTrigger.UNKNOWN == "unknown"
        assert PrReviewTrigger.ON_COMMAND_PHRASE == "on_command_phrase"
        assert PrReviewTrigger.ON_READY_FOR_REVIEW == "on_ready_for_review"
        assert PrReviewTrigger.ON_NEW_COMMIT == "on_new_commit"

    def test_unknown_trigger_handled_gracefully(self) -> None:
        """Unknown trigger values should map to UNKNOWN instead of raising error."""
        result = PrReviewTrigger("some_future_trigger")  # type: ignore[arg-type]
        assert result == PrReviewTrigger.UNKNOWN

    def test_valid_triggers_parse_correctly(self) -> None:
        """Known trigger strings should parse to correct enum values."""
        assert PrReviewTrigger("on_command_phrase") == PrReviewTrigger.ON_COMMAND_PHRASE
        assert PrReviewTrigger("on_ready_for_review") == PrReviewTrigger.ON_READY_FOR_REVIEW
        assert PrReviewTrigger("on_new_commit") == PrReviewTrigger.ON_NEW_COMMIT
