"""Student submission API routes backed by S3-compatible artifact storage."""

from collections.abc import Sequence
from contextlib import suppress
import logging
from pathlib import PurePosixPath
import re
from tempfile import SpooledTemporaryFile
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from optimark_athena.artifact_store import ArtifactStore
from optimark_athena.config import SubmissionSettings
from optimark_athena.dependencies import (
    get_academic_service,
    get_artifact_store,
    get_assessment_service,
    get_db_session,
    get_submission_settings,
    require_course_capability,
    require_authenticated_session,
)
from optimark_clio import (
    AssignmentDetail,
    CourseSummary,
    StudentAssignmentSummary,
    StudentSubmissionRecord,
    StudentSubmissionWorkspace,
)
from optimark_metis import (
    AcademicService,
    AssessmentService,
    AssignmentPublishState,
    AssignmentType,
    AuthenticatedSession,
    CourseCapability,
    CourseRole,
    DuplicateAssignmentVersionError,
    EntityNotFoundError,
    EvaluationKind,
    EvaluationRecord,
    EvaluationStatus,
    InvalidAssessmentDataError,
    Submission,
    SubmissionState,
)


router = APIRouter(prefix="/api/v1", tags=["submissions"])

_FILENAME_SANITIZER = re.compile(r"[^A-Za-z0-9._-]+")
_STREAM_BUFFER_BYTES = 1024 * 1024

logger = logging.getLogger(__name__)


@router.get(
    "/student/assignments",
    response_model=list[StudentAssignmentSummary],
)
def list_student_assignments(
    authentication: Annotated[
        AuthenticatedSession,
        Depends(require_authenticated_session),
    ],
    academic_service: Annotated[AcademicService, Depends(get_academic_service)],
    assessment_service: Annotated[AssessmentService, Depends(get_assessment_service)],
) -> list[StudentAssignmentSummary]:
    """List published coding assignments available to the current student."""
    courses = academic_service.list_courses_for_user(
        authentication.user.id,
        role_filter=CourseRole.STUDENT,
    )
    assignment_summaries: list[StudentAssignmentSummary] = []

    for course in courses:
        assignments = assessment_service.list_course_assignments(course.id)
        for assignment in assignments:
            if assignment.assignment_type is not AssignmentType.CODING:
                continue
            if assignment.publish_state is not AssignmentPublishState.PUBLISHED:
                continue

            active_version = _get_active_assignment_version(
                assessment_service=assessment_service,
                assignment_id=assignment.id,
            )
            submissions = assessment_service.list_assignment_submissions(
                assignment.id,
                student_user_id=authentication.user.id,
            )
            latest_submission = _build_latest_submission_record(
                assessment_service=assessment_service,
                submissions=submissions,
            )
            assignment_summaries.append(
                StudentAssignmentSummary(
                    course=CourseSummary.from_domain(course),
                    assignment=AssignmentDetail.from_domain(assignment),
                    active_assignment_version_id=(
                        active_version.id if active_version is not None else None
                    ),
                    latest_submission=latest_submission,
                ),
            )

    assignment_summaries.sort(
        key=lambda item: (
            item.course.term.lower(),
            item.course.course_code.lower(),
            item.assignment.title.lower(),
        ),
    )
    return assignment_summaries


@router.get(
    "/courses/{course_id}/assignments/{assignment_id}/submission-workspace",
    response_model=StudentSubmissionWorkspace,
)
def get_submission_workspace(
    course_id: UUID,
    assignment_id: UUID,
    authentication: Annotated[
        AuthenticatedSession,
        Depends(require_course_capability(CourseCapability.SUBMIT_WORK)),
    ],
    academic_service: Annotated[AcademicService, Depends(get_academic_service)],
    assessment_service: Annotated[AssessmentService, Depends(get_assessment_service)],
) -> StudentSubmissionWorkspace:
    """Return the student submission workspace for a published coding assignment."""
    course = academic_service.get_course(course_id)
    assignment = _require_student_submittable_assignment(
        assessment_service=assessment_service,
        assignment_id=assignment_id,
        course_id=course_id,
    )
    active_version = _get_active_assignment_version(
        assessment_service=assessment_service,
        assignment_id=assignment.id,
    )
    submissions = assessment_service.list_assignment_submissions(
        assignment.id,
        student_user_id=authentication.user.id,
    )

    return StudentSubmissionWorkspace(
        course=CourseSummary.from_domain(course),
        assignment=AssignmentDetail.from_domain(assignment),
        active_assignment_version_id=active_version.id if active_version else None,
        submissions=_build_student_submission_records(
            assessment_service=assessment_service,
            submissions=submissions,
        ),
    )


