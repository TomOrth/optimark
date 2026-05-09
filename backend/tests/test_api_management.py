"""API tests for instructor course and assignment management routes."""

from fastapi.testclient import TestClient

from optimark_metis.academic import CourseRole
from optimark_metis.assessment import AssignmentPublishState, AssignmentType


def test_list_managed_courses_returns_only_instructor_courses(
    api_client: TestClient,
    auth_service,
    academic_service,
) -> None:
    """Verify the managed-courses endpoint returns instructor-owned courses.

    Args:
        api_client: FastAPI test client bound to the shared test database.
        auth_service: Auth service used to issue test sessions.
        academic_service: Academic service used to seed course memberships.
    """
    unauthenticated = api_client.get("/api/v1/courses/managed")
    assert unauthenticated.status_code == 401

    issued_session = auth_service.signup(
        email="instructor-manager@example.edu",
        display_name="Instructor Manager",
        password="super-secure-pass",
    )
    managed_course = academic_service.create_course(
        course_code="CS 5501",
        title="Advanced Algorithms",
        term="Fall 2028",
    )
    observed_course = academic_service.create_course(
        course_code="CS 5502",
        title="Distributed Systems",
        term="Fall 2028",
    )
    academic_service.enroll_user(
        course_id=managed_course.id,
        user_id=issued_session.authentication.user.id,
        role=CourseRole.INSTRUCTOR,
    )
    academic_service.enroll_user(
        course_id=observed_course.id,
        user_id=issued_session.authentication.user.id,
        role=CourseRole.STUDENT,
    )

    api_client.cookies.set("optimark_session", issued_session.token)
    response = api_client.get("/api/v1/courses/managed")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(managed_course.id),
            "course_code": "CS 5501",
            "title": "Advanced Algorithms",
            "term": "Fall 2028",
        },
    ]


