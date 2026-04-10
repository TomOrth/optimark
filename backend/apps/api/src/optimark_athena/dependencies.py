"""FastAPI dependencies for Athena auth, sessions, and authorization."""

from collections.abc import Generator
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from pwdlib import PasswordHash
from sqlalchemy.orm import Session, sessionmaker

from optimark_athena.config import AuthSettings, load_auth_settings
from optimark_metis import (
    AcademicService,
    AuthService,
    AuthenticationRequiredError,
    AuthorizationService,
    CourseCapability,
    EntityNotFoundError,
    SessionExpiredError,
)
from optimark_metis.academic import User
from optimark_metis.auth import AuthenticatedSession
from optimark_mnemosyne import (
    SqlAlchemyAcademicRepository,
    SqlAlchemyAuthRepository,
    create_session_factory,
)


@lru_cache
def get_auth_settings() -> AuthSettings:
    """Return cached auth settings for the API process.

    Returns:
        AuthSettings: Resolved auth settings.
    """
    return load_auth_settings()


@lru_cache
def get_session_factory() -> sessionmaker:
    """Return a cached SQLAlchemy session factory.

    Returns:
        sessionmaker: Session factory bound to the configured database.
    """
    return create_session_factory()


@lru_cache
def get_password_hasher() -> PasswordHash:
    """Return the password hasher used for signup and login.

    Returns:
        PasswordHash: Recommended password hasher instance.
    """
    return PasswordHash.recommended()


def get_db_session(
    session_factory: Annotated[sessionmaker, Depends(get_session_factory)],
) -> Generator[Session, None, None]:
    """Yield a request-scoped SQLAlchemy session.

    Args:
        session_factory: Factory used to create ORM sessions.

    Yields:
        Session: Active SQLAlchemy session.
    """
    with session_factory() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


def get_academic_service(
    db_session: Annotated[Session, Depends(get_db_session)],
) -> AcademicService:
    """Build the academic service for the current request.

    Args:
        db_session: Request-scoped SQLAlchemy session.

    Returns:
        AcademicService: Academic service backed by SQLAlchemy repositories.
    """
    return AcademicService(SqlAlchemyAcademicRepository(db_session))


def get_auth_service(
    db_session: Annotated[Session, Depends(get_db_session)],
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    password_hasher: Annotated[PasswordHash, Depends(get_password_hasher)],
) -> AuthService:
    """Build the auth service for the current request.

    Args:
        db_session: Request-scoped SQLAlchemy session.
        auth_settings: Resolved auth settings.
        password_hasher: Password hasher used for credentials.

    Returns:
        AuthService: Auth service backed by SQLAlchemy repositories.
    """
    return AuthService(
        academic_repository=SqlAlchemyAcademicRepository(db_session),
        auth_repository=SqlAlchemyAuthRepository(db_session),
        password_hasher=password_hasher,
        session_ttl=auth_settings.session_ttl,
    )


def get_authorization_service(
    academic_service: Annotated[AcademicService, Depends(get_academic_service)],
) -> AuthorizationService:
    """Build the authorization service for the current request.

    Args:
        academic_service: Academic service used to resolve enrollments.

    Returns:
        AuthorizationService: Course-capability authorization service.
    """
    return AuthorizationService(academic_service)


def require_authenticated_session(
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
) -> AuthenticatedSession:
    """Require a valid authenticated session.

    Args:
        request: Current HTTP request.
        auth_service: Auth service used to validate the session.
        auth_settings: Resolved auth settings.

    Returns:
        AuthenticatedSession: Authenticated session context.

    Raises:
        HTTPException: If no valid session is present.
    """
    session_token = request.cookies.get(auth_settings.cookie_name)
    try:
        return auth_service.get_session_user(session_token=session_token or "")
    except (AuthenticationRequiredError, SessionExpiredError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


def require_authenticated_user(
    authentication: Annotated[
        AuthenticatedSession,
        Depends(require_authenticated_session),
    ],
) -> User:
    """Require and return the authenticated user.

    Args:
        authentication: Resolved authenticated session context.

    Returns:
        User: Authenticated platform user.
    """
    return authentication.user


def require_course_capability(capability: CourseCapability):
    """Build a dependency that enforces a course-scoped capability.

    Args:
        capability: Required course capability.

    Returns:
        Callable: FastAPI dependency that raises 403 on insufficient access.
    """

    def dependency(
        course_id: UUID,
        authentication: Annotated[
            AuthenticatedSession,
            Depends(require_authenticated_session),
        ],
        authorization_service: Annotated[
            AuthorizationService,
            Depends(get_authorization_service),
        ],
    ) -> AuthenticatedSession:
        """Enforce the required course capability for the authenticated user.

        Args:
            course_id: Course identifier from the route path.
            authentication: Resolved authenticated session context.
            authorization_service: Authorization service used for capability checks.

        Returns:
            AuthenticatedSession: Authenticated session context for downstream use.

        Raises:
            HTTPException: If the course is missing or the user lacks permission.
        """
        try:
            has_access = authorization_service.user_has_course_capability(
                course_id=course_id,
                user_id=authentication.user.id,
                capability=capability,
            )
        except EntityNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc

        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{capability.value} access is required",
            )
        return authentication

    return dependency
