"""Pydantic contracts for the generic assessment domain."""

import json
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from optimark_clio.academic import CourseSummary
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


class SubmissionLifecycleStatus(StrEnum):
    """Student-facing lifecycle states for a submission."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WITHDRAWN = "withdrawn"


class CreateAssignmentInput(BaseModel):
    """Input payload for creating an assignment."""

    course_id: UUID
    title: str
    description: str
    assignment_type: AssignmentType
    publish_state: AssignmentPublishState = AssignmentPublishState.DRAFT


class AssignmentSummary(BaseModel):
    """Summary representation of an assignment."""

    id: UUID
    course_id: UUID
    title: str
    assignment_type: AssignmentType
    publish_state: AssignmentPublishState

    @classmethod
    def from_domain(cls, assignment: Assignment) -> "AssignmentSummary":
        """Build a summary contract from a domain assignment."""
        return cls(
            id=assignment.id,
            course_id=assignment.course_id,
            title=assignment.title,
            assignment_type=assignment.assignment_type,
            publish_state=assignment.publish_state,
        )


class AssignmentDetail(AssignmentSummary):
    """Detailed representation of an assignment including timestamps."""

    description: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, assignment: Assignment) -> "AssignmentDetail":
        """Build a detail contract from a domain assignment."""
        return cls(
            id=assignment.id,
            course_id=assignment.course_id,
            title=assignment.title,
            description=assignment.description,
            assignment_type=assignment.assignment_type,
            publish_state=assignment.publish_state,
            created_at=assignment.created_at,
            updated_at=assignment.updated_at,
        )


class CreateAssignmentVersionInput(BaseModel):
    """Input payload for creating an assignment version."""

    assignment_id: UUID
    version_number: int
    change_summary: str = ""
    config_snapshot: dict[str, Any]
    created_by_user_id: UUID | None = None

    @field_validator("config_snapshot")
    @classmethod
    def validate_config_snapshot(
        cls,
        value: dict[str, Any],
    ) -> dict[str, Any]:
        """Ensure config snapshots are JSON-serializable objects.

        Args:
            value: Candidate configuration snapshot.

        Returns:
            dict[str, Any]: Validated configuration snapshot.

        Raises:
            ValueError: If the payload is not JSON-serializable.
        """
        _ensure_json_serializable(value, field_name="config_snapshot")
        return value


class AssignmentVersionRecord(BaseModel):
    """Serialized assignment-version record."""

    id: UUID
    assignment_id: UUID
    version_number: int
    change_summary: str
    config_snapshot: dict[str, Any]
    created_by_user_id: UUID | None
    created_at: datetime

    @classmethod
    def from_domain(
        cls,
        assignment_version: AssignmentVersion,
    ) -> "AssignmentVersionRecord":
        """Build a version contract from a domain assignment version."""
        return cls(
            id=assignment_version.id,
            assignment_id=assignment_version.assignment_id,
            version_number=assignment_version.version_number,
            change_summary=assignment_version.change_summary,
            config_snapshot=assignment_version.config_snapshot,
            created_by_user_id=assignment_version.created_by_user_id,
            created_at=assignment_version.created_at,
        )


class CreateSubmissionInput(BaseModel):
    """Input payload for creating a submission."""

    assignment_id: UUID
    assignment_version_id: UUID
    student_user_id: UUID
    state: SubmissionState = SubmissionState.SUBMITTED
    artifact_key: str | None = None


class SubmissionRecord(BaseModel):
    """Serialized submission record."""

    id: UUID
    assignment_id: UUID
    assignment_version_id: UUID
    student_user_id: UUID
    state: SubmissionState
    artifact_key: str | None
    submitted_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, submission: Submission) -> "SubmissionRecord":
        """Build a submission contract from a domain submission."""
        return cls(
            id=submission.id,
            assignment_id=submission.assignment_id,
            assignment_version_id=submission.assignment_version_id,
            student_user_id=submission.student_user_id,
            state=submission.state,
            artifact_key=submission.artifact_key,
            submitted_at=submission.submitted_at,
            created_at=submission.created_at,
            updated_at=submission.updated_at,
        )


class StudentSubmissionRecord(SubmissionRecord):
    """Student-facing submission record with derived lifecycle status."""

    lifecycle_status: SubmissionLifecycleStatus
    artifact_name: str | None = None

    @classmethod
    def from_domain(
        cls,
        submission: Submission,
        *,
        evaluations: list[EvaluationRecord] | None = None,
        artifact_name: str | None = None,
    ) -> "StudentSubmissionRecord":
        """Build a student submission contract from domain records."""
        return cls(
            id=submission.id,
            assignment_id=submission.assignment_id,
            assignment_version_id=submission.assignment_version_id,
            student_user_id=submission.student_user_id,
            state=submission.state,
            artifact_key=submission.artifact_key,
            artifact_name=artifact_name,
            lifecycle_status=_derive_submission_lifecycle_status(
                submission=submission,
                evaluations=evaluations or [],
            ),
            submitted_at=submission.submitted_at,
            created_at=submission.created_at,
            updated_at=submission.updated_at,
        )


class StudentAssignmentSummary(BaseModel):
    """Student-facing coding assignment summary."""

    course: CourseSummary
    assignment: AssignmentDetail
    active_assignment_version_id: UUID | None
    latest_submission: StudentSubmissionRecord | None = None


class StudentSubmissionWorkspace(BaseModel):
    """Student-facing submission workspace payload."""

    course: CourseSummary
    assignment: AssignmentDetail
    active_assignment_version_id: UUID | None
    submissions: list[StudentSubmissionRecord]


class RecordEvaluationInput(BaseModel):
    """Input payload for recording an evaluation result."""

    submission_id: UUID
    assignment_version_id: UUID
    evaluation_kind: EvaluationKind
    status: EvaluationStatus
    score: Decimal | None = None
    max_score: Decimal | None = None
    summary: str = ""
    result_payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("result_payload")
    @classmethod
    def validate_result_payload(
        cls,
        value: dict[str, Any],
    ) -> dict[str, Any]:
        """Ensure evaluation payloads are JSON-serializable objects.

        Args:
            value: Candidate result payload.

        Returns:
            dict[str, Any]: Validated result payload.

        Raises:
            ValueError: If the payload is not JSON-serializable.
        """
        _ensure_json_serializable(value, field_name="result_payload")
        return value


class EvaluationRecordPayload(BaseModel):
    """Serialized evaluation record payload."""

    id: UUID
    submission_id: UUID
    assignment_version_id: UUID
    evaluation_kind: EvaluationKind
    status: EvaluationStatus
    score: Decimal | None
    max_score: Decimal | None
    summary: str
    result_payload: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(
        cls,
        evaluation: EvaluationRecord,
    ) -> "EvaluationRecordPayload":
        """Build an evaluation contract from a domain evaluation record."""
        return cls(
            id=evaluation.id,
            submission_id=evaluation.submission_id,
            assignment_version_id=evaluation.assignment_version_id,
            evaluation_kind=evaluation.evaluation_kind,
            status=evaluation.status,
            score=evaluation.score,
            max_score=evaluation.max_score,
            summary=evaluation.summary,
            result_payload=evaluation.result_payload,
            created_at=evaluation.created_at,
            updated_at=evaluation.updated_at,
        )


class RecordGradeInput(BaseModel):
    """Input payload for recording a grade result."""

    submission_id: UUID
    student_user_id: UUID
    grader_user_id: UUID | None = None
    state: GradeState = GradeState.PROVISIONAL
    score: Decimal
    max_score: Decimal
    feedback: str = ""


class GradeRecordPayload(BaseModel):
    """Serialized grade record payload."""

    id: UUID
    submission_id: UUID
    student_user_id: UUID
    grader_user_id: UUID | None
    state: GradeState
    score: Decimal
    max_score: Decimal
    feedback: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, grade_record: GradeRecord) -> "GradeRecordPayload":
        """Build a grade contract from a domain grade record."""
        return cls(
            id=grade_record.id,
            submission_id=grade_record.submission_id,
            student_user_id=grade_record.student_user_id,
            grader_user_id=grade_record.grader_user_id,
            state=grade_record.state,
            score=grade_record.score,
            max_score=grade_record.max_score,
            feedback=grade_record.feedback,
            created_at=grade_record.created_at,
            updated_at=grade_record.updated_at,
        )


def _ensure_json_serializable(value: dict[str, Any], *, field_name: str) -> None:
    """Validate that a mapping payload can be encoded as JSON.

    Args:
        value: Payload to validate.
        field_name: Field name used in validation errors.

    Raises:
        ValueError: If the payload cannot be encoded as JSON.
    """
    try:
        json.dumps(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be JSON-serializable") from exc


def _derive_submission_lifecycle_status(
    *,
    submission: Submission,
    evaluations: list[EvaluationRecord],
) -> SubmissionLifecycleStatus:
    """Map domain submission/evaluation state to a student-facing status."""
    if submission.state is SubmissionState.DRAFT:
        return SubmissionLifecycleStatus.DRAFT
    if submission.state is SubmissionState.WITHDRAWN:
        return SubmissionLifecycleStatus.WITHDRAWN

    latest_evaluation = evaluations[-1] if evaluations else None
    if latest_evaluation is None:
        return SubmissionLifecycleStatus.SUBMITTED

    match latest_evaluation.status:
        case EvaluationStatus.QUEUED:
            return SubmissionLifecycleStatus.QUEUED
        case EvaluationStatus.RUNNING:
            return SubmissionLifecycleStatus.RUNNING
        case EvaluationStatus.SUCCEEDED:
            return SubmissionLifecycleStatus.COMPLETED
        case EvaluationStatus.FAILED | EvaluationStatus.CANCELLED:
            return SubmissionLifecycleStatus.FAILED

    return SubmissionLifecycleStatus.SUBMITTED
