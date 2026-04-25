"""Metis domain package for Optimark."""

from optimark_metis.academic import Course, CourseRole, Enrollment, User
from optimark_metis.assessment import (
    Assignment,
    AssignmentPublishState,
    AssignmentType,
    AssignmentVersion,
    EvaluationKind,
    EvaluationRecord,
    EvaluationStatus,
    GradeRecord,
    GradeState,
    Submission,
    SubmissionState,
)
from optimark_metis.assessment_repository import AssessmentRepository
from optimark_metis.assessment_service import AssessmentService
from optimark_metis.auth import (
    AuthIdentity,
    AuthProvider,
    AuthSession,
    AuthenticatedSession,
    CourseCapability,
    IssuedSession,
    PasswordAuthentication,
)
from optimark_metis.auth_repository import AuthRepository
from optimark_metis.auth_service import AuthService
from optimark_metis.authorization import (
    AuthorizationService,
    capabilities_for_role,
    roles_for_capability,
)
from optimark_metis.errors import (
    AcademicDomainError,
    AssessmentDomainError,
    AuthenticationRequiredError,
    AuthorizationError,
    AuthDomainError,
    DuplicateAssignmentVersionError,
    DuplicateEmailError,
    DuplicateEnrollmentError,
    EntityNotFoundError,
    InvalidAssessmentDataError,
    InvalidCredentialsError,
    InvalidAcademicDataError,
    PasswordPolicyError,
    SessionExpiredError,
)
from optimark_metis.repository import AcademicRepository
from optimark_metis.runtime import ServiceDescriptor, build_service_descriptor
from optimark_metis.service import AcademicService

__all__ = [
    "AcademicDomainError",
    "AcademicRepository",
    "AcademicService",
    "AssessmentDomainError",
    "AssessmentRepository",
    "AssessmentService",
    "Assignment",
    "AssignmentPublishState",
    "AssignmentType",
    "AssignmentVersion",
    "AuthDomainError",
    "AuthIdentity",
    "AuthProvider",
    "AuthRepository",
    "AuthService",
    "AuthSession",
    "AuthenticatedSession",
    "AuthenticationRequiredError",
    "AuthorizationError",
    "AuthorizationService",
    "Course",
    "CourseCapability",
    "CourseRole",
    "DuplicateAssignmentVersionError",
    "DuplicateEmailError",
    "DuplicateEnrollmentError",
    "Enrollment",
    "EntityNotFoundError",
    "EvaluationKind",
    "EvaluationRecord",
    "EvaluationStatus",
    "GradeRecord",
    "GradeState",
    "InvalidAssessmentDataError",
    "InvalidCredentialsError",
    "InvalidAcademicDataError",
    "IssuedSession",
    "PasswordAuthentication",
    "PasswordPolicyError",
    "ServiceDescriptor",
    "SessionExpiredError",
    "Submission",
    "SubmissionState",
    "User",
    "build_service_descriptor",
    "capabilities_for_role",
    "roles_for_capability",
]
