"""SQLAlchemy-backed repository implementations for auth data."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from optimark_metis.academic import User
from optimark_metis.auth import (
    AuthIdentity,
    AuthProvider,
    AuthSession,
    AuthenticatedSession,
    PasswordAuthentication,
)
from optimark_metis.errors import DuplicateEmailError
from optimark_mnemosyne.models import (
    AuthIdentityModel,
    AuthSessionModel,
    PasswordCredentialModel,
    UserModel,
)


class SqlAlchemyAuthRepository:
    """Persist and query auth entities through SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with an active SQLAlchemy session.

        Args:
            session: Active ORM session used for persistence operations.
        """
        self._session = session

    def add_password_identity(
        self,
        *,
        user_id: UUID,
        provider_subject: str,
        password_hash: str,
    ) -> AuthIdentity:
        """Insert a password identity and credential.

        Args:
            user_id: Related user identifier.
            provider_subject: Canonical email used as the provider subject.
            password_hash: Persisted password hash.

        Returns:
            AuthIdentity: Persisted auth identity.

        Raises:
            DuplicateEmailError: If a password identity already exists for the email.
        """
        identity = AuthIdentityModel(
            user_id=user_id,
            provider=AuthProvider.PASSWORD,
            provider_subject=provider_subject,
        )
        credential = PasswordCredentialModel(
            user_id=user_id,
            password_hash=password_hash,
        )
        self._session.add(identity)
        self._session.add(credential)
        try:
            self._session.flush()
        except IntegrityError as exc:
            if _is_duplicate_identity_integrity_error(exc):
                raise DuplicateEmailError(
                    f"user email {provider_subject} already exists",
                ) from exc
            raise
        return _auth_identity_from_model(identity)

    def get_password_authentication(
        self,
        *,
        provider_subject: str,
    ) -> PasswordAuthentication | None:
        """Fetch password-authentication material for a subject.

        Args:
            provider_subject: Canonical provider subject to look up.

        Returns:
            PasswordAuthentication | None: Resolved login material when present.
        """
        statement = (
            select(UserModel, PasswordCredentialModel.password_hash)
            .join(AuthIdentityModel, AuthIdentityModel.user_id == UserModel.id)
            .join(
                PasswordCredentialModel,
                PasswordCredentialModel.user_id == UserModel.id,
            )
            .where(
                AuthIdentityModel.provider == AuthProvider.PASSWORD,
                AuthIdentityModel.provider_subject == provider_subject,
            )
        )
        row = self._session.execute(statement).one_or_none()
        if row is None:
            return None

        user_model, password_hash = row
        return PasswordAuthentication(
            user=_user_from_model(user_model),
            password_hash=password_hash,
        )

    def add_session(
        self,
        *,
        user_id: UUID,
        token_hash: str,
        created_at: datetime,
        expires_at: datetime,
    ) -> AuthSession:
        """Insert a new auth session.

        Args:
            user_id: Related user identifier.
            token_hash: SHA-256 hash of the raw session token.
            created_at: Session creation timestamp.
            expires_at: Session expiry timestamp.

        Returns:
            AuthSession: Persisted auth session.
        """
        model = AuthSessionModel(
            user_id=user_id,
            token_hash=token_hash,
            created_at=created_at,
            last_seen_at=created_at,
            expires_at=expires_at,
        )
        self._session.add(model)
        self._session.flush()
        return _auth_session_from_model(model)

    def get_authenticated_session_by_token_hash(
        self,
        *,
        token_hash: str,
    ) -> AuthenticatedSession | None:
        """Fetch an authenticated session context by hashed token.

        Args:
            token_hash: SHA-256 hash of the raw session token.

        Returns:
            AuthenticatedSession | None: Authenticated session context when present.
        """
        statement = (
            select(UserModel, AuthSessionModel)
            .join(AuthSessionModel, AuthSessionModel.user_id == UserModel.id)
            .where(AuthSessionModel.token_hash == token_hash)
        )
        row = self._session.execute(statement).one_or_none()
        if row is None:
            return None

        user_model, session_model = row
        return AuthenticatedSession(
            user=_user_from_model(user_model),
            session=_auth_session_from_model(session_model),
        )

    def touch_session(
        self,
        *,
        session_id: UUID,
        last_seen_at: datetime,
    ) -> AuthSession:
        """Update a session last-seen timestamp.

        Args:
            session_id: Session identifier to update.
            last_seen_at: Timestamp to persist.

        Returns:
            AuthSession: Updated session entity.
        """
        model = self._session.get(AuthSessionModel, session_id)
        if model is None:
            raise LookupError(f"session {session_id} was not found")

        model.last_seen_at = last_seen_at
        self._session.flush()
        return _auth_session_from_model(model)

    def revoke_session(
        self,
        *,
        session_id: UUID,
        revoked_at: datetime,
    ) -> AuthSession:
        """Revoke a persisted session.

        Args:
            session_id: Session identifier to revoke.
            revoked_at: Timestamp to persist.

        Returns:
            AuthSession: Revoked session entity.
        """
        model = self._session.get(AuthSessionModel, session_id)
        if model is None:
            raise LookupError(f"session {session_id} was not found")

        model.revoked_at = revoked_at
        self._session.flush()
        return _auth_session_from_model(model)

    def get_identity(
        self,
        *,
        provider: AuthProvider,
        provider_subject: str,
    ) -> AuthIdentity | None:
        """Fetch an identity link by provider and subject.

        Args:
            provider: Auth provider to resolve.
            provider_subject: Provider subject to resolve.

        Returns:
            AuthIdentity | None: Matching identity link when present.
        """
        statement = select(AuthIdentityModel).where(
            AuthIdentityModel.provider == provider,
            AuthIdentityModel.provider_subject == provider_subject,
        )
        model = self._session.scalar(statement)
        if model is None:
            return None
        return _auth_identity_from_model(model)


def _auth_identity_from_model(model: AuthIdentityModel) -> AuthIdentity:
    """Convert an auth identity ORM model into a domain entity.

    Args:
        model: ORM auth identity model instance.

    Returns:
        AuthIdentity: Domain auth identity entity.
    """
    return AuthIdentity(
        id=model.id,
        user_id=model.user_id,
        provider=model.provider,
        provider_subject=model.provider_subject,
        created_at=_coerce_utc(model.created_at),
    )


def _auth_session_from_model(model: AuthSessionModel) -> AuthSession:
    """Convert an auth session ORM model into a domain entity.

    Args:
        model: ORM auth session model instance.

    Returns:
        AuthSession: Domain auth session entity.
    """
    return AuthSession(
        id=model.id,
        user_id=model.user_id,
        created_at=_coerce_utc(model.created_at),
        last_seen_at=_coerce_utc(model.last_seen_at),
        expires_at=_coerce_utc(model.expires_at),
        revoked_at=(
            None if model.revoked_at is None else _coerce_utc(model.revoked_at)
        ),
    )


def _user_from_model(model: UserModel) -> User:
    """Convert a user ORM model into a domain user.

    Args:
        model: ORM user model instance.

    Returns:
        User: Domain user entity.
    """
    return User(
        id=model.id,
        email=model.email,
        display_name=model.display_name,
        created_at=_coerce_utc(model.created_at),
        updated_at=_coerce_utc(model.updated_at),
    )


def _coerce_utc(value: datetime) -> datetime:
    """Normalize timestamps to timezone-aware UTC values.

    Args:
        value: Timestamp returned by the ORM or database driver.

    Returns:
        datetime: Timezone-aware UTC timestamp.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _is_duplicate_identity_integrity_error(error: IntegrityError) -> bool:
    """Return whether an integrity error represents a duplicate password identity.

    Args:
        error: Integrity error raised by SQLAlchemy during flush.

    Returns:
        bool: True when the error matches the auth-identity uniqueness constraint.
    """
    message = str(error.orig)
    return (
        "uq_auth_identities_provider_subject" in message
        or "auth_identities.provider" in message
        or "auth_identities.provider_subject" in message
        or (
            "UNIQUE constraint failed:" in message
            and "auth_identities.provider" in message
            and "auth_identities.provider_subject" in message
        )
    )