@router.post(
    "/courses/{course_id}/assignments/{assignment_id}/submissions",
    response_model=StudentSubmissionRecord,
    status_code=status.HTTP_201_CREATED,
)
async def create_submission(
    request: Request,
    course_id: UUID,
    assignment_id: UUID,
    filename: Annotated[str, Query(min_length=1, max_length=255)],
    state: Annotated[Literal["draft", "submitted"], Query()] = "submitted",
    authentication: Annotated[
        AuthenticatedSession,
        Depends(require_course_capability(CourseCapability.SUBMIT_WORK)),
    ] = None,
    assessment_service: Annotated[AssessmentService, Depends(get_assessment_service)] = None,
    db_session: Annotated[Session, Depends(get_db_session)] = None,
    artifact_store: Annotated[ArtifactStore, Depends(get_artifact_store)] = None,
    submission_settings: Annotated[
        SubmissionSettings,
        Depends(get_submission_settings),
    ] = None,
) -> StudentSubmissionRecord:
    """Store an uploaded artifact and create a submission record for the student."""
    assignment = _require_student_submittable_assignment(
        assessment_service=assessment_service,
        assignment_id=assignment_id,
        course_id=course_id,
    )
    active_version = _ensure_active_assignment_version(
        assessment_service=assessment_service,
        assignment_id=assignment.id,
    )
    normalized_filename = _normalize_filename(filename)
    _validate_content_length(
        request=request,
        max_upload_bytes=submission_settings.max_upload_bytes,
    )

    submission_state = (
        SubmissionState.DRAFT if state == "draft" else SubmissionState.SUBMITTED
    )
    uploaded_artifact_key: str | None = None
    artifact_file = await _spool_request_body(
        request=request,
        max_upload_bytes=submission_settings.max_upload_bytes,
    )

    try:
        submission = assessment_service.create_submission(
            assignment_id=assignment.id,
            assignment_version_id=active_version.id,
            student_user_id=authentication.user.id,
            state=submission_state,
            artifact_key=None,
        )

        uploaded_artifact_key = await run_in_threadpool(
            artifact_store.put_artifact,
            key=_build_artifact_key(
                course_id=course_id,
                assignment_id=assignment.id,
                student_user_id=authentication.user.id,
                submission_id=submission.id,
                filename=normalized_filename,
            ),
            fileobj=artifact_file,
            content_type=request.headers.get(
                "content-type",
                "application/octet-stream",
            ),
            metadata={
                "course-id": str(course_id),
                "assignment-id": str(assignment.id),
                "student-user-id": str(authentication.user.id),
                "submission-id": str(submission.id),
                "filename": normalized_filename,
            },
        )
        submission = assessment_service.update_submission_artifact_key(
            submission_id=submission.id,
            artifact_key=uploaded_artifact_key,
        )

        evaluations: list[EvaluationRecord] = []
        if submission_state is SubmissionState.SUBMITTED:
            evaluations.append(
                assessment_service.record_evaluation(
                    submission_id=submission.id,
                    assignment_version_id=active_version.id,
                    evaluation_kind=EvaluationKind.AUTOMATED,
                    status=EvaluationStatus.QUEUED,
                    summary="Queued for autograde orchestration.",
                    result_payload={},
                ),
            )

        db_session.commit()
        return StudentSubmissionRecord.from_domain(
            submission,
            evaluations=evaluations,
            artifact_name=normalized_filename,
        )
    except Exception:
        db_session.rollback()
        if uploaded_artifact_key is not None:
            with suppress(Exception):
                await run_in_threadpool(
                    artifact_store.delete_artifact,
                    key=uploaded_artifact_key,
                )
            logger.exception(
                "Failed to create submission after uploading artifact",
                extra={
                    "assignment_id": str(assignment.id),
                    "course_id": str(course_id),
                },
            )
        raise
    finally:
        artifact_file.close()


def _require_student_submittable_assignment(
    *,
    assessment_service: AssessmentService,
    assignment_id: UUID,
    course_id: UUID,
):
    """Fetch and validate a student-submittable coding assignment."""
    try:
        assignment = assessment_service.get_assignment(assignment_id)
    except EntityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if assignment.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"assignment {assignment_id} was not found in course {course_id}",
        )
    if assignment.assignment_type is not AssignmentType.CODING:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="only coding assignments support student submissions",
        )
    if assignment.publish_state is not AssignmentPublishState.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="assignment is not published for student submission",
        )
    return assignment


def _get_active_assignment_version(
    *,
    assessment_service: AssessmentService,
    assignment_id: UUID,
):
    """Return the latest assignment version without creating new records."""
    versions = assessment_service.list_assignment_versions(assignment_id)
    return versions[-1] if versions else None


