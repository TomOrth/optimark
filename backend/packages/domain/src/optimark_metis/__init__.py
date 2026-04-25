"""Metis domain package for Optimark."""

from optimark_metis.academic import Course, CourseRole, Enrollment, User
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
    AuthenticationRequiredError,
    AuthorizationError,
    AuthDomainError,
    DuplicateEmailError,
    DuplicateEnrollmentError,
    EntityNotFoundError,
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
    "DuplicateEmailError",
    "DuplicateEnrollmentError",
    "Enrollment",
    "EntityNotFoundError",
    "InvalidCredentialsError",
    "InvalidAcademicDataError",
    "IssuedSession",
    "PasswordAuthentication",
    "PasswordPolicyError",
    "ServiceDescriptor",
    "SessionExpiredError",
    "User",
    "build_service_descriptor",
    "capabilities_for_role",
    "roles_for_capability",
]
