"""Auth and authorization domain entities for Optimark."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from optimark_metis.academic import User


def utc_now() -> datetime:
    """Return the current UTC timestamp.

    Returns:
        datetime: Timezone-aware UTC timestamp.
    """
    return datetime.now(UTC)


class AuthProvider(StrEnum):
    """Supported identity-provider values."""

    PASSWORD = "password"


class CourseCapability(StrEnum):
    """Permission capabilities enforced for course-scoped actions."""

    MANAGE_COURSE = "manage_course"
    GRADE_SUBMISSIONS = "grade_submissions"
    SUBMIT_WORK = "submit_work"


@dataclass(frozen=True)
class AuthIdentity:
    """Immutable domain representation of an auth identity link.

    Attributes:
        id: Stable identity-link identifier.
        user_id: Related user identifier.
        provider: Auth provider type.
        provider_subject: Provider-specific stable subject value.
        created_at: Time when the identity link was created.
    """

    id: UUID
    user_id: UUID
    provider: AuthProvider
    provider_subject: str
    created_at: datetime


@dataclass(frozen=True)
class PasswordAuthentication:
    """Login material resolved for password authentication.

    Attributes:
        user: User matched to the credential.
        password_hash: Persisted password hash for verification.
    """

    user: User
    password_hash: str


@dataclass(frozen=True)
class AuthSession:
    """Immutable domain representation of an issued auth session.

    Attributes:
        id: Stable session identifier.
        user_id: Related user identifier.
        created_at: Time when the session was created.
        last_seen_at: Last authenticated access time for the session.
        expires_at: Time when the session becomes invalid.
        revoked_at: Time when the session was revoked, if any.
    """

    id: UUID
    user_id: UUID
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime
    revoked_at: datetime | None


@dataclass(frozen=True)
class AuthenticatedSession:
    """Authenticated session context containing the user and session.

    Attributes:
        user: Authenticated platform user.
        session: Active or resolved session metadata.
    """

    user: User
    session: AuthSession


@dataclass(frozen=True)
class IssuedSession:
    """Newly issued session bundle including the raw cookie token.

    Attributes:
        authentication: Authenticated session context.
        token: Raw opaque session token to place in the session cookie.
    """

    authentication: AuthenticatedSession
    token: str
