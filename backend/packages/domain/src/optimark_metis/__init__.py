"""Metis domain package for Optimark."""

from optimark_metis.academic import Course, CourseRole, Enrollment, User
from optimark_metis.errors import (
    AcademicDomainError,
    DuplicateEnrollmentError,
    EntityNotFoundError,
    InvalidAcademicDataError,
)
from optimark_metis.repository import AcademicRepository
from optimark_metis.runtime import ServiceDescriptor, build_service_descriptor
from optimark_metis.service import AcademicService

__all__ = [
    "AcademicDomainError",
    "AcademicRepository",
    "AcademicService",
    "Course",
    "CourseRole",
    "DuplicateEnrollmentError",
    "Enrollment",
    "EntityNotFoundError",
    "InvalidAcademicDataError",
    "ServiceDescriptor",
    "User",
    "build_service_descriptor",
]
