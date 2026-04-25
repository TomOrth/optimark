"""Application service layer for auth and session operations."""

from collections.abc import Callable
from datetime import datetime, timedelta
import hashlib
import secrets

from pwdlib import PasswordHash

from optimark_metis.academic import User
from optimark_metis.auth import AuthenticatedSession, IssuedSession, utc_now
from optimark_metis.auth_repository import AuthRepository
from optimark_metis.errors import (
    AuthenticationRequiredError,
    DuplicateEmailError,
    InvalidAcademicDataError,
    InvalidCredentialsError,
    PasswordPolicyError,
    SessionExpiredError,
)
from optimark_metis.repository import AcademicRepository


class AuthService:
    """Coordinate signup, login, logout, and session validation."""

    def __init__(
        self,
        *,
        academic_repository: AcademicRepository,
        auth_repository: AuthRepository,
        password_hasher: PasswordHash,
        session_ttl: timedelta,
        token_generator: Callable[[], str] | None = None,
        now_provider: Callable[[], datetime] = utc_now,
    ) -> None:
        """Initialize the auth service.

        Args:
            academic_repository: Repository for user persistence.
            auth_repository: Repository for auth persistence.
            password_hasher: Password hasher and verifier.
            session_ttl: Lifetime for newly issued sessions.
            token_generator: Optional generator for raw session tokens.
            now_provider: Callable used to obtain the current UTC time.

        Raises:
            ValueError: If the configured session lifetime is not positive.
        """
        if session_ttl <= timedelta():
            raise ValueError("session_ttl must be positive")

        self._academic_repository = academic_repository
        self._auth_repository = auth_repository
        self._password_hasher = password_hasher
        self._session_ttl = session_ttl
        self._token_generator = token_generator or _generate_session_token
        self._now_provider = now_provider

    def signup(self, *, email: str, display_name: str, password: str) -> IssuedSession:
        """Create a new password-backed account and initial session.

        Args:
            email: User email address.
            display_name: User-facing display name.
            password: Raw user password.

        Returns:
            IssuedSession: Newly issued authenticated session bundle.

        Raises:
            DuplicateEmailError: If the canonical email already exists.
            PasswordPolicyError: If the password is invalid.
            InvalidAcademicDataError: If required user fields are blank.
        """
        normalized_email = _normalize_required(value=email, field_name="email").lower()
        normalized_display_name = _normalize_required(
            value=display_name,
            field_name="display_name",
        )
        self._validate_password(password)

        if self._academic_repository.get_user_by_email(normalized_email) is not None:
            raise DuplicateEmailError(f"user email {normalized_email} already exists")

        user = self._academic_repository.add_user(
            email=normalized_email,
            display_name=normalized_display_name,
        )
        self._auth_repository.add_password_identity(
            user_id=user.id,
            provider_subject=normalized_email,
            password_hash=self._password_hasher.hash(password),
        )
        return self._issue_session(user)

    def login(self, *, email: str, password: str) -> IssuedSession:
        """Authenticate a password-backed user and issue a new session.

        Args:
            email: User email address.
            password: Raw user password.

        Returns:
            IssuedSession: Newly issued authenticated session bundle.

        Raises:
            InvalidCredentialsError: If the credentials do not match.
            PasswordPolicyError: If the password is blank.
            InvalidAcademicDataError: If the email is blank.
        """
        normalized_email = _normalize_required(value=email, field_name="email").lower()
        if not password.strip():
            raise PasswordPolicyError("password is required")

        authentication = self._auth_repository.get_password_authentication(
            provider_subject=normalized_email,
        )
        if authentication is None or not self._password_hasher.verify(
            password,
            authentication.password_hash,
        ):
            raise InvalidCredentialsError("invalid email or password")

        return self._issue_session(authentication.user)

    def get_session_user(self, *, session_token: str) -> AuthenticatedSession:
        """Resolve and validate an authenticated session from a raw token.

        Args:
            session_token: Raw opaque session token from the client cookie.

        Returns:
            AuthenticatedSession: Authenticated user and current session.

        Raises:
            AuthenticationRequiredError: If the token is missing or invalid.
            SessionExpiredError: If the session exists but has expired.
        """
        token_hash = _hash_session_token(session_token)
        authentication = self._auth_repository.get_authenticated_session_by_token_hash(
            token_hash=token_hash,
        )
        if authentication is None:
            raise AuthenticationRequiredError("authentication is required")

        now = self._now_provider()
        session = authentication.session
        if session.revoked_at is not None:
            raise AuthenticationRequiredError("authentication is required")
        if session.expires_at <= now:
            self._auth_repository.revoke_session(
                session_id=session.id,
                revoked_at=now,
            )
            raise SessionExpiredError("session has expired")

        touched_session = self._auth_repository.touch_session(
            session_id=session.id,
            last_seen_at=now,
        )
        return AuthenticatedSession(
            user=authentication.user,
            session=touched_session,
        )

    def logout(self, *, session_token: str | None) -> None:
        """Revoke a session if it exists.

        Args:
            session_token: Raw opaque session token from the client cookie.
        """
        if session_token is None or not session_token.strip():
            return

        authentication = self._auth_repository.get_authenticated_session_by_token_hash(
            token_hash=_hash_session_token(session_token),
        )
        if authentication is None or authentication.session.revoked_at is not None:
            return

        self._auth_repository.revoke_session(
            session_id=authentication.session.id,
            revoked_at=self._now_provider(),
        )

    def _issue_session(self, user: User) -> IssuedSession:
        """Issue a new session for a user.

        Args:
            user: Authenticated user receiving the session.

        Returns:
            IssuedSession: Newly issued authenticated session bundle.
        """
        created_at = self._now_provider()
        token = self._token_generator()
        session = self._auth_repository.add_session(
            user_id=user.id,
            token_hash=_hash_session_token(token),
            created_at=created_at,
            expires_at=created_at + self._session_ttl,
        )
        return IssuedSession(
            authentication=AuthenticatedSession(user=user, session=session),
            token=token,
        )

    @staticmethod
    def _validate_password(password: str) -> None:
        """Validate a raw password against the baseline policy.

        Args:
            password: Raw password to validate.

        Raises:
            PasswordPolicyError: If the password is blank or too short.
        """
        if not password.strip():
            raise PasswordPolicyError("password is required")
        if len(password) < 12:
            raise PasswordPolicyError("password must be at least 12 characters")


def _normalize_required(*, value: str, field_name: str) -> str:
    """Normalize and validate a required string field.

    Args:
        value: Raw string value to normalize.
        field_name: Field name used in the error message.

    Returns:
        str: Stripped string value.

    Raises:
        InvalidAcademicDataError: If the value is blank after trimming.
    """
    normalized = value.strip()
    if not normalized:
        raise InvalidAcademicDataError(f"{field_name} is required")
    return normalized


def _hash_session_token(session_token: str) -> str:
    """Return the SHA-256 digest for a raw session token.

    Args:
        session_token: Raw session token to hash.

    Returns:
        str: Hex-encoded token digest.

    Raises:
        AuthenticationRequiredError: If the token is blank.
    """
    normalized = session_token.strip()
    if not normalized:
        raise AuthenticationRequiredError("authentication is required")
    return hashlib.sha256(normalized.encode("utf-8"), usedforsecurity=True).hexdigest()


def _generate_session_token() -> str:
    """Generate a new opaque session token.

    Returns:
        str: URL-safe session token.
    """
    return secrets.token_urlsafe(32)
