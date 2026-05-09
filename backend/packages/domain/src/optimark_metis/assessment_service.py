"""Application service layer for the generic assessment domain."""

import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Mapping
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
from optimark_metis.assessment_repository import AssessmentRepository
from optimark_metis.errors import (
    DuplicateAssignmentVersionError,
    EntityNotFoundError,
    InvalidAssessmentDataError,
)
from optimark_metis.service import AcademicService


class AssessmentService:
    """Coordinate assessment domain operations and validation."""

    def __init__(
        self,
        repository: AssessmentRepository,
        academic_service: AcademicService,
    ) -> None:
        """Initialize the service with persistence and academic dependencies.

        Args:
            repository: Repository implementation used for assessment persistence.
            academic_service: Academic service used for course and user validation.
        """
        self._repository = repository
        self._academic_service = academic_service

    def create_assignment(
        self,
        *,
        course_id: UUID,
        title: str,
        description: str,
        assignment_type: AssignmentType,
        publish_state: AssignmentPublishState = AssignmentPublishState.DRAFT,
    ) -> Assignment:
        """Create an assignment for a course."""
        self._academic_service.get_course(course_id)
        return self._repository.add_assignment(
            course_id=course_id,
            title=self._normalize_required(value=title, field_name="title"),
            description=self._normalize_required(
                value=description,
                field_name="description",
            ),
            assignment_type=assignment_type,
            publish_state=publish_state,
        )

    def get_assignment(self, assignment_id: UUID) -> Assignment:
        """Fetch an assignment by identifier."""
        assignment = self._repository.get_assignment(assignment_id)
        if assignment is None:
            raise EntityNotFoundError(f"assignment {assignment_id} was not found")
        return assignment

    def list_course_assignments(self, course_id: UUID) -> list[Assignment]:
        """List assignments for a course."""
        self._academic_service.get_course(course_id)
        return list(self._repository.list_course_assignments(course_id))

    def create_assignment_version(
        self,
        *,
        assignment_id: UUID,
        version_number: int,
        config_snapshot: dict[str, object],
        change_summary: str = "",
        created_by_user_id: UUID | None = None,
    ) -> AssignmentVersion:
        """Create a versioned configuration snapshot for an assignment."""
        self.get_assignment(assignment_id)
        if created_by_user_id is not None:
            self._academic_service.get_user(created_by_user_id)
        if version_number < 1:
            raise InvalidAssessmentDataError("version_number must be at least 1")
        if self._repository.get_assignment_version_by_number(
            assignment_id=assignment_id,
            version_number=version_number,
        ) is not None:
            raise DuplicateAssignmentVersionError(
                f"assignment {assignment_id} already has version {version_number}",
            )
        return self._repository.add_assignment_version(
            assignment_id=assignment_id,
            version_number=version_number,
            change_summary=change_summary.strip(),
            config_snapshot=self._normalize_snapshot(config_snapshot),
            created_by_user_id=created_by_user_id,
        )

    def get_assignment_version(self, assignment_version_id: UUID) -> AssignmentVersion:
        """Fetch an assignment version by identifier."""
        assignment_version = self._repository.get_assignment_version(
            assignment_version_id,
        )
        if assignment_version is None:
            raise EntityNotFoundError(
                f"assignment version {assignment_version_id} was not found",
            )
        return assignment_version

    def list_assignment_versions(self, assignment_id: UUID) -> list[AssignmentVersion]:
        """List assignment versions in version-number order."""
        self.get_assignment(assignment_id)
        return list(self._repository.list_assignment_versions(assignment_id))

    def create_submission(
        self,
        *,
        assignment_id: UUID,
        assignment_version_id: UUID,
        student_user_id: UUID,
        state: SubmissionState = SubmissionState.SUBMITTED,
        artifact_key: str | None = None,
    ) -> Submission:
        """Create a submission for an assignment version."""
        self._academic_service.get_user(student_user_id)
        assignment = self.get_assignment(assignment_id)
        assignment_version = self.get_assignment_version(assignment_version_id)
        if assignment_version.assignment_id != assignment.id:
            raise InvalidAssessmentDataError(
                "assignment_version_id does not belong to assignment_id",
            )
        submitted_at = (
            datetime.now(timezone.utc)
            if state is SubmissionState.SUBMITTED
            else None
        )
        return self._repository.add_submission(
            assignment_id=assignment.id,
            assignment_version_id=assignment_version.id,
            student_user_id=student_user_id,
            state=state,
            artifact_key=self._normalize_optional(artifact_key),
            submitted_at=submitted_at,
        )

    def get_submission(self, submission_id: UUID) -> Submission:
        """Fetch a submission by identifier."""
        submission = self._repository.get_submission(submission_id)
        if submission is None:
            raise EntityNotFoundError(f"submission {submission_id} was not found")
        return submission

    def list_assignment_submissions(
        self,
        assignment_id: UUID,
        *,
        student_user_id: UUID | None = None,
    ) -> list[Submission]:
        """List submissions for an assignment."""
        self.get_assignment(assignment_id)
        if student_user_id is not None:
            self._academic_service.get_user(student_user_id)
        return list(
            self._repository.list_assignment_submissions(
                assignment_id,
                student_user_id=student_user_id,
            ),
        )

    def record_evaluation(
        self,
        *,
        submission_id: UUID,
        assignment_version_id: UUID,
        evaluation_kind: EvaluationKind,
        status: EvaluationStatus,
        score: Decimal | None = None,
        max_score: Decimal | None = None,
        summary: str = "",
        result_payload: dict[str, object] | None = None,
    ) -> EvaluationRecord:
        """Record an evaluation result for a submission."""
        submission = self.get_submission(submission_id)
        assignment_version = self.get_assignment_version(assignment_version_id)
        if submission.assignment_version_id != assignment_version.id:
            raise InvalidAssessmentDataError(
                "assignment_version_id does not match the submission version",
            )
        self._validate_score_pair(score=score, max_score=max_score)
        return self._repository.add_evaluation_record(
            submission_id=submission.id,
            assignment_version_id=assignment_version.id,
            evaluation_kind=evaluation_kind,
            status=status,
            score=score,
            max_score=max_score,
            summary=summary.strip(),
            result_payload=self._normalize_json_object(
                payload=dict(result_payload or {}),
                field_name="result_payload",
            ),
        )

    def list_submission_evaluations(
        self,
        submission_id: UUID,
    ) -> list[EvaluationRecord]:
        """List evaluation records for a submission."""
        self.get_submission(submission_id)
        return list(self._repository.list_submission_evaluations(submission_id))

    def list_evaluations_for_submissions(
        self,
        submission_ids: list[UUID],
    ) -> Mapping[UUID, list[EvaluationRecord]]:
        """List evaluation records for many submissions in one repository call."""
        return {
            submission_id: list(evaluations)
            for submission_id, evaluations in self._repository.list_evaluations_for_submissions(
                submission_ids,
            ).items()
        }

    def update_submission_artifact_key(
        self,
        *,
        submission_id: UUID,
        artifact_key: str,
    ) -> Submission:
        """Persist the final artifact key for a submission."""
        submission = self._repository.update_submission_artifact_key(
            submission_id=submission_id,
            artifact_key=self._normalize_required(
                value=artifact_key,
                field_name="artifact_key",
            ),
        )
        if submission is None:
            raise EntityNotFoundError(f"submission {submission_id} was not found")
        return submission

    def record_grade(
        self,
        *,
        submission_id: UUID,
        student_user_id: UUID,
        grader_user_id: UUID | None = None,
        state: GradeState = GradeState.PROVISIONAL,
        score: Decimal,
        max_score: Decimal,
        feedback: str = "",
    ) -> GradeRecord:
        """Record a grade decision for a submission."""
        submission = self.get_submission(submission_id)
        self._academic_service.get_user(student_user_id)
        if grader_user_id is not None:
            self._academic_service.get_user(grader_user_id)
        if submission.student_user_id != student_user_id:
            raise InvalidAssessmentDataError(
                "student_user_id does not match the submission owner",
            )
        self._validate_score_pair(score=score, max_score=max_score)
        return self._repository.add_grade_record(
            submission_id=submission.id,
            student_user_id=student_user_id,
            grader_user_id=grader_user_id,
            state=state,
            score=score,
            max_score=max_score,
            feedback=feedback.strip(),
        )

    def list_submission_grade_records(self, submission_id: UUID) -> list[GradeRecord]:
        """List grade records for a submission."""
        self.get_submission(submission_id)
        return list(self._repository.list_submission_grade_records(submission_id))

    @staticmethod
    def _normalize_required(*, value: str, field_name: str) -> str:
        """Trim and validate a required string field."""
        normalized_value = value.strip()
        if normalized_value == "":
            raise InvalidAssessmentDataError(f"{field_name} is required")
        return normalized_value

    @staticmethod
    def _normalize_optional(value: str | None) -> str | None:
        """Trim an optional string field."""
        if value is None:
            return None
        normalized_value = value.strip()
        return normalized_value or None

    @staticmethod
    def _normalize_json_object(
        *,
        payload: dict[str, object],
        field_name: str,
    ) -> dict[str, object]:
        """Validate and copy a JSON-serializable object payload.

        Args:
            payload: Raw payload mapping to validate.
            field_name: Field name used in validation errors.

        Returns:
            dict[str, object]: Shallow copy of the validated payload.

        Raises:
            InvalidAssessmentDataError: If the payload is not a JSON object or
                contains non-JSON-serializable nested values.
        """
        if not isinstance(payload, dict):
            raise InvalidAssessmentDataError(f"{field_name} must be a JSON object")
        normalized_payload = dict(payload)
        try:
            json.dumps(normalized_payload)
        except (TypeError, ValueError) as exc:
            raise InvalidAssessmentDataError(
                f"{field_name} must be JSON-serializable",
            ) from exc
        return normalized_payload

    @classmethod
    def _normalize_snapshot(
        cls,
        config_snapshot: dict[str, object],
    ) -> dict[str, object]:
        """Validate and copy a configuration snapshot."""
        return cls._normalize_json_object(
            payload=config_snapshot,
            field_name="config_snapshot",
        )

    @staticmethod
    def _validate_score_pair(
        *,
        score: Decimal | None,
        max_score: Decimal | None,
    ) -> None:
        """Validate a score/max-score pair."""
        if (score is None) != (max_score is None):
            raise InvalidAssessmentDataError(
                "score and max_score must either both be set or both be omitted",
            )
        if score is None or max_score is None:
            return
        if score < 0 or max_score <= 0:
            raise InvalidAssessmentDataError(
                "score must be non-negative and max_score must be positive",
            )
        if score > max_score:
            raise InvalidAssessmentDataError("score cannot exceed max_score")