def test_course_assignment_management_routes_support_crud(
    api_client: TestClient,
    auth_service,
    academic_service,
) -> None:
    """Verify instructors can create, list, fetch, and update assignments.

    Args:
        api_client: FastAPI test client bound to the shared test database.
        auth_service: Auth service used to issue test sessions.
        academic_service: Academic service used to seed course memberships.
    """
    issued_session = auth_service.signup(
        email="instructor-assignment@example.edu",
        display_name="Assignment Instructor",
        password="super-secure-pass",
    )
    course = academic_service.create_course(
        course_code="CS 6601",
        title="Program Analysis",
        term="Spring 2029",
    )
    academic_service.enroll_user(
        course_id=course.id,
        user_id=issued_session.authentication.user.id,
        role=CourseRole.INSTRUCTOR,
    )
    api_client.cookies.set("optimark_session", issued_session.token)

    create_response = api_client.post(
        f"/api/v1/courses/{course.id}/assignments",
        json={
            "title": "Escape Analysis Lab",
            "description": "Implement baseline escape analysis.",
            "assignment_type": AssignmentType.CODING.value,
            "publish_state": AssignmentPublishState.DRAFT.value,
        },
    )

    assert create_response.status_code == 201
    created_assignment = create_response.json()
    assignment_id = created_assignment["id"]
    assert created_assignment["course_id"] == str(course.id)
    assert created_assignment["title"] == "Escape Analysis Lab"

    list_response = api_client.get(f"/api/v1/courses/{course.id}/assignments")
    assert list_response.status_code == 200
    assert list_response.json() == [
        {
            "id": assignment_id,
            "course_id": str(course.id),
            "title": "Escape Analysis Lab",
            "assignment_type": AssignmentType.CODING.value,
            "publish_state": AssignmentPublishState.DRAFT.value,
        },
    ]

    detail_response = api_client.get(
        f"/api/v1/courses/{course.id}/assignments/{assignment_id}",
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["description"] == (
        "Implement baseline escape analysis."
    )

    update_response = api_client.patch(
        f"/api/v1/courses/{course.id}/assignments/{assignment_id}",
        json={
            "title": "Interprocedural Escape Analysis Lab",
            "publish_state": AssignmentPublishState.PUBLISHED.value,
        },
    )
    assert update_response.status_code == 200
    updated_assignment = update_response.json()
    assert updated_assignment["title"] == "Interprocedural Escape Analysis Lab"
    assert updated_assignment["publish_state"] == (
        AssignmentPublishState.PUBLISHED.value
    )
    assert updated_assignment["description"] == "Implement baseline escape analysis."


def test_course_assignment_management_routes_enforce_permissions_and_scope(
    api_client: TestClient,
    db_session,
    auth_service,
    academic_service,
    assessment_service,
) -> None:
    """Verify management routes reject unauthorized and out-of-scope access.

    Args:
        api_client: FastAPI test client bound to the shared test database.
        auth_service: Auth service used to issue test sessions.
        academic_service: Academic service used to seed course memberships.
        assessment_service: Assessment service used to seed assignment records.
    """
    instructor_session = auth_service.signup(
        email="course-owner@example.edu",
        display_name="Course Owner",
        password="super-secure-pass",
    )
    student_session = auth_service.signup(
        email="learner@example.edu",
        display_name="Learner",
        password="super-secure-pass",
    )
    managed_course = academic_service.create_course(
        course_code="CS 7701",
        title="Compiler Construction",
        term="Summer 2029",
    )
    other_course = academic_service.create_course(
        course_code="CS 7702",
        title="Machine Learning Systems",
        term="Summer 2029",
    )
    academic_service.enroll_user(
        course_id=managed_course.id,
        user_id=instructor_session.authentication.user.id,
        role=CourseRole.INSTRUCTOR,
    )
    academic_service.enroll_user(
        course_id=other_course.id,
        user_id=instructor_session.authentication.user.id,
        role=CourseRole.INSTRUCTOR,
    )
    academic_service.enroll_user(
        course_id=managed_course.id,
        user_id=student_session.authentication.user.id,
        role=CourseRole.STUDENT,
    )
    assignment = assessment_service.create_assignment(
        course_id=managed_course.id,
        title="SSA Lab",
        description="Build an SSA transformer.",
        assignment_type=AssignmentType.CODING,
        publish_state=AssignmentPublishState.DRAFT,
    )
    db_session.commit()

    unauthenticated = api_client.get(
        f"/api/v1/courses/{managed_course.id}/assignments",
    )
    assert unauthenticated.status_code == 401

    api_client.cookies.set("optimark_session", student_session.token)
    forbidden = api_client.get(f"/api/v1/courses/{managed_course.id}/assignments")
    assert forbidden.status_code == 403

    api_client.cookies.set("optimark_session", instructor_session.token)
    wrong_scope = api_client.get(
        f"/api/v1/courses/{other_course.id}/assignments/{assignment.id}",
    )
    assert wrong_scope.status_code == 404

    invalid_update = api_client.patch(
        f"/api/v1/courses/{managed_course.id}/assignments/{assignment.id}",
        json={},
    )
    assert invalid_update.status_code == 400
    assert invalid_update.json() == {
        "detail": "at least one assignment field must be provided",
    }


def test_course_assignment_management_routes_allow_idempotent_updates(
    api_client: TestClient,
    db_session,
    auth_service,
    academic_service,
    assessment_service,
) -> None:
    """Verify managed assignment updates remain idempotent for editor actions."""
    instructor_session = auth_service.signup(
        email="idempotent-instructor@example.edu",
        display_name="Idempotent Instructor",
        password="super-secure-pass",
    )
    course = academic_service.create_course(
        course_code="CS 8801",
        title="Static Analysis",
        term="Fall 2029",
    )
    academic_service.enroll_user(
        course_id=course.id,
        user_id=instructor_session.authentication.user.id,
        role=CourseRole.INSTRUCTOR,
    )
    assignment = assessment_service.create_assignment(
        course_id=course.id,
        title="Alias Analysis Lab",
        description="Implement Andersen-style points-to analysis.",
        assignment_type=AssignmentType.CODING,
        publish_state=AssignmentPublishState.DRAFT,
    )
    db_session.commit()

    api_client.cookies.set("optimark_session", instructor_session.token)
    update_response = api_client.patch(
        f"/api/v1/courses/{course.id}/assignments/{assignment.id}",
        json={
            "title": assignment.title,
            "description": assignment.description,
            "assignment_type": assignment.assignment_type.value,
            "publish_state": assignment.publish_state.value,
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["id"] == str(assignment.id)
    assert update_response.json()["publish_state"] == (
        AssignmentPublishState.DRAFT.value
    )
