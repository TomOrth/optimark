"""Repository protocol definitions for auth persistence."""

from datetime import datetime
from typing import Protocol
from uuid import UUID

from optimark_metis.auth import (
    AuthIdentity,
    AuthProvider,
    AuthSession,
    AuthenticatedSession,
    PasswordAuthentication,
)


class AuthRepository(Protocol):
    """Protocol describing persistence operations for auth data."""

    def add_password_identity(
        self,
        *,
        user_id: UUID,
        provider_subject: str,
        password_hash: str,
    ) -> AuthIdentity:
        """Persist a password-backed auth identity."""

    def get_password_authentication(
        self,
        *,
        provider_subject: str,
    ) -> PasswordAuthentication | None:
        """Fetch password-authentication material for a canonical subject."""

    def add_session(
        self,
        *,
        user_id: UUID,
        token_hash: str,
        created_at: datetime,
        expires_at: datetime,
    ) -> AuthSession:
        """Persist a new auth session."""

    def get_authenticated_session_by_token_hash(
        self,
        *,
        token_hash: str,
    ) -> AuthenticatedSession | None:
        """Fetch an authenticated session context by hashed token."""

    def touch_session(
        self,
        *,
        session_id: UUID,
        last_seen_at: datetime,
    ) -> AuthSession:
        """Update a session last-seen timestamp."""

    def revoke_session(
        self,
        *,
        session_id: UUID,
        revoked_at: datetime,
    ) -> AuthSession:
        """Revoke a persisted session."""

    def get_identity(
        self,
        *,
        provider: AuthProvider,
        provider_subject: str,
    ) -> AuthIdentity | None:
        """Fetch an auth identity link by provider and subject."""
