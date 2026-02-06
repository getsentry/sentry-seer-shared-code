"""
Tests for Pydantic v1 code review models (SeerRepoDefinition).

Validates core data structures used in code review integration.
"""

from sentry_seer_types.v1.code_review import SeerRepoDefinition


class TestSeerRepoDefinition:
    """Test repository definition model and validation."""

    def test_minimal_valid_repo(self) -> None:
        """Minimum required fields should create valid repo."""
        repo = SeerRepoDefinition(
            provider="github",
            owner="getsentry",
            name="sentry",
            external_id="123456",
        )
        assert repo.provider == "github"
        assert repo.owner == "getsentry"
        assert repo.name == "sentry"
        assert repo.external_id == "123456"

    def test_full_name_property(self) -> None:
        """full_name should return 'owner/name' format."""
        repo = SeerRepoDefinition(
            provider="github",
            owner="getsentry",
            name="sentry",
            external_id="123",
        )
        assert repo.full_name == "getsentry/sentry"

    def test_provider_raw_can_be_set(self) -> None:
        """provider_raw can be set explicitly when provided."""
        repo = SeerRepoDefinition(
            provider="github",
            owner="getsentry",
            name="sentry",
            external_id="123",
            provider_raw="github",
        )
        assert repo.provider_raw == "github"

    def test_with_optional_fields(self) -> None:
        """All optional fields should be accepted."""
        repo = SeerRepoDefinition(
            organization_id=42,
            integration_id="int-123",
            provider="github_enterprise",
            owner="my-org",
            name="my-repo",
            external_id="456",
            base_commit_sha="abc123def456",
        )
        assert repo.organization_id == 42
        assert repo.base_commit_sha == "abc123def456"
