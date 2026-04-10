"""Pydantic contracts for auth and session APIs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from optimark_metis.academic import User
from optimark_metis.auth import AuthProvider, AuthenticatedSession


class SignupRequest(BaseModel):
    """Input payload for user signup."""

    email: str
    display_name: str
    password: str


class LoginRequest(BaseModel):
    """Input payload for user login."""

    email: str
    password: str


class SessionUser(BaseModel):
    """Serialized authenticated-user payload.

    Attributes:
        id: Stable user identifier.
        email: Canonical user email address.
        display_name: User-facing display name.
    """

    id: UUID
    email: str
    display_name: str

    @classmethod
    def from_domain(cls, user: User) -> "SessionUser":
        """Build a session user contract from a domain user.

        Args:
            user: Domain user entity to serialize.

        Returns:
            SessionUser: Serialized authenticated-user payload.
        """
        return cls(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
        )


class SessionResponse(BaseModel):
    """Serialized session response payload.

    Attributes:
        user: Authenticated user payload.
        provider: Auth provider used for the session.
        expires_at: Time when the current session expires.
    """

    user: SessionUser
    provider: AuthProvider
    expires_at: datetime

    @classmethod
    def from_authenticated_session(
        cls,
        authentication: AuthenticatedSession,
    ) -> "SessionResponse":
        """Build a session response from an authenticated session context.

        Args:
            authentication: Authenticated session context to serialize.

        Returns:
            SessionResponse: Serialized session response payload.
        """
        return cls(
            user=SessionUser.from_domain(authentication.user),
            provider=AuthProvider.PASSWORD,
            expires_at=authentication.session.expires_at,
        )


class AuthErrorResponse(BaseModel):
    """Serialized auth error payload."""

    detail: str
