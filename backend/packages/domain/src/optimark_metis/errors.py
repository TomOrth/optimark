"""Custom exceptions for domain and service operations."""

class AcademicDomainError(Exception):
    """Base error for academic domain operations."""


class InvalidAcademicDataError(AcademicDomainError):
    """Raised when required academic fields are missing or malformed."""


class EntityNotFoundError(AcademicDomainError):
    """Raised when a requested entity does not exist."""


class DuplicateEmailError(AcademicDomainError):
    """Raised when a canonical user email already exists."""


class DuplicateEnrollmentError(AcademicDomainError):
    """Raised when a user is enrolled in the same course more than once."""


class AuthDomainError(Exception):
    """Base error for auth and authorization operations."""


class InvalidCredentialsError(AuthDomainError):
    """Raised when login credentials do not match a stored identity."""


class PasswordPolicyError(AuthDomainError):
    """Raised when a supplied password fails the baseline policy."""


class AuthenticationRequiredError(AuthDomainError):
    """Raised when a request requires a valid authenticated session."""


class SessionExpiredError(AuthenticationRequiredError):
    """Raised when a persisted session exists but is no longer valid."""


class AuthorizationError(AuthDomainError):
    """Raised when a user lacks permission for a protected action."""
