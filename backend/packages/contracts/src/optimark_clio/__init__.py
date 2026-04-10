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
from optimark_clio.health import HealthResponse, WorkerBootstrapMessage

__all__ = [
    "CourseDetail",
    "CourseSummary",
    "CreateCourseInput",
    "CreateUserInput",
    "EnrollmentRecord",
    "EnrollUserInput",
    "HealthResponse",
    "UserDetail",
    "UserSummary",
    "WorkerBootstrapMessage",
]
