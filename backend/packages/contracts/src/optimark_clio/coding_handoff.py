"""Shared contracts for coding artifact packaging and execution handoff."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from optimark_clio.coding_runner import CodingRunnerArtifactRef


class CodingHandoffMode(StrEnum):
    """How the worker presents artifacts to an execution environment."""

    REFERENCE_MANIFEST = "reference_manifest"
    PREPARED_BUNDLE = "prepared_bundle"


class CodingHandoffPackagingVersion(StrEnum):
    """Version marker for the packaging contract itself."""

    V1 = "v1"


class CodingBundleEntryKind(StrEnum):
    """Normalized entry kinds inside a prepared execution bundle."""

    SUBMISSION_ROOT = "submission_root"
    ASSIGNMENT_SUPPORT = "assignment_support"
    GRADER_SUPPORT = "grader_support"
    WORKSPACE_MANIFEST = "workspace_manifest"


class CodingBundleEntry(BaseModel):
    """How one source artifact is materialized inside a prepared bundle."""

    source_artifact: CodingRunnerArtifactRef
    entry_kind: CodingBundleEntryKind
    relative_path: str
    required: bool = True
    extraction_mode: str = "as_provided"


class CodingExecutionArtifactSet(BaseModel):
    """Normalized artifact set required to stage a coding execution run."""

    submission_artifact: CodingRunnerArtifactRef
    assignment_artifacts: list[CodingRunnerArtifactRef] = Field(default_factory=list)
    grader_artifacts: list[CodingRunnerArtifactRef] = Field(default_factory=list)


class CodingExecutionHandoff(BaseModel):
    """Stable handoff manifest from orchestration into execution preparation."""

    handoff_id: UUID
    run_id: UUID
    assignment_id: UUID
    assignment_version_id: UUID
    submission_id: UUID
    created_at: datetime
    packaging_version: CodingHandoffPackagingVersion = CodingHandoffPackagingVersion.V1
    mode: CodingHandoffMode
    artifacts: CodingExecutionArtifactSet
    staging_key_prefix: str
    manifest_artifact: CodingRunnerArtifactRef | None = None
    prepared_bundle_artifact: CodingRunnerArtifactRef | None = None
    bundle_entries: list[CodingBundleEntry] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_mode_specific_fields(self) -> "CodingExecutionHandoff":
        """Ensure required fields are present for the selected handoff mode."""
        if self.mode is CodingHandoffMode.REFERENCE_MANIFEST:
            if self.manifest_artifact is None:
                raise ValueError(
                    "manifest_artifact is required when mode is reference_manifest",
                )
            if self.prepared_bundle_artifact is not None:
                raise ValueError(
                    "prepared_bundle_artifact must be omitted when mode is reference_manifest",
                )
            if self.bundle_entries:
                raise ValueError(
                    "bundle_entries must be empty when mode is reference_manifest",
                )

        if self.mode is CodingHandoffMode.PREPARED_BUNDLE:
            if self.prepared_bundle_artifact is None:
                raise ValueError(
                    "prepared_bundle_artifact is required when mode is prepared_bundle",
                )
            if not self.bundle_entries:
                raise ValueError(
                    "bundle_entries are required when mode is prepared_bundle",
                )

        return self
