"""Tests for the coding artifact packaging and handoff schemas."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from optimark_clio import (
    CodingBundleEntry,
    CodingBundleEntryKind,
    CodingExecutionArtifactSet,
    CodingExecutionHandoff,
    CodingHandoffMode,
    CodingRunnerArtifactRef,
    CodingRunnerArtifactRole,
)


def _artifact(role: CodingRunnerArtifactRole, uri: str, name: str) -> CodingRunnerArtifactRef:
    return CodingRunnerArtifactRef(
        role=role,
        reference_uri=uri,
        display_name=name,
    )


def test_reference_manifest_handoff_requires_manifest_artifact() -> None:
    """Verify the reference-only handoff mode carries a manifest artifact."""
    submission_artifact = _artifact(
        CodingRunnerArtifactRole.SUBMISSION,
        "s3://optimark-dev/submissions/submission.zip",
        "submission.zip",
    )
    handoff = CodingExecutionHandoff(
        handoff_id=uuid4(),
        run_id=uuid4(),
        assignment_id=uuid4(),
        assignment_version_id=uuid4(),
        submission_id=uuid4(),
        created_at=datetime(2026, 5, 9, 14, 0, tzinfo=UTC),
        mode=CodingHandoffMode.REFERENCE_MANIFEST,
        artifacts=CodingExecutionArtifactSet(submission_artifact=submission_artifact),
        staging_key_prefix="runs/123/",
        manifest_artifact=_artifact(
            CodingRunnerArtifactRole.RESULT_BUNDLE,
            "s3://optimark-dev/runs/123/handoff-manifest.json",
            "handoff-manifest.json",
        ),
    )

    assert handoff.mode is CodingHandoffMode.REFERENCE_MANIFEST
    assert handoff.manifest_artifact is not None
    assert handoff.prepared_bundle_artifact is None


def test_prepared_bundle_handoff_requires_bundle_and_entries() -> None:
    """Verify prepared bundles declare both the bundle and its entry mapping."""
    submission_artifact = _artifact(
        CodingRunnerArtifactRole.SUBMISSION,
        "s3://optimark-dev/submissions/submission.zip",
        "submission.zip",
    )
    prepared_bundle = _artifact(
        CodingRunnerArtifactRole.RESULT_BUNDLE,
        "s3://optimark-dev/runs/123/workspace.tar.gz",
        "workspace.tar.gz",
    )
    handoff = CodingExecutionHandoff(
        handoff_id=uuid4(),
        run_id=uuid4(),
        assignment_id=uuid4(),
        assignment_version_id=uuid4(),
        submission_id=uuid4(),
        created_at=datetime(2026, 5, 9, 14, 0, tzinfo=UTC),
        mode=CodingHandoffMode.PREPARED_BUNDLE,
        artifacts=CodingExecutionArtifactSet(submission_artifact=submission_artifact),
        staging_key_prefix="runs/123/",
        prepared_bundle_artifact=prepared_bundle,
        bundle_entries=[
            CodingBundleEntry(
                source_artifact=submission_artifact,
                entry_kind=CodingBundleEntryKind.SUBMISSION_ROOT,
                relative_path="workspace/submission/",
            ),
        ],
    )

    assert handoff.prepared_bundle_artifact == prepared_bundle
    assert handoff.bundle_entries[0].relative_path == "workspace/submission/"


def test_handoff_mode_specific_validation_rejects_ambiguous_combinations() -> None:
    """Verify handoff manifests reject incompatible packaging combinations."""
    submission_artifact = _artifact(
        CodingRunnerArtifactRole.SUBMISSION,
        "s3://optimark-dev/submissions/submission.zip",
        "submission.zip",
    )
    common_kwargs = {
        "handoff_id": uuid4(),
        "run_id": uuid4(),
        "assignment_id": uuid4(),
        "assignment_version_id": uuid4(),
        "submission_id": uuid4(),
        "created_at": datetime(2026, 5, 9, 14, 0, tzinfo=UTC),
        "artifacts": CodingExecutionArtifactSet(submission_artifact=submission_artifact),
        "staging_key_prefix": "runs/123/",
    }

    with pytest.raises(ValueError, match="manifest_artifact is required"):
        CodingExecutionHandoff(
            mode=CodingHandoffMode.REFERENCE_MANIFEST,
            **common_kwargs,
        )

    with pytest.raises(ValueError, match="prepared_bundle_artifact is required"):
        CodingExecutionHandoff(
            mode=CodingHandoffMode.PREPARED_BUNDLE,
            **common_kwargs,
        )

    with pytest.raises(ValueError, match="manifest_artifact must be omitted"):
        CodingExecutionHandoff(
            mode=CodingHandoffMode.PREPARED_BUNDLE,
            prepared_bundle_artifact=_artifact(
                CodingRunnerArtifactRole.RESULT_BUNDLE,
                "s3://optimark-dev/runs/123/workspace.tar.gz",
                "workspace.tar.gz",
            ),
            manifest_artifact=_artifact(
                CodingRunnerArtifactRole.RESULT_BUNDLE,
                "s3://optimark-dev/runs/123/handoff-manifest.json",
                "handoff-manifest.json",
            ),
            bundle_entries=[
                CodingBundleEntry(
                    source_artifact=submission_artifact,
                    entry_kind=CodingBundleEntryKind.SUBMISSION_ROOT,
                    relative_path="workspace/submission/",
                ),
            ],
            **common_kwargs,
        )
