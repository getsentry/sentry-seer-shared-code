"""
Tests for Pydantic v2 code review models (RepoDefinition).

Validates core data structures used in code review integration.
"""

import pytest
from pydantic import ValidationError

from sentry_seer_types.v2.code_review import RepoDefinition


class TestRepoDefinition:
    """Test repository definition model and validation."""

    def test_minimal_valid_repo(self) -> None:
        """Minimum required fields should create valid repo."""
        repo = RepoDefinition(
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
        repo = RepoDefinition(
            provider="github",
            owner="getsentry",
            name="sentry",
            external_id="123",
        )
        assert repo.full_name == "getsentry/sentry"

    def test_provider_raw_stored_automatically(self) -> None:
        """Original provider string should be preserved in provider_raw."""
        repo = RepoDefinition(
            provider="github",
            owner="getsentry",
            name="sentry",
            external_id="123",
        )
        assert repo.provider_raw == "github"

    def test_with_optional_fields(self) -> None:
        """All optional fields should be accepted."""
        repo = RepoDefinition(
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

    def test_invalid_provider_rejected(self) -> None:
        """Invalid provider values should raise validation error."""
        with pytest.raises(ValidationError):
            RepoDefinition(
                provider="invalid_provider",  # type: ignore[arg-type]
                owner="getsentry",
                name="sentry",
                external_id="123",
            )
