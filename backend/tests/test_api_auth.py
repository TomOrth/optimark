"""API tests for signup, login, logout, and auth dependencies."""

from datetime import timedelta

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from optimark_athena.config import AuthSettings
from optimark_athena.dependencies import (
    get_auth_settings,
    get_db_session,
    require_course_capability,
)
from optimark_metis.academic import CourseRole
from optimark_metis.auth import CourseCapability


def test_signup_login_session_and_logout_flow(api_client: TestClient) -> None:
    """Verify the auth endpoints set cookies and restore sessions."""
    signup_response = api_client.post(
        "/api/v1/auth/signup",
        json={
            "email": "instructor@example.edu",
            "display_name": "Instructor",
            "password": "super-secure-pass",
        },
    )

    assert signup_response.status_code == 201
    assert signup_response.json()["user"]["email"] == "instructor@example.edu"
    assert "optimark_session=" in signup_response.headers["set-cookie"]

    session_response = api_client.get("/api/v1/auth/session")
    assert session_response.status_code == 200
    assert session_response.json()["user"]["display_name"] == "Instructor"

    logout_response = api_client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 204

    unauthorized_session = api_client.get("/api/v1/auth/session")
    assert unauthorized_session.status_code == 401

    login_response = api_client.post(
        "/api/v1/auth/login",
        json={
            "email": "instructor@example.edu",
            "password": "super-secure-pass",
        },
    )
    assert login_response.status_code == 200
    assert login_response.json()["user"]["email"] == "instructor@example.edu"
    assert "optimark_session=" in login_response.headers["set-cookie"]


def test_auth_routes_reject_invalid_credentials(api_client: TestClient) -> None:
    """Verify login rejects incorrect credentials."""
    api_client.post(
        "/api/v1/auth/signup",
        json={
            "email": "ta@example.edu",
            "display_name": "TA",
            "password": "super-secure-pass",
        },
    )

    response = api_client.post(
        "/api/v1/auth/login",
        json={
            "email": "ta@example.edu",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid email or password"}


def test_course_capability_dependency_enforces_auth_and_role(
    db_session,
    auth_service,
    academic_service,
) -> None:
    """Verify the capability dependency returns 401 and 403 when appropriate."""
    probe_app = FastAPI()

    @probe_app.get("/courses/{course_id}/grade")
    def grade_probe(
        authentication=Depends(
            require_course_capability(CourseCapability.GRADE_SUBMISSIONS),
        ),
    ) -> dict[str, str]:
        return {"user_id": str(authentication.user.id)}

    def override_get_db_session():
        yield db_session

    probe_app.dependency_overrides[get_db_session] = override_get_db_session
    probe_app.dependency_overrides[get_auth_settings] = lambda: AuthSettings(
        cookie_name="optimark_session",
        session_ttl=timedelta(days=14),
        cookie_secure=False,
        cookie_same_site="lax",
    )

    issued_session = auth_service.signup(
        email="student@example.edu",
        display_name="Student",
        password="super-secure-pass",
    )
    course = academic_service.create_course(
        course_code="CS 3251",
        title="Computer Networking",
        term="Spring 2028",
    )
    academic_service.enroll_user(
        course_id=course.id,
        user_id=issued_session.authentication.user.id,
        role=CourseRole.STUDENT,
    )

    with TestClient(probe_app) as client:
        unauthenticated = client.get(f"/courses/{course.id}/grade")
        assert unauthenticated.status_code == 401

        client.cookies.set("optimark_session", issued_session.token)
        forbidden = client.get(f"/courses/{course.id}/grade")
        assert forbidden.status_code == 403

    probe_app.dependency_overrides.clear()
