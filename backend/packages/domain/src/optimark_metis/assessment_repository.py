"""Repository protocol definitions for assessment persistence."""

from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from optimark_metis.assessment import (
    Assignment,
    AssignmentPublishState,
    AssignmentType,
    AssignmentVersion,
    EvaluationKind,
    EvaluationRecord,
    EvaluationStatus,
    GradeRecord,
    GradeState,
    Submission,
    SubmissionState,
)


class AssessmentRepository(Protocol):
    """Protocol describing persistence operations for assessment data."""

    def add_assignment(
        self,
        *,
        course_id: UUID,
        title: str,
        description: str,
        assignment_type: AssignmentType,
        publish_state: AssignmentPublishState,
    ) -> Assignment:
        """Persist a new assignment."""

    def get_assignment(self, assignment_id: UUID) -> Assignment | None:
        """Fetch an assignment by identifier."""

    def list_course_assignments(self, course_id: UUID) -> Sequence[Assignment]:
        """List assignments for a course."""

    def add_assignment_version(
        self,
        *,
        assignment_id: UUID,
        version_number: int,
        change_summary: str,
        config_snapshot: dict[str, object],
        created_by_user_id: UUID | None,
    ) -> AssignmentVersion:
        """Persist a new assignment version."""

    def get_assignment_version(
        self,
        assignment_version_id: UUID,
    ) -> AssignmentVersion | None:
        """Fetch an assignment version by identifier."""

    def get_assignment_version_by_number(
        self,
        *,
        assignment_id: UUID,
        version_number: int,
    ) -> AssignmentVersion | None:
        """Fetch an assignment version by assignment and version number."""

    def list_assignment_versions(
        self,
        assignment_id: UUID,
    ) -> Sequence[AssignmentVersion]:
        """List versions for an assignment."""

    def add_submission(
        self,
        *,
        assignment_id: UUID,
        assignment_version_id: UUID,
        student_user_id: UUID,
        state: SubmissionState,
        artifact_key: str | None,
        submitted_at: datetime | None,
    ) -> Submission:
        """Persist a new submission."""

    def get_submission(self, submission_id: UUID) -> Submission | None:
        """Fetch a submission by identifier."""

    def list_assignment_submissions(
        self,
        assignment_id: UUID,
        *,
        student_user_id: UUID | None = None,
    ) -> Sequence[Submission]:
        """List submissions for an assignment."""

    def add_evaluation_record(
        self,
        *,
        submission_id: UUID,
        assignment_version_id: UUID,
        evaluation_kind: EvaluationKind,
        status: EvaluationStatus,
        score: Decimal | None,
        max_score: Decimal | None,
        summary: str,
        result_payload: dict[str, object],
    ) -> EvaluationRecord:
        """Persist a new evaluation record."""

    def list_submission_evaluations(
        self,
        submission_id: UUID,
    ) -> Sequence[EvaluationRecord]:
        """List evaluation records for a submission."""

    def add_grade_record(
        self,
        *,
        submission_id: UUID,
        student_user_id: UUID,
        grader_user_id: UUID | None,
        state: GradeState,
        score: Decimal,
        max_score: Decimal,
        feedback: str,
    ) -> GradeRecord:
        """Persist a new grade record."""

    def list_submission_grade_records(
        self,
        submission_id: UUID,
    ) -> Sequence[GradeRecord]:
        """List grade records for a submission."""
