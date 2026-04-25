"""Generic assessment domain entities for assignments, submissions, and grades."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID


class AssignmentType(StrEnum):
    """Supported assignment types for the MVP and future expansion."""

    CODING = "coding"
    DOCUMENT = "document"
    QUIZ = "quiz"


class AssignmentPublishState(StrEnum):
    """Lifecycle states for assignment visibility."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class SubmissionState(StrEnum):
    """Lifecycle states for a submission artifact."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    WITHDRAWN = "withdrawn"


class EvaluationKind(StrEnum):
    """Kinds of evaluation records that can be attached to submissions."""

    AUTOMATED = "automated"
    MANUAL = "manual"


class EvaluationStatus(StrEnum):
    """Execution or review status for an evaluation record."""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GradeState(StrEnum):
    """Lifecycle states for a grade record."""

    PROVISIONAL = "provisional"
    RELEASED = "released"
    SUPERSEDED = "superseded"


@dataclass(frozen=True)
class Assignment:
    """Immutable domain representation of an assignment.

    Attributes:
        id: Stable assignment identifier.
        course_id: Related course identifier.
        title: User-facing assignment title.
        description: Assignment instructions or summary text.
        assignment_type: Generic assignment type.
        publish_state: Visibility state for the assignment.
        created_at: Time when the assignment record was created.
        updated_at: Time when the assignment record was last updated.
    """

    id: UUID
    course_id: UUID
    title: str
    description: str
    assignment_type: AssignmentType
    publish_state: AssignmentPublishState
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class AssignmentVersion:
    """Immutable domain representation of a versioned assignment snapshot.

    Attributes:
        id: Stable assignment-version identifier.
        assignment_id: Related assignment identifier.
        version_number: Monotonic version number within the assignment.
        change_summary: Human-readable summary of the version change.
        config_snapshot: Serialized snapshot of the assignment configuration.
        created_by_user_id: Optional user that created the version.
        created_at: Time when the version record was created.
    """

    id: UUID
    assignment_id: UUID
    version_number: int
    change_summary: str
    config_snapshot: dict[str, Any]
    created_by_user_id: UUID | None
    created_at: datetime


@dataclass(frozen=True)
class Submission:
    """Immutable domain representation of a learner submission.

    Attributes:
        id: Stable submission identifier.
        assignment_id: Related assignment identifier.
        assignment_version_id: Version the submission targets.
        student_user_id: Related learner identifier.
        state: Submission lifecycle state.
        artifact_key: Optional artifact storage key.
        submitted_at: Time the submission was formally submitted.
        created_at: Time when the submission record was created.
        updated_at: Time when the submission record was last updated.
    """

    id: UUID
    assignment_id: UUID
    assignment_version_id: UUID
    student_user_id: UUID
    state: SubmissionState
    artifact_key: str | None
    submitted_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class EvaluationRecord:
    """Immutable domain representation of an evaluation attempt.

    Attributes:
        id: Stable evaluation identifier.
        submission_id: Related submission identifier.
        assignment_version_id: Version evaluated by the record.
        evaluation_kind: Whether the evaluation was automated or manual.
        status: Current evaluation status.
        score: Optional earned score.
        max_score: Optional score ceiling.
        summary: Human-readable result summary.
        result_payload: Structured evaluation payload for downstream consumers.
        created_at: Time when the evaluation record was created.
        updated_at: Time when the evaluation record was last updated.
    """

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


@dataclass(frozen=True)
class GradeRecord:
    """Immutable domain representation of a grade decision.

    Attributes:
        id: Stable grade-record identifier.
        submission_id: Related submission identifier.
        student_user_id: Related learner identifier.
        grader_user_id: Optional grader identifier.
        state: Grade lifecycle state.
        score: Earned score for the record.
        max_score: Maximum score for the record.
        feedback: Human-readable feedback text.
        created_at: Time when the grade record was created.
        updated_at: Time when the grade record was last updated.
    """

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
