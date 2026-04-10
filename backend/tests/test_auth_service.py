"""Service and repository tests for the auth domain foundation."""

from datetime import UTC, datetime, timedelta
import hashlib

from pwdlib import PasswordHash

from optimark_metis.academic import CourseRole
from optimark_metis.auth import CourseCapability
from optimark_metis.auth_service import AuthService
from optimark_metis.authorization import AuthorizationService, capabilities_for_role
from optimark_metis.errors import (
    AuthenticationRequiredError,
    DuplicateEmailError,
    InvalidCredentialsError,
    PasswordPolicyError,
    SessionExpiredError,
)
from optimark_mnemosyne.auth_repository import SqlAlchemyAuthRepository
from optimark_mnemosyne.repository import SqlAlchemyAcademicRepository


def test_auth_service_signup_and_login_issue_sessions(auth_service: AuthService) -> None:
    """Verify signup and login issue password-backed sessions."""
    issued_signup = auth_service.signup(
        email="  instructor@example.edu ",
        display_name="  Dr. Grace Hopper ",
        password="super-secure-pass",
    )
    issued_login = auth_service.login(
        email="instructor@example.edu",
        password="super-secure-pass",
    )

    assert issued_signup.authentication.user.email == "instructor@example.edu"
    assert issued_signup.authentication.user.display_name == "Dr. Grace Hopper"
    assert (
        issued_signup.authentication.session.user_id
        == issued_signup.authentication.user.id
    )
    assert issued_login.authentication.user.id == issued_signup.authentication.user.id
    assert issued_login.token != issued_signup.token


def test_auth_service_rejects_duplicate_canonical_signup_email(
    auth_service: AuthService,
) -> None:
    """Verify signup rejects duplicate canonical emails."""
    auth_service.signup(
        email="Instructor@Example.edu",
        display_name="Instructor",
        password="super-secure-pass",
    )

    try:
        auth_service.signup(
            email=" instructor@example.edu ",
            display_name="Duplicate Instructor",
            password="another-secure-pass",
        )
    except DuplicateEmailError:
        pass
    else:
        raise AssertionError("expected duplicate canonical email to be rejected")


def test_auth_service_rejects_invalid_passwords(auth_service: AuthService) -> None:
    """Verify signup and login enforce the baseline password policy."""
    try:
        auth_service.signup(
            email="student@example.edu",
            display_name="Student",
            password="short",
        )
    except PasswordPolicyError:
        pass
    else:
        raise AssertionError("expected weak password to be rejected")

    auth_service.signup(
        email="student@example.edu",
        display_name="Student",
        password="very-secure-pass",
    )

    try:
        auth_service.login(
            email="student@example.edu",
            password="",
        )
    except PasswordPolicyError:
        pass
    else:
        raise AssertionError("expected blank login password to be rejected")


def test_auth_service_rejects_invalid_credentials(auth_service: AuthService) -> None:
    """Verify login rejects incorrect credentials."""
    auth_service.signup(
        email="ta@example.edu",
        display_name="TA",
        password="very-secure-pass",
    )

    try:
        auth_service.login(
            email="ta@example.edu",
            password="wrong-password",
        )
    except InvalidCredentialsError:
        pass
    else:
        raise AssertionError("expected invalid credentials to be rejected")


def test_auth_service_revokes_and_expires_sessions(db_session) -> None:
    """Verify logout and expiry invalidate persisted sessions."""
    current_time = [datetime(2026, 4, 9, 12, 0, tzinfo=UTC)]

    def now_provider() -> datetime:
        """Return the current synthetic test time."""
        return current_time[0]

    expiring_repository = SqlAlchemyAuthRepository(db_session)
    auth_service = AuthService(
        academic_repository=SqlAlchemyAcademicRepository(db_session),
        auth_repository=expiring_repository,
        password_hasher=PasswordHash.recommended(),
        session_ttl=timedelta(days=14),
        token_generator=lambda: "expiring-session-token",
        now_provider=now_provider,
    )

    issued_session = auth_service.signup(
        email="student@example.edu",
        display_name="Student",
        password="very-secure-pass",
    )
    authentication = auth_service.get_session_user(session_token=issued_session.token)
    assert authentication.user.email == "student@example.edu"

    auth_service.logout(session_token=issued_session.token)
    try:
        auth_service.get_session_user(session_token=issued_session.token)
    except AuthenticationRequiredError:
        pass
    else:
        raise AssertionError("expected revoked session to be rejected")

    revoked_session = expiring_repository.get_authenticated_session_by_token_hash(
        token_hash=hashlib.sha256(
            issued_session.token.encode("utf-8"),
            usedforsecurity=True,
        ).hexdigest(),
    )
    assert revoked_session is not None
    assert revoked_session.session.revoked_at == current_time[0]

    current_time[0] = current_time[0] + timedelta(days=1)
    expiring_service = AuthService(
        academic_repository=SqlAlchemyAcademicRepository(db_session),
        auth_repository=expiring_repository,
        password_hasher=PasswordHash.recommended(),
        session_ttl=timedelta(days=14),
        token_generator=lambda: "later-session-token",
        now_provider=now_provider,
    )
    issued_later = expiring_service.login(
        email="student@example.edu",
        password="very-secure-pass",
    )

    current_time[0] = current_time[0] + timedelta(days=15)
    try:
        expiring_service.get_session_user(session_token=issued_later.token)
    except SessionExpiredError:
        pass
    else:
        raise AssertionError("expected expired session to be rejected")


def test_authorization_service_maps_role_capabilities(
    academic_service,
) -> None:
    """Verify course capabilities map to the expected enrollment roles."""
    instructor = academic_service.create_user(
        email="instructor@example.edu",
        display_name="Instructor",
    )
    ta = academic_service.create_user(
        email="ta@example.edu",
        display_name="TA",
    )
    student = academic_service.create_user(
        email="student@example.edu",
        display_name="Student",
    )
    course = academic_service.create_course(
        course_code="CS 4510",
        title="Automata and Complexity",
        term="Fall 2027",
    )
    academic_service.enroll_user(
        course_id=course.id,
        user_id=instructor.id,
        role=CourseRole.INSTRUCTOR,
    )
    academic_service.enroll_user(
        course_id=course.id,
        user_id=ta.id,
        role=CourseRole.TA,
    )
    academic_service.enroll_user(
        course_id=course.id,
        user_id=student.id,
        role=CourseRole.STUDENT,
    )

    authorization_service = AuthorizationService(academic_service)

    assert CourseCapability.MANAGE_COURSE in capabilities_for_role(
        CourseRole.INSTRUCTOR,
    )
    assert authorization_service.user_has_course_capability(
        course_id=course.id,
        user_id=instructor.id,
        capability=CourseCapability.MANAGE_COURSE,
    )
    assert authorization_service.user_has_course_capability(
        course_id=course.id,
        user_id=ta.id,
        capability=CourseCapability.GRADE_SUBMISSIONS,
    )
    assert authorization_service.user_has_course_capability(
        course_id=course.id,
        user_id=student.id,
        capability=CourseCapability.SUBMIT_WORK,
    )
    assert not authorization_service.user_has_course_capability(
        course_id=course.id,
        user_id=student.id,
        capability=CourseCapability.GRADE_SUBMISSIONS,
    )
