"""Instructor-facing course and assignment management API routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from optimark_athena.dependencies import (
    get_academic_service,
    get_assessment_service,
    require_authenticated_user,
    require_course_capability,
)
from optimark_clio import (
    AssignmentDetail,
    AssignmentSummary,
    AuthErrorResponse,
    CourseSummary,
    CreateCourseAssignmentInput,
    UpdateAssignmentInput,
)
from optimark_metis import (
    AcademicService,
    Assignment,
    AssessmentService,
    CourseCapability,
    EntityNotFoundError,
    InvalidAssessmentDataError,
)
from optimark_metis.academic import CourseRole, User


router = APIRouter(prefix="/api/v1", tags=["management"])


@router.get(
    "/courses/managed",
    response_model=list[CourseSummary],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": AuthErrorResponse},
    },
)
def list_managed_courses(
    current_user: Annotated[User, Depends(require_authenticated_user)],
    academic_service: Annotated[AcademicService, Depends(get_academic_service)],
) -> list[CourseSummary]:
    """List courses the authenticated instructor can manage.

    Args:
        current_user: Authenticated platform user.
        academic_service: Academic service used to resolve course memberships.

    Returns:
        list[CourseSummary]: Managed course summaries for the instructor.
    """
    courses = academic_service.list_courses_for_user(
        current_user.id,
        role_filter=CourseRole.INSTRUCTOR,
    )
    return [CourseSummary.from_domain(course) for course in courses]


@router.get(
    "/courses/{course_id}/assignments",
    response_model=list[AssignmentSummary],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": AuthErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": AuthErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": AuthErrorResponse},
    },
)
def list_course_assignments(
    course_id: UUID,
    _: Annotated[
        object,
        Depends(require_course_capability(CourseCapability.MANAGE_COURSE)),
    ],
    assessment_service: Annotated[AssessmentService, Depends(get_assessment_service)],
) -> list[AssignmentSummary]:
    """List assignments for a managed course.

    Args:
        course_id: Course identifier from the route path.
        _: Authenticated capability-gated session context.
        assessment_service: Assessment service used to load assignments.

    Returns:
        list[AssignmentSummary]: Assignment summaries for the course.
    """
    assignments = assessment_service.list_course_assignments(course_id)
    return [AssignmentSummary.from_domain(assignment) for assignment in assignments]


@router.post(
    "/courses/{course_id}/assignments",
    response_model=AssignmentDetail,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": AuthErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": AuthErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": AuthErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": AuthErrorResponse},
    },
)
def create_course_assignment(
    course_id: UUID,
    payload: CreateCourseAssignmentInput,
    _: Annotated[
        object,
        Depends(require_course_capability(CourseCapability.MANAGE_COURSE)),
    ],
    assessment_service: Annotated[AssessmentService, Depends(get_assessment_service)],
) -> AssignmentDetail:
    """Create a new assignment within a managed course.

    Args:
        course_id: Course identifier from the route path.
        payload: Assignment creation payload.
        _: Authenticated capability-gated session context.
        assessment_service: Assessment service used to persist the assignment.

    Returns:
        AssignmentDetail: Persisted assignment payload.

    Raises:
        HTTPException: If the payload is invalid.
    """
    try:
        assignment = assessment_service.create_assignment(
            course_id=course_id,
            title=payload.title,
            description=payload.description,
            assignment_type=payload.assignment_type,
            publish_state=payload.publish_state,
        )
    except InvalidAssessmentDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return AssignmentDetail.from_domain(assignment)


@router.get(
    "/courses/{course_id}/assignments/{assignment_id}",
    response_model=AssignmentDetail,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": AuthErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": AuthErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": AuthErrorResponse},
    },
)
def get_course_assignment(
    course_id: UUID,
    assignment_id: UUID,
    _: Annotated[
        object,
        Depends(require_course_capability(CourseCapability.MANAGE_COURSE)),
    ],
    assessment_service: Annotated[AssessmentService, Depends(get_assessment_service)],
) -> AssignmentDetail:
    """Fetch a single assignment detail within a managed course.

    Args:
        course_id: Course identifier from the route path.
        assignment_id: Assignment identifier from the route path.
        _: Authenticated capability-gated session context.
        assessment_service: Assessment service used to load the assignment.

    Returns:
        AssignmentDetail: Assignment detail payload scoped to the course.
    """
    assignment = _get_course_scoped_assignment(
        course_id=course_id,
        assignment_id=assignment_id,
        assessment_service=assessment_service,
    )
    return AssignmentDetail.from_domain(assignment)


@router.patch(
    "/courses/{course_id}/assignments/{assignment_id}",
    response_model=AssignmentDetail,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": AuthErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": AuthErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": AuthErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": AuthErrorResponse},
    },
)
def update_course_assignment(
    course_id: UUID,
    assignment_id: UUID,
    payload: UpdateAssignmentInput,
    _: Annotated[
        object,
        Depends(require_course_capability(CourseCapability.MANAGE_COURSE)),
    ],
    assessment_service: Annotated[AssessmentService, Depends(get_assessment_service)],
) -> AssignmentDetail:
    """Update a managed course assignment.

    Args:
        course_id: Course identifier from the route path.
        assignment_id: Assignment identifier from the route path.
        payload: Editable assignment fields to update.
        _: Authenticated capability-gated session context.
        assessment_service: Assessment service used to persist the update.

    Returns:
        AssignmentDetail: Updated assignment payload.

    Raises:
        HTTPException: If the assignment is missing, outside the course, or invalid.
    """
    _get_course_scoped_assignment(
        course_id=course_id,
        assignment_id=assignment_id,
        assessment_service=assessment_service,
    )

    try:
        updated_assignment = assessment_service.update_assignment(
            assignment_id=assignment_id,
            title=payload.title,
            description=payload.description,
            assignment_type=payload.assignment_type,
            publish_state=payload.publish_state,
        )
    except InvalidAssessmentDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return AssignmentDetail.from_domain(updated_assignment)


def _get_course_scoped_assignment(
    *,
    course_id: UUID,
    assignment_id: UUID,
    assessment_service: AssessmentService,
) -> Assignment:
    """Resolve an assignment and verify it belongs to the requested course.

    Args:
        course_id: Course identifier from the route path.
        assignment_id: Assignment identifier from the route path.
        assessment_service: Assessment service used to load the assignment.

    Returns:
        Assignment: Resolved assignment entity.

    Raises:
        HTTPException: If the assignment does not exist for the given course.
    """
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

    return assignment