def _ensure_active_assignment_version(
    *,
    assessment_service: AssessmentService,
    assignment_id: UUID,
):
    """Return the latest assignment version, creating the initial one if needed."""
    existing_version = _get_active_assignment_version(
        assessment_service=assessment_service,
        assignment_id=assignment_id,
    )
    if existing_version is not None:
        return existing_version

    assignment = assessment_service.get_assignment(assignment_id)
    try:
        return assessment_service.create_assignment_version(
            assignment_id=assignment.id,
            version_number=1,
            change_summary="Initial submission snapshot",
            config_snapshot={
                "title": assignment.title,
                "description": assignment.description,
                "assignment_type": assignment.assignment_type.value,
                "publish_state": assignment.publish_state.value,
            },
            created_by_user_id=None,
        )
    except DuplicateAssignmentVersionError:
        version = assessment_service.list_assignment_versions(assignment.id)
        if version:
            return version[-1]
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="assignment version creation conflicted; retry the submission",
        ) from None
    except InvalidAssessmentDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


def _build_student_submission_records(
    *,
    assessment_service: AssessmentService,
    submissions: Sequence[Submission],
) -> list[StudentSubmissionRecord]:
    """Serialize submissions with their derived student-facing status."""
    evaluation_map = assessment_service.list_evaluations_for_submissions(
        [submission.id for submission in submissions],
    )
    serialized = [
        StudentSubmissionRecord.from_domain(
            submission,
            evaluations=list(evaluation_map.get(submission.id, [])),
            artifact_name=_artifact_name_from_key(submission.artifact_key),
        )
        for submission in submissions
    ]
    serialized.sort(key=lambda submission: submission.created_at, reverse=True)
    return serialized


def _build_latest_submission_record(
    *,
    assessment_service: AssessmentService,
    submissions: Sequence[Submission],
) -> StudentSubmissionRecord | None:
    """Serialize the latest submission in a collection."""
    if not submissions:
        return None
    latest_submission = max(submissions, key=lambda submission: submission.created_at)
    evaluation_map = assessment_service.list_evaluations_for_submissions(
        [latest_submission.id],
    )
    return StudentSubmissionRecord.from_domain(
        latest_submission,
        evaluations=list(evaluation_map.get(latest_submission.id, [])),
        artifact_name=_artifact_name_from_key(latest_submission.artifact_key),
    )


def _normalize_filename(filename: str) -> str:
    """Normalize a user-supplied filename into a safe object-key suffix."""
    candidate = PurePosixPath(filename.strip()).name
    if candidate == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="filename is required",
        )

    sanitized = _FILENAME_SANITIZER.sub("-", candidate).strip(".-")
    if sanitized == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="filename must contain at least one valid character",
        )
    return sanitized[:120]


def _build_artifact_key(
    *,
    course_id: UUID,
    assignment_id: UUID,
    student_user_id: UUID,
    submission_id: UUID,
    filename: str,
) -> str:
    """Build a unique artifact key rooted under the submission prefix."""
    return (
        f"{course_id}/{assignment_id}/{student_user_id}/"
        f"{submission_id}__{filename}"
    )


def _artifact_name_from_key(artifact_key: str | None) -> str | None:
    """Recover the original filename suffix from an artifact key."""
    if artifact_key is None:
        return None
    tail = PurePosixPath(artifact_key).name
    if "__" not in tail:
        return tail
    return tail.split("__", 1)[1] or tail


def _validate_content_length(*, request: Request, max_upload_bytes: int) -> None:
    """Reject requests that advertise an invalid or oversized body."""
    raw_content_length = request.headers.get("content-length")
    if raw_content_length is None:
        return

    try:
        content_length = int(raw_content_length)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="content-length must be an integer",
        ) from exc

    if content_length < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="content-length must be non-negative",
        )
    if content_length == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="submission artifact body is required",
        )
    if content_length > max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=(
                f"submission artifact exceeds the {max_upload_bytes}-byte upload limit"
            ),
        )


async def _spool_request_body(
    *,
    request: Request,
    max_upload_bytes: int,
) -> SpooledTemporaryFile[bytes]:
    """Stream the request body into a temporary file while enforcing size limits."""
    temp_file: SpooledTemporaryFile[bytes] = SpooledTemporaryFile(
        max_size=_STREAM_BUFFER_BYTES,
        mode="w+b",
    )
    total_bytes = 0

    try:
        async for chunk in request.stream():
            if not chunk:
                continue
            total_bytes += len(chunk)
            if total_bytes > max_upload_bytes:
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail=(
                        f"submission artifact exceeds the {max_upload_bytes}-byte upload limit"
                    ),
                )
            temp_file.write(chunk)
    except Exception:
        temp_file.close()
        raise

    if total_bytes == 0:
        temp_file.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="submission artifact body is required",
        )

    temp_file.seek(0)
    return temp_file
