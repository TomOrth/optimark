"""Shared contracts for coding-grade authority, reruns, and release semantics."""

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class CodingGradeAuthority(StrEnum):
    """Authoritative source categories for a coding grade decision."""

    AUTOGRADE = "autograde"
    REVIEW_ADJUSTMENT = "review_adjustment"
    MANUAL_OVERRIDE = "manual_override"


class CodingReviewState(StrEnum):
    """Staff-side review state for a coding submission."""

    PENDING_AUTOGRADE = "pending_autograde"
    READY_FOR_REVIEW = "ready_for_review"
    REVIEWED = "reviewed"
    OVERRIDDEN = "overridden"


class CodingGradeReleaseState(StrEnum):
    """Student visibility state for the authoritative grade."""

    UNRELEASED = "unreleased"
    RELEASED = "released"


class CodingRerunScenario(StrEnum):
    """Product scenarios that determine how reruns affect grade authority."""

    PRE_RELEASE_UNREVIEWED = "pre_release_unreviewed"
    PRE_RELEASE_REVIEWED = "pre_release_reviewed"
    POST_RELEASE = "post_release"


class CodingRerunOutcome(StrEnum):
    """Normalized outcomes for how a rerun affects grade semantics."""

    REPLACE_CANDIDATE_ONLY = "replace_candidate_only"
    REQUIRE_REVIEW_RECONCILIATION = "require_review_reconciliation"
    PRESERVE_RELEASED_GRADE = "preserve_released_grade"


class CodingGradeDecisionSnapshot(BaseModel):
    """Snapshot of the current authoritative and student-visible grade semantics."""

    submission_id: UUID
    latest_autograde_evaluation_id: UUID | None = None
    authoritative_grade_record_id: UUID | None = None
    authoritative_source: CodingGradeAuthority | None = None
    review_state: CodingReviewState
    release_state: CodingGradeReleaseState
    student_visible_grade_record_id: UUID | None = None
    rerun_pending_reconciliation: bool = False

    @model_validator(mode="after")
    def validate_consistency(self) -> "CodingGradeDecisionSnapshot":
        """Ensure the snapshot encodes coherent authority and release semantics."""
        if self.authoritative_source is None and self.authoritative_grade_record_id is not None:
            raise ValueError(
                "authoritative_source is required when authoritative_grade_record_id is present",
            )
        if self.authoritative_source is not None and self.authoritative_grade_record_id is None:
            raise ValueError(
                "authoritative_grade_record_id is required when authoritative_source is present",
            )
        if self.review_state is CodingReviewState.OVERRIDDEN and (
            self.authoritative_source is not CodingGradeAuthority.MANUAL_OVERRIDE
        ):
            raise ValueError(
                "manual_override authority is required when review_state is overridden",
            )
        if self.student_visible_grade_record_id is not None and self.authoritative_grade_record_id is None:
            raise ValueError(
                "authoritative_grade_record_id is required when student_visible_grade_record_id is present",
            )
        if self.release_state is CodingGradeReleaseState.RELEASED:
            if self.authoritative_grade_record_id is None:
                raise ValueError(
                    "authoritative_grade_record_id is required when release_state is released",
                )
            if self.student_visible_grade_record_id is None:
                raise ValueError(
                    "student_visible_grade_record_id is required when release_state is released",
                )
            if self.student_visible_grade_record_id != self.authoritative_grade_record_id:
                raise ValueError(
                    "student_visible_grade_record_id must match authoritative_grade_record_id when released",
                )
        if (
            self.release_state is CodingGradeReleaseState.UNRELEASED
            and self.student_visible_grade_record_id is not None
            and self.student_visible_grade_record_id == self.authoritative_grade_record_id
        ):
            raise ValueError(
                "matching student_visible_grade_record_id and authoritative_grade_record_id require release_state to be released",
            )
        return self


class CodingRerunPolicy(BaseModel):
    """Normalized policy decision for how a rerun affects the grade state."""

    scenario: CodingRerunScenario
    outcome: CodingRerunOutcome
    authoritative_grade_changes_automatically: bool
    student_visible_grade_changes_automatically: bool
    reviewer_action_required: bool
    summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_consistency(self) -> "CodingRerunPolicy":
        """Ensure rerun-policy flags stay aligned with the documented scenario semantics."""
        expected = {
            CodingRerunScenario.PRE_RELEASE_UNREVIEWED: (
                CodingRerunOutcome.REPLACE_CANDIDATE_ONLY,
                False,
                False,
                False,
            ),
            CodingRerunScenario.PRE_RELEASE_REVIEWED: (
                CodingRerunOutcome.REQUIRE_REVIEW_RECONCILIATION,
                False,
                False,
                True,
            ),
            CodingRerunScenario.POST_RELEASE: (
                CodingRerunOutcome.PRESERVE_RELEASED_GRADE,
                False,
                False,
                True,
            ),
        }
        (
            expected_outcome,
            expected_authoritative_auto,
            expected_student_auto,
            expected_reviewer_required,
        ) = expected[self.scenario]
        if (
            self.outcome is not expected_outcome
            or self.authoritative_grade_changes_automatically is not expected_authoritative_auto
            or self.student_visible_grade_changes_automatically is not expected_student_auto
            or self.reviewer_action_required is not expected_reviewer_required
        ):
            raise ValueError(
                "rerun policy fields are inconsistent for the selected scenario",
            )
        return self
