"""
Tests for base models (RepoDefinition, FileChange, BranchOverride).

Validates core data structures and business logic in base models.
"""

import pytest
from pydantic import ValidationError

from sentry_seer_types.base import BranchOverride, FileChange, FileChangeError, RepoDefinition


class TestBranchOverride:
    """Test branch override logic for event-based routing."""

    def test_matches_when_tag_present(self) -> None:
        """Should match when event contains matching tag."""
        override = BranchOverride(
            tag_name="environment",
            tag_value="production",
            branch_name="prod-hotfix",
        )
        event_tags = [
            {"key": "environment", "value": "production"},
            {"key": "other", "value": "something"},
        ]
        assert override.matches_event_tags(event_tags)

    def test_no_match_when_tag_missing(self) -> None:
        """Should not match when tag key is absent."""
        override = BranchOverride(
            tag_name="environment",
            tag_value="production",
            branch_name="prod-hotfix",
        )
        event_tags = [{"key": "other", "value": "something"}]
        assert not override.matches_event_tags(event_tags)

    def test_no_match_when_value_differs(self) -> None:
        """Should not match when tag key exists but value differs."""
        override = BranchOverride(
            tag_name="environment",
            tag_value="production",
            branch_name="prod-hotfix",
        )
        event_tags = [{"key": "environment", "value": "staging"}]
        assert not override.matches_event_tags(event_tags)

    def test_no_match_empty_tags(self) -> None:
        """Should not match when event has no tags."""
        override = BranchOverride(
            tag_name="environment",
            tag_value="production",
            branch_name="prod-hotfix",
        )
        assert not override.matches_event_tags([])


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
            branch_name="develop",
            branch_overrides=[
                BranchOverride(
                    tag_name="env",
                    tag_value="prod",
                    branch_name="production",
                )
            ],
            instructions="Focus on security issues",
            base_commit_sha="abc123def456",
        )
        assert repo.organization_id == 42
        assert repo.branch_name == "develop"
        assert len(repo.branch_overrides) == 1
        assert repo.instructions == "Focus on security issues"

    def test_invalid_provider_rejected(self) -> None:
        """Invalid provider values should raise validation error."""
        with pytest.raises(ValidationError):
            RepoDefinition(
                provider="invalid_provider",  # type: ignore[arg-type]
                owner="getsentry",
                name="sentry",
                external_id="123",
            )


class TestFileChange:
    """Test file change operations and validation."""

    def test_create_new_file(self) -> None:
        """Create operation should return new content for nonexistent file."""
        change = FileChange(
            change_type="create",
            path="new_file.py",
            new_snippet="print('hello')",
        )
        result = change.apply(None)
        assert result == "print('hello')"

    def test_create_fails_if_file_exists(self) -> None:
        """Create operation should fail if file already exists."""
        change = FileChange(
            change_type="create",
            path="file.py",
            new_snippet="content",
        )
        with pytest.raises(FileChangeError, match="already exists"):
            change.apply("existing content")

    def test_create_requires_new_snippet(self) -> None:
        """Create operation must have new_snippet."""
        change = FileChange(
            change_type="create",
            path="file.py",
        )
        with pytest.raises(FileChangeError, match="must be provided"):
            change.apply(None)

    def test_edit_replaces_content(self) -> None:
        """Edit operation should replace reference with new content."""
        change = FileChange(
            change_type="edit",
            path="file.py",
            reference_snippet="old_code",
            new_snippet="new_code",
        )
        result = change.apply("def foo():\n    old_code\n    return")
        assert result == "def foo():\n    new_code\n    return"

    def test_edit_fails_if_file_missing(self) -> None:
        """Edit operation should fail if file doesn't exist."""
        change = FileChange(
            change_type="edit",
            path="file.py",
            reference_snippet="old",
            new_snippet="new",
        )
        with pytest.raises(FileChangeError, match="doesn't exist"):
            change.apply(None)

    def test_edit_fails_if_reference_not_found(self) -> None:
        """Edit operation should fail if reference snippet not in file."""
        change = FileChange(
            change_type="edit",
            path="file.py",
            reference_snippet="missing_code",
            new_snippet="new_code",
        )
        with pytest.raises(FileChangeError, match="not found"):
            change.apply("def foo(): other_code")

    def test_edit_requires_both_snippets(self) -> None:
        """Edit operation must have both reference and new snippets."""
        change = FileChange(
            change_type="edit",
            path="file.py",
            reference_snippet="old",
        )
        with pytest.raises(FileChangeError, match="must be provided"):
            change.apply("content")

    def test_delete_returns_none(self) -> None:
        """Delete operation should return None."""
        change = FileChange(
            change_type="delete",
            path="file.py",
        )
        result = change.apply("any content")
        assert result is None

    def test_delete_fails_if_file_missing(self) -> None:
        """Delete operation should fail if file doesn't exist."""
        change = FileChange(
            change_type="delete",
            path="file.py",
        )
        with pytest.raises(FileChangeError, match="doesn't exist"):
            change.apply(None)

    def test_edit_replaces_only_first_occurrence(self) -> None:
        """Edit should replace only the first match of reference snippet."""
        change = FileChange(
            change_type="edit",
            path="file.py",
            reference_snippet="duplicate",
            new_snippet="replaced",
        )
        result = change.apply("duplicate and duplicate")
        assert result == "replaced and duplicate"
