"""Tests for coding-grade authority, rerun, and release semantics."""

from uuid import uuid4

import pytest

from optimark_clio import (
    CodingGradeAuthority,
    CodingGradeDecisionSnapshot,
    CodingGradeReleaseState,
    CodingReviewState,
    CodingRerunOutcome,
    CodingRerunPolicy,
    CodingRerunScenario,
)


def test_released_snapshot_requires_matching_authoritative_and_visible_grade() -> None:
    """Verify released grades always point at one authoritative visible record."""
    grade_record_id = uuid4()
    snapshot = CodingGradeDecisionSnapshot(
        submission_id=uuid4(),
        latest_autograde_evaluation_id=uuid4(),
        authoritative_grade_record_id=grade_record_id,
        authoritative_source=CodingGradeAuthority.REVIEW_ADJUSTMENT,
        review_state=CodingReviewState.REVIEWED,
        release_state=CodingGradeReleaseState.RELEASED,
        student_visible_grade_record_id=grade_record_id,
    )

    assert snapshot.release_state is CodingGradeReleaseState.RELEASED
    assert snapshot.student_visible_grade_record_id == grade_record_id


def test_override_state_requires_manual_override_authority() -> None:
    """Verify override review state cannot point at non-override authority."""
    with pytest.raises(ValueError, match="manual_override authority is required"):
        CodingGradeDecisionSnapshot(
            submission_id=uuid4(),
            authoritative_grade_record_id=uuid4(),
            authoritative_source=CodingGradeAuthority.REVIEW_ADJUSTMENT,
            review_state=CodingReviewState.OVERRIDDEN,
            release_state=CodingGradeReleaseState.UNRELEASED,
        )


def test_released_snapshot_rejects_missing_or_mismatched_visible_grade() -> None:
    """Verify release semantics reject partial or inconsistent visibility state."""
    authoritative_grade_record_id = uuid4()

    with pytest.raises(ValueError, match="student_visible_grade_record_id is required"):
        CodingGradeDecisionSnapshot(
            submission_id=uuid4(),
            authoritative_grade_record_id=authoritative_grade_record_id,
            authoritative_source=CodingGradeAuthority.AUTOGRADE,
            review_state=CodingReviewState.REVIEWED,
            release_state=CodingGradeReleaseState.RELEASED,
        )

    with pytest.raises(ValueError, match="must match authoritative_grade_record_id"):
        CodingGradeDecisionSnapshot(
            submission_id=uuid4(),
            authoritative_grade_record_id=authoritative_grade_record_id,
            authoritative_source=CodingGradeAuthority.AUTOGRADE,
            review_state=CodingReviewState.REVIEWED,
            release_state=CodingGradeReleaseState.RELEASED,
            student_visible_grade_record_id=uuid4(),
        )


def test_rerun_policy_captures_non_destructive_post_release_behavior() -> None:
    """Verify the policy contract can encode preserved released grades on rerun."""
    policy = CodingRerunPolicy(
        scenario=CodingRerunScenario.POST_RELEASE,
        outcome=CodingRerunOutcome.PRESERVE_RELEASED_GRADE,
        authoritative_grade_changes_automatically=False,
        student_visible_grade_changes_automatically=False,
        reviewer_action_required=True,
        summary="Keep the released grade visible until staff explicitly reconcile the rerun.",
    )

    assert policy.outcome is CodingRerunOutcome.PRESERVE_RELEASED_GRADE
    assert policy.reviewer_action_required is True
