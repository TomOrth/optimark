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
from optimark_clio.assessment import (
    AssignmentDetail,
    AssignmentSummary,
    AssignmentVersionRecord,
    CreateAssignmentInput,
    CreateAssignmentVersionInput,
    CreateSubmissionInput,
    EvaluationRecordPayload,
    GradeRecordPayload,
    RecordEvaluationInput,
    RecordGradeInput,
    SubmissionRecord,
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
    "AssignmentDetail",
    "AssignmentSummary",
    "AssignmentVersionRecord",
    "AuthErrorResponse",
    "CourseDetail",
    "CourseSummary",
    "CreateAssignmentInput",
    "CreateAssignmentVersionInput",
    "CreateCourseInput",
    "CreateSubmissionInput",
    "CreateUserInput",
    "EnrollmentRecord",
    "EvaluationRecordPayload",
    "EnrollUserInput",
    "GradeRecordPayload",
    "HealthResponse",
    "LoginRequest",
    "RecordEvaluationInput",
    "RecordGradeInput",
    "SessionResponse",
    "SessionUser",
    "SignupRequest",
    "SubmissionRecord",
    "UserDetail",
    "UserSummary",
    "WorkerBootstrapMessage",
]
