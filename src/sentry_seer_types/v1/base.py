"""
Base models for code review integration.

This module contains foundational Pydantic models used across the Sentry-Seer
integration, including repository definitions, file changes, and configuration.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field, root_validator

from sentry_seer_types.v1.types import ChangeType, GitProvider


class BranchOverride(BaseModel):
    """
    Branch override based on event tags.

    Allows dynamically selecting a different branch based on specific event
    attributes, useful for routing different types of events to different branches.

    Examples:
        >>> override = BranchOverride(
        ...     tag_name="environment",
        ...     tag_value="production",
        ...     branch_name="prod-hotfix"
        ... )
        >>> event_tags = [{"key": "environment", "value": "production"}]
        >>> override.matches_event_tags(event_tags)
        True
    """

    tag_name: str = Field(description="The tag key to match against")
    tag_value: str = Field(description="The tag value to match against")
    branch_name: str = Field(description="The branch to use when this tag matches")

    def matches_event_tags(self, event_tags: list[dict[str, str | None]]) -> bool:
        """
        Check if this override matches any of the provided event tags.

        Args:
            event_tags: List of event tags, each containing 'key' and 'value'

        Returns:
            True if any tag matches both tag_name and tag_value
        """
        return any(
            tag.get("key") == self.tag_name and tag.get("value") == self.tag_value
            for tag in event_tags
        )


class RepoDefinition(BaseModel):
    """
    Complete definition of a repository for code review operations.

    Contains all necessary information to identify and access a repository,
    including authentication details, branch configuration, and custom instructions.
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
    branch_name: Optional[str] = Field(
        default=None,
        description="Specific branch for code review operations. If not set, uses default branch.",
    )
    branch_overrides: list[BranchOverride] = Field(
        default_factory=list,
        description="Dynamic branch selection based on event tags",
    )
    instructions: Optional[str] = Field(
        default=None,
        description="Custom instructions for AI agents when analyzing this repository",
    )
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
        """
        Get the full repository name in 'owner/name' format.

        Returns:
            Repository name in the format "owner/name"

        Examples:
            >>> repo = RepoDefinition(
            ...     provider="github",
            ...     owner="getsentry",
            ...     name="sentry",
            ...     external_id="123"
            ... )
            >>> repo.full_name
            'getsentry/sentry'
        """
        return f"{self.owner}/{self.name}"

    @root_validator(pre=True)
    def store_provider_raw(cls, values: Any) -> Any:
        """
        Store the original provider value before Pydantic validates it.

        Preserves the raw provider string for cases where the original format
        matters (e.g., logging, debugging).
        """
        if isinstance(values, dict) and "provider" in values and "provider_raw" not in values:
            values["provider_raw"] = values["provider"]
        return values


class FileChangeError(Exception):
    """Raised when a file change operation fails or is invalid."""

    pass


class FileChange(BaseModel):
    """
    Represents a single file modification in a code review or autofix operation.

    FileChange describes an operation to create, edit, or delete a file, including
    the actual content changes and metadata like commit messages.
    """

    change_type: ChangeType = Field(description="Type of file operation")
    path: str = Field(description="File path relative to repository root")
    reference_snippet: Optional[str] = Field(
        default=None,
        description="Code snippet to find and replace (for edit operations)",
    )
    new_snippet: Optional[str] = Field(
        default=None,
        description="New code content (for create/edit operations)",
    )
    description: Optional[str] = Field(
        default=None,
        description="Human-readable description of the change",
    )
    commit_message: Optional[str] = Field(
        default=None,
        description="Git commit message for this change",
    )
    tool_call_id: Optional[str] = Field(
        default=None,
        description="ID of the AI tool call that generated this change",
    )

    def apply(self, file_contents: str | None) -> str | None:
        """
        Apply this change to existing file contents.

        Args:
            file_contents: Current file contents, or None if file doesn't exist

        Returns:
            New file contents after applying the change, or None if deleting

        Raises:
            FileChangeError: If the change cannot be applied (e.g., creating
                an existing file, editing without reference snippet)

        Examples:
            >>> # Create a new file
            >>> change = FileChange(
            ...     change_type="create",
            ...     path="new_file.py",
            ...     new_snippet="print('hello')"
            ... )
            >>> change.apply(None)
            "print('hello')"

            >>> # Edit existing file
            >>> change = FileChange(
            ...     change_type="edit",
            ...     path="file.py",
            ...     reference_snippet="old_code",
            ...     new_snippet="new_code"
            ... )
            >>> change.apply("def foo(): old_code")
            'def foo(): new_code'

            >>> # Delete a file
            >>> change = FileChange(change_type="delete", path="file.py")
            >>> change.apply("any content")
            None
        """
        if self.change_type == "create":
            if file_contents is not None and file_contents != "":
                raise FileChangeError("Cannot create a file that already exists.")
            if self.new_snippet is None:
                raise FileChangeError("New snippet must be provided for creating a file.")
            return self.new_snippet

        if self.change_type == "edit":
            if file_contents is None:
                raise FileChangeError("Cannot edit a file that doesn't exist.")
            if self.reference_snippet is None:
                raise FileChangeError("Reference snippet must be provided for editing a file.")
            if self.new_snippet is None:
                raise FileChangeError("New snippet must be provided for editing a file.")
            if self.reference_snippet not in file_contents:
                raise FileChangeError(
                    f"Reference snippet not found in file contents.\n"
                    f"Looking for: {self.reference_snippet[:100]}..."
                )
            return file_contents.replace(self.reference_snippet, self.new_snippet, 1)

        if self.change_type == "delete":
            if file_contents is None:
                raise FileChangeError("Cannot delete a file that doesn't exist.")
            return None

        raise FileChangeError(f"Unknown change type: {self.change_type}")
