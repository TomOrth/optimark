"""Student submission API routes backed by S3-compatible artifact storage."""

from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import PurePosixPath
import re
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from optimark_athena.artifact_store import ArtifactStore
from optimark_athena.dependencies import (
    get_academic_service,
    get_artifact_store,
    get_assessment_service,
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

            active_version = _get_or_create_active_assignment_version(
                assessment_service=assessment_service,
                assignment_id=assignment.id,
                created_by_user_id=authentication.user.id,
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
                    active_assignment_version_id=active_version.id,
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
    active_version = _get_or_create_active_assignment_version(
        assessment_service=assessment_service,
        assignment_id=assignment.id,
        created_by_user_id=authentication.user.id,
    )
    submissions = assessment_service.list_assignment_submissions(
        assignment.id,
        student_user_id=authentication.user.id,
    )

    return StudentSubmissionWorkspace(
        course=CourseSummary.from_domain(course),
        assignment=AssignmentDetail.from_domain(assignment),
        active_assignment_version_id=active_version.id,
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
    artifact_store: Annotated[ArtifactStore, Depends(get_artifact_store)] = None,
) -> StudentSubmissionRecord:
    """Store an uploaded artifact and create a submission record for the student."""
    assignment = _require_student_submittable_assignment(
        assessment_service=assessment_service,
        assignment_id=assignment_id,
        course_id=course_id,
    )
    active_version = _get_or_create_active_assignment_version(
        assessment_service=assessment_service,
        assignment_id=assignment.id,
        created_by_user_id=authentication.user.id,
    )

    artifact_body = await request.body()
    if not artifact_body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="submission artifact body is required",
        )

    normalized_filename = _normalize_filename(filename)
    artifact_key = _build_artifact_key(
        course_id=course_id,
        assignment_id=assignment.id,
        student_user_id=authentication.user.id,
        filename=normalized_filename,
    )
    artifact_key = artifact_store.put_artifact(
        key=artifact_key,
        body=artifact_body,
        content_type=request.headers.get("content-type", "application/octet-stream"),
        metadata={
            "course-id": str(course_id),
            "assignment-id": str(assignment.id),
            "student-user-id": str(authentication.user.id),
            "filename": normalized_filename,
        },
    )

    submission_state = (
        SubmissionState.DRAFT if state == "draft" else SubmissionState.SUBMITTED
    )
    submission = assessment_service.create_submission(
        assignment_id=assignment.id,
        assignment_version_id=active_version.id,
        student_user_id=authentication.user.id,
        state=submission_state,
        artifact_key=artifact_key,
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

    return StudentSubmissionRecord.from_domain(
        submission,
        evaluations=evaluations,
        artifact_name=normalized_filename,
    )


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


def _get_or_create_active_assignment_version(
    *,
    assessment_service: AssessmentService,
    assignment_id: UUID,
    created_by_user_id: UUID,
):
    """Return the latest assignment version, creating an initial snapshot if needed."""
    versions = assessment_service.list_assignment_versions(assignment_id)
    if versions:
        return versions[-1]

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
            created_by_user_id=created_by_user_id,
        )
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
    serialized = [
        StudentSubmissionRecord.from_domain(
            submission,
            evaluations=assessment_service.list_submission_evaluations(submission.id),
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
    return StudentSubmissionRecord.from_domain(
        latest_submission,
        evaluations=assessment_service.list_submission_evaluations(latest_submission.id),
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
    filename: str,
) -> str:
    """Build a deterministic artifact key rooted under the submission prefix."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return (
        f"{course_id}/{assignment_id}/{student_user_id}/"
        f"{timestamp}__{filename}"
    )


def _artifact_name_from_key(artifact_key: str | None) -> str | None:
    """Recover the original filename suffix from an artifact key."""
    if artifact_key is None:
        return None
    tail = PurePosixPath(artifact_key).name
    if "__" not in tail:
        return tail
    return tail.split("__", 1)[1] or tail
