from pydantic import BaseModel, Field


class BranchOverride(BaseModel):
    tag_name: str = Field(description="The tag key to match against")
    tag_value: str = Field(description="The tag value to match against")
    branch_name: str = Field(description="The branch to use when this tag matches")


class SeerRepoDefinition(BaseModel):
    organization_id: int | None = None
    integration_id: str | None = None
    provider: str
    owner: str
    name: str
    external_id: str
    branch_name: str | None = Field(
        default=None,
        description="The branch that will be used, otherwise the default branch will be used.",
    )
    branch_overrides: list[BranchOverride] = Field(
        default_factory=list,
        description="List of branch overrides based on event tags.",
    )
    instructions: str | None = Field(
        default=None,
        description="Custom instructions when working in this repo.",
    )
    base_commit_sha: str | None = None
    provider_raw: str | None = None

    @property
    def full_name(self) -> str:
        """Full repository name in 'owner/name' format."""
        return f"{self.owner}/{self.name}"
