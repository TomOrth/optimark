"""Shared contracts exposed by the Clio package."""

from optimark_clio.academic import (
    CourseDetail,
    CourseSummary,
    CreateCourseInput,
    CreateUserInput,
    EnrollmentRecord,
    EnrollUserInput,
    UserDetail,
    UserSummary,
)
from optimark_clio.auth import (
    AuthErrorResponse,
    LoginRequest,
    SessionResponse,
    SessionUser,
    SignupRequest,
)
from optimark_clio.health import HealthResponse, WorkerBootstrapMessage

__all__ = [
    "AuthErrorResponse",
    "CourseDetail",
    "CourseSummary",
    "CreateCourseInput",
    "CreateUserInput",
    "EnrollmentRecord",
    "EnrollUserInput",
    "HealthResponse",
    "LoginRequest",
    "SessionResponse",
    "SessionUser",
    "SignupRequest",
    "UserDetail",
    "UserSummary",
    "WorkerBootstrapMessage",
]
