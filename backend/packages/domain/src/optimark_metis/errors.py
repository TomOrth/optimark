"""Custom exceptions for academic domain and service operations."""

class AcademicDomainError(Exception):
    """Base error for academic domain operations."""


class InvalidAcademicDataError(AcademicDomainError):
    """Raised when required academic fields are missing or malformed."""


class EntityNotFoundError(AcademicDomainError):
    """Raised when a requested entity does not exist."""


class DuplicateEnrollmentError(AcademicDomainError):
    """Raised when a user is enrolled in the same course more than once."""
