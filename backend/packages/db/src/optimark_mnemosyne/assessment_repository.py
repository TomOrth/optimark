"""SQLAlchemy-backed repository implementations for assessment data."""

from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal
from typing import Mapping
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

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
from optimark_metis.errors import DuplicateAssignmentVersionError
from optimark_mnemosyne._converters import coerce_utc
from optimark_mnemosyne.models import (
    AssignmentModel,
    AssignmentVersionModel,
    EvaluationRecordModel,
    GradeRecordModel,
    SubmissionModel,
)


class SqlAlchemyAssessmentRepository:
    """Persist and query assessment entities through SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with an active SQLAlchemy session.

        Args:
            session: Active ORM session used for persistence operations.
        """
        self._session = session

    def add_assignment(
        self,
        *,
        course_id: UUID,
        title: str,
        description: str,
        assignment_type: AssignmentType,
        publish_state: AssignmentPublishState,
    ) -> Assignment:
        """Insert a new assignment record."""
        model = AssignmentModel(
            course_id=course_id,
            title=title,
            description=description,
            assignment_type=assignment_type,
            publish_state=publish_state,
        )
        self._session.add(model)
        self._session.flush()
        return _assignment_from_model(model)

    def get_assignment(self, assignment_id: UUID) -> Assignment | None:
        """Fetch an assignment by identifier."""
        model = self._session.get(AssignmentModel, assignment_id)
        if model is None:
            return None
        return _assignment_from_model(model)

    def list_course_assignments(self, course_id: UUID) -> Sequence[Assignment]:
        """List assignments for a course."""
        statement = (
            select(AssignmentModel)
            .where(AssignmentModel.course_id == course_id)
            .order_by(AssignmentModel.created_at, AssignmentModel.id)
        )
        return [
            _assignment_from_model(model) for model in self._session.scalars(statement)
        ]

    def update_assignment(
        self,
        *,
        assignment_id: UUID,
        title: str,
        description: str,
        assignment_type: AssignmentType,
        publish_state: AssignmentPublishState,
    ) -> Assignment:
        """Persist updates to an existing assignment record."""
        model = self._session.get(AssignmentModel, assignment_id)
        if model is None:
            raise LookupError(f"assignment {assignment_id} was not found")

        model.title = title
        model.description = description
        model.assignment_type = assignment_type
        model.publish_state = publish_state
        self._session.flush()
        return _assignment_from_model(model)

    def add_assignment_version(
        self,
        *,
        assignment_id: UUID,
        version_number: int,
        change_summary: str,
        config_snapshot: dict[str, object],
        created_by_user_id: UUID | None,
    ) -> AssignmentVersion:
        """Insert a new assignment-version record."""
        model = AssignmentVersionModel(
            assignment_id=assignment_id,
            version_number=version_number,
            change_summary=change_summary,
            config_snapshot=config_snapshot,
            created_by_user_id=created_by_user_id,
        )
        self._session.add(model)
        try:
            self._session.flush()
        except IntegrityError as exc:
            if _is_duplicate_assignment_version_integrity_error(exc):
                raise DuplicateAssignmentVersionError(
                    f"assignment {assignment_id} already has version {version_number}",
                ) from exc
            raise
        return _assignment_version_from_model(model)

    def get_assignment_version(
        self,
        assignment_version_id: UUID,
    ) -> AssignmentVersion | None:
        """Fetch an assignment version by identifier."""
        model = self._session.get(AssignmentVersionModel, assignment_version_id)
        if model is None:
            return None
        return _assignment_version_from_model(model)

    def get_assignment_version_by_number(
        self,
        *,
        assignment_id: UUID,
        version_number: int,
    ) -> AssignmentVersion | None:
        """Fetch an assignment version by assignment and version number."""
        statement = select(AssignmentVersionModel).where(
            AssignmentVersionModel.assignment_id == assignment_id,
            AssignmentVersionModel.version_number == version_number,
        )
        model = self._session.scalar(statement)
        if model is None:
            return None
        return _assignment_version_from_model(model)

    def list_assignment_versions(
        self,
        assignment_id: UUID,
    ) -> Sequence[AssignmentVersion]:
        """List versions for an assignment."""
        statement = (
            select(AssignmentVersionModel)
            .where(AssignmentVersionModel.assignment_id == assignment_id)
            .order_by(
                AssignmentVersionModel.version_number,
                AssignmentVersionModel.id,
            )
        )
        return [
            _assignment_version_from_model(model)
            for model in self._session.scalars(statement)
        ]

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
        """Insert a new submission record."""
        model = SubmissionModel(
            assignment_id=assignment_id,
            assignment_version_id=assignment_version_id,
            student_user_id=student_user_id,
            state=state,
            artifact_key=artifact_key,
            submitted_at=submitted_at,
        )
        self._session.add(model)
        self._session.flush()
        return _submission_from_model(model)

    def get_submission(self, submission_id: UUID) -> Submission | None:
        """Fetch a submission by identifier."""
        model = self._session.get(SubmissionModel, submission_id)
        if model is None:
            return None
        return _submission_from_model(model)

    def list_assignment_submissions(
        self,
        assignment_id: UUID,
        *,
        student_user_id: UUID | None = None,
    ) -> Sequence[Submission]:
        """List submissions for an assignment."""
        statement: Select[tuple[SubmissionModel]] = (
            select(SubmissionModel)
            .where(SubmissionModel.assignment_id == assignment_id)
            .order_by(SubmissionModel.created_at, SubmissionModel.id)
        )
        if student_user_id is not None:
            statement = statement.where(SubmissionModel.student_user_id == student_user_id)
        return [_submission_from_model(model) for model in self._session.scalars(statement)]

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
        """Insert a new evaluation record."""
        model = EvaluationRecordModel(
            submission_id=submission_id,
            assignment_version_id=assignment_version_id,
            evaluation_kind=evaluation_kind,
            status=status,
            score=score,
            max_score=max_score,
            summary=summary,
            result_payload=result_payload,
        )
        self._session.add(model)
        self._session.flush()
        return _evaluation_record_from_model(model)

    def list_submission_evaluations(
        self,
        submission_id: UUID,
    ) -> Sequence[EvaluationRecord]:
        """List evaluation records for a submission."""
        statement = (
            select(EvaluationRecordModel)
            .where(EvaluationRecordModel.submission_id == submission_id)
            .order_by(EvaluationRecordModel.created_at, EvaluationRecordModel.id)
        )
        return [
            _evaluation_record_from_model(model)
            for model in self._session.scalars(statement)
        ]

    def list_evaluations_for_submissions(
        self,
        submission_ids: Sequence[UUID],
    ) -> Mapping[UUID, Sequence[EvaluationRecord]]:
        """List evaluation records for many submissions in a single query."""
        if not submission_ids:
            return {}

        statement = (
            select(EvaluationRecordModel)
            .where(EvaluationRecordModel.submission_id.in_(submission_ids))
            .order_by(
                EvaluationRecordModel.submission_id,
                EvaluationRecordModel.created_at,
                EvaluationRecordModel.id,
            )
        )
        grouped: dict[UUID, list[EvaluationRecord]] = {submission_id: [] for submission_id in submission_ids}
        for model in self._session.scalars(statement):
            grouped.setdefault(model.submission_id, []).append(
                _evaluation_record_from_model(model),
            )
        return grouped

    def update_submission_artifact_key(
        self,
        *,
        submission_id: UUID,
        artifact_key: str,
    ) -> Submission | None:
        """Update the stored artifact key for a submission."""
        model = self._session.get(SubmissionModel, submission_id)
        if model is None:
            return None
        model.artifact_key = artifact_key
        self._session.flush()
        return _submission_from_model(model)

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
        """Insert a new grade record."""
        model = GradeRecordModel(
            submission_id=submission_id,
            student_user_id=student_user_id,
            grader_user_id=grader_user_id,
            state=state,
            score=score,
            max_score=max_score,
            feedback=feedback,
        )
        self._session.add(model)
        self._session.flush()
        return _grade_record_from_model(model)

    def list_submission_grade_records(
        self,
        submission_id: UUID,
    ) -> Sequence[GradeRecord]:
        """List grade records for a submission."""
        statement = (
            select(GradeRecordModel)
            .where(GradeRecordModel.submission_id == submission_id)
            .order_by(GradeRecordModel.created_at, GradeRecordModel.id)
        )
        return [
            _grade_record_from_model(model)
            for model in self._session.scalars(statement)
        ]


