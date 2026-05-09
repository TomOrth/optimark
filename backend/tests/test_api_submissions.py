"""API tests for the student submission workflow."""

from uuid import UUID

from fastapi.testclient import TestClient

from optimark_metis.academic import CourseRole
from optimark_metis.assessment import (
    AssignmentPublishState,
    AssignmentType,
    EvaluationKind,
    EvaluationStatus,
    SubmissionState,
)


def test_student_can_list_workspace_and_create_draft_submission(
    api_client: TestClient,
    academic_service,
    assessment_service,
    auth_service,
    fake_artifact_store,
) -> None:
    """Verify students can access a published coding task and save a draft."""
    student_session = auth_service.signup(
        email="student@example.edu",
        display_name="Student",
        password="super-secure-pass",
    )
    course = academic_service.create_course(
        course_code="CS 3100",
        title="Systems",
        term="Fall 2028",
    )
    academic_service.enroll_user(
        course_id=course.id,
        user_id=student_session.authentication.user.id,
        role=CourseRole.STUDENT,
    )
    assignment = assessment_service.create_assignment(
        course_id=course.id,
        title="Project 1",
        description="Submit your starter archive.",
        assignment_type=AssignmentType.CODING,
        publish_state=AssignmentPublishState.PUBLISHED,
    )

    api_client.cookies.set("optimark_session", student_session.token)

    assignments_response = api_client.get("/api/v1/student/assignments")
    assert assignments_response.status_code == 200
    assignments_payload = assignments_response.json()
    assert len(assignments_payload) == 1
    assert assignments_payload[0]["assignment"]["title"] == "Project 1"
    assert assignments_payload[0]["latest_submission"] is None
    assert assignments_payload[0]["active_assignment_version_id"]

    workspace_response = api_client.get(
        f"/api/v1/courses/{course.id}/assignments/{assignment.id}/submission-workspace",
    )
    assert workspace_response.status_code == 200
    workspace_payload = workspace_response.json()
    assert workspace_payload["assignment"]["title"] == "Project 1"
    assert workspace_payload["submissions"] == []

    create_response = api_client.post(
        f"/api/v1/courses/{course.id}/assignments/{assignment.id}/submissions",
        params={"filename": "starter.zip", "state": "draft"},
        content=b"zip-binary",
        headers={"content-type": "application/zip"},
    )
    assert create_response.status_code == 201
    submission_payload = create_response.json()
    assert submission_payload["state"] == SubmissionState.DRAFT.value
    assert submission_payload["lifecycle_status"] == "draft"
    assert submission_payload["artifact_name"] == "starter.zip"
    assert submission_payload["submitted_at"] is None
    assert submission_payload["artifact_key"] in fake_artifact_store.objects
    assert (
        fake_artifact_store.objects[submission_payload["artifact_key"]]["body"]
        == b"zip-binary"
    )

    refreshed_workspace = api_client.get(
        f"/api/v1/courses/{course.id}/assignments/{assignment.id}/submission-workspace",
    )
    assert refreshed_workspace.status_code == 200
    refreshed_payload = refreshed_workspace.json()
    assert len(refreshed_payload["submissions"]) == 1
    assert refreshed_payload["submissions"][0]["lifecycle_status"] == "draft"


def test_submitted_artifact_is_queued_for_automation(
    api_client: TestClient,
    academic_service,
    assessment_service,
    auth_service,
) -> None:
    """Verify final submissions create a queued automated evaluation."""
    student_session = auth_service.signup(
        email="student2@example.edu",
        display_name="Student Two",
        password="super-secure-pass",
    )
    course = academic_service.create_course(
        course_code="CS 4100",
        title="Compilers",
        term="Spring 2029",
    )
    academic_service.enroll_user(
        course_id=course.id,
        user_id=student_session.authentication.user.id,
        role=CourseRole.STUDENT,
    )
    assignment = assessment_service.create_assignment(
        course_id=course.id,
        title="Parser Lab",
        description="Upload your parser bundle.",
        assignment_type=AssignmentType.CODING,
        publish_state=AssignmentPublishState.PUBLISHED,
    )

    api_client.cookies.set("optimark_session", student_session.token)
    response = api_client.post(
        f"/api/v1/courses/{course.id}/assignments/{assignment.id}/submissions",
        params={"filename": "parser.tar.gz", "state": "submitted"},
        content=b"bundle",
        headers={"content-type": "application/gzip"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["state"] == SubmissionState.SUBMITTED.value
    assert payload["lifecycle_status"] == "queued"
    assert payload["submitted_at"] is not None

    submission = assessment_service.get_submission(UUID(payload["id"]))
    evaluations = assessment_service.list_submission_evaluations(submission.id)
    assert len(evaluations) == 1
    assert evaluations[0].evaluation_kind is EvaluationKind.AUTOMATED
    assert evaluations[0].status is EvaluationStatus.QUEUED


def test_student_submission_routes_reject_unpublished_assignments(
    api_client: TestClient,
    academic_service,
    assessment_service,
    auth_service,
) -> None:
    """Verify unpublished assignments are not exposed through student routes."""
    student_session = auth_service.signup(
        email="student3@example.edu",
        display_name="Student Three",
        password="super-secure-pass",
    )
    course = academic_service.create_course(
        course_code="CS 2050",
        title="Discrete Math",
        term="Fall 2029",
    )
    academic_service.enroll_user(
        course_id=course.id,
        user_id=student_session.authentication.user.id,
        role=CourseRole.STUDENT,
    )
    hidden_assignment = assessment_service.create_assignment(
        course_id=course.id,
        title="Hidden Draft",
        description="Not yet visible.",
        assignment_type=AssignmentType.CODING,
        publish_state=AssignmentPublishState.DRAFT,
    )

    api_client.cookies.set("optimark_session", student_session.token)

    list_response = api_client.get("/api/v1/student/assignments")
    assert list_response.status_code == 200
    assert list_response.json() == []

    workspace_response = api_client.get(
        f"/api/v1/courses/{course.id}/assignments/{hidden_assignment.id}/submission-workspace",
    )
    assert workspace_response.status_code == 404


def test_non_students_cannot_submit_work(
    api_client: TestClient,
    academic_service,
    assessment_service,
    auth_service,
) -> None:
    """Verify course capability enforcement blocks non-student submission access."""
    instructor_session = auth_service.signup(
        email="instructor@example.edu",
        display_name="Instructor",
        password="super-secure-pass",
    )
    course = academic_service.create_course(
        course_code="CS 4500",
        title="Distributed Systems",
        term="Winter 2029",
    )
    academic_service.enroll_user(
        course_id=course.id,
        user_id=instructor_session.authentication.user.id,
        role=CourseRole.INSTRUCTOR,
    )
    assignment = assessment_service.create_assignment(
        course_id=course.id,
        title="Lab 2",
        description="Upload your cluster bundle.",
        assignment_type=AssignmentType.CODING,
        publish_state=AssignmentPublishState.PUBLISHED,
    )

    api_client.cookies.set("optimark_session", instructor_session.token)
    response = api_client.post(
        f"/api/v1/courses/{course.id}/assignments/{assignment.id}/submissions",
        params={"filename": "cluster.zip", "state": "submitted"},
        content=b"cluster",
        headers={"content-type": "application/zip"},
    )

    assert response.status_code == 403