def _assignment_from_model(model: AssignmentModel) -> Assignment:
    """Convert an assignment ORM model into a domain assignment."""
    return Assignment(
        id=model.id,
        course_id=model.course_id,
        title=model.title,
        description=model.description,
        assignment_type=model.assignment_type,
        publish_state=model.publish_state,
        created_at=coerce_utc(model.created_at),
        updated_at=coerce_utc(model.updated_at),
    )


def _assignment_version_from_model(
    model: AssignmentVersionModel,
) -> AssignmentVersion:
    """Convert an assignment-version ORM model into a domain entity."""
    return AssignmentVersion(
        id=model.id,
        assignment_id=model.assignment_id,
        version_number=model.version_number,
        change_summary=model.change_summary,
        config_snapshot=dict(model.config_snapshot),
        created_by_user_id=model.created_by_user_id,
        created_at=coerce_utc(model.created_at),
    )


def _submission_from_model(model: SubmissionModel) -> Submission:
    """Convert a submission ORM model into a domain submission."""
    return Submission(
        id=model.id,
        assignment_id=model.assignment_id,
        assignment_version_id=model.assignment_version_id,
        student_user_id=model.student_user_id,
        state=model.state,
        artifact_key=model.artifact_key,
        submitted_at=coerce_utc(model.submitted_at) if model.submitted_at else None,
        created_at=coerce_utc(model.created_at),
        updated_at=coerce_utc(model.updated_at),
    )


def _evaluation_record_from_model(
    model: EvaluationRecordModel,
) -> EvaluationRecord:
    """Convert an evaluation ORM model into a domain evaluation record."""
    return EvaluationRecord(
        id=model.id,
        submission_id=model.submission_id,
        assignment_version_id=model.assignment_version_id,
        evaluation_kind=model.evaluation_kind,
        status=model.status,
        score=model.score,
        max_score=model.max_score,
        summary=model.summary,
        result_payload=dict(model.result_payload),
        created_at=coerce_utc(model.created_at),
        updated_at=coerce_utc(model.updated_at),
    )


def _grade_record_from_model(model: GradeRecordModel) -> GradeRecord:
    """Convert a grade ORM model into a domain grade record."""
    return GradeRecord(
        id=model.id,
        submission_id=model.submission_id,
        student_user_id=model.student_user_id,
        grader_user_id=model.grader_user_id,
        state=model.state,
        score=model.score,
        max_score=model.max_score,
        feedback=model.feedback,
        created_at=coerce_utc(model.created_at),
        updated_at=coerce_utc(model.updated_at),
    )


def _is_duplicate_assignment_version_integrity_error(
    error: IntegrityError,
) -> bool:
    """Return whether an integrity error represents a duplicate version number."""
    message = str(error.orig)
    return (
        "uq_assignment_versions_assignment_number" in message
        or "assignment_versions.assignment_id, assignment_versions.version_number"
        in message
        or "UNIQUE constraint failed: assignment_versions.assignment_id, "
        "assignment_versions.version_number" in message
    )
