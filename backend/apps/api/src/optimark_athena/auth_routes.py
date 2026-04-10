"""Auth API routes for signup, login, logout, and session restoration."""

from datetime import datetime
from email.utils import format_datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from optimark_athena.config import AuthSettings
from optimark_athena.dependencies import (
    get_auth_service,
    get_auth_settings,
    require_authenticated_session,
)
from optimark_clio.auth import (
    AuthErrorResponse,
    LoginRequest,
    SessionResponse,
    SignupRequest,
)
from optimark_metis import (
    AuthService,
    DuplicateEmailError,
    InvalidAcademicDataError,
    InvalidCredentialsError,
    PasswordPolicyError,
)


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": AuthErrorResponse},
        status.HTTP_409_CONFLICT: {"model": AuthErrorResponse},
    },
)
def signup(
    payload: SignupRequest,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
) -> SessionResponse:
    """Create a user account and issue the initial authenticated session.

    Args:
        payload: Signup request payload.
        response: HTTP response used to set the session cookie.
        auth_service: Auth service used to create the account.
        auth_settings: Resolved auth settings.

    Returns:
        SessionResponse: Authenticated session payload.

    Raises:
        HTTPException: If the request payload is invalid or the email already exists.
    """
    try:
        issued_session = auth_service.signup(
            email=payload.email,
            display_name=payload.display_name,
            password=payload.password,
        )
    except (InvalidAcademicDataError, PasswordPolicyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except DuplicateEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    _set_session_cookie(
        response=response,
        session_token=issued_session.token,
        expires_at=issued_session.authentication.session.expires_at,
        auth_settings=auth_settings,
    )
    return SessionResponse.from_authenticated_session(issued_session.authentication)


@router.post(
    "/login",
    response_model=SessionResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": AuthErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": AuthErrorResponse},
    },
)
def login(
    payload: LoginRequest,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
) -> SessionResponse:
    """Authenticate a user and issue a new session cookie.

    Args:
        payload: Login request payload.
        response: HTTP response used to set the session cookie.
        auth_service: Auth service used to validate credentials.
        auth_settings: Resolved auth settings.

    Returns:
        SessionResponse: Authenticated session payload.

    Raises:
        HTTPException: If the login request is invalid or unauthorized.
    """
    try:
        issued_session = auth_service.login(
            email=payload.email,
            password=payload.password,
        )
    except PasswordPolicyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except InvalidAcademicDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    _set_session_cookie(
        response=response,
        session_token=issued_session.token,
        expires_at=issued_session.authentication.session.expires_at,
        auth_settings=auth_settings,
    )
    return SessionResponse.from_authenticated_session(issued_session.authentication)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
) -> Response:
    """Revoke the current session and clear the session cookie.

    Args:
        request: Current HTTP request.
        auth_service: Auth service used to revoke the session.
        auth_settings: Resolved auth settings.

    Returns:
        Response: Empty successful response.
    """
    auth_service.logout(session_token=request.cookies.get(auth_settings.cookie_name))
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    _clear_session_cookie(response=response, auth_settings=auth_settings)
    return response


@router.get(
    "/session",
    response_model=SessionResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": AuthErrorResponse},
    },
)
def get_session(
    authentication=Depends(require_authenticated_session),
) -> SessionResponse:
    """Return the current authenticated session payload.

    Args:
        authentication: Resolved authenticated session context.

    Returns:
        SessionResponse: Authenticated session payload.
    """
    return SessionResponse.from_authenticated_session(authentication)


def _set_session_cookie(
    *,
    response: Response,
    session_token: str,
    expires_at: datetime,
    auth_settings: AuthSettings,
) -> None:
    """Set the opaque session cookie on a response.

    Args:
        response: HTTP response to mutate.
        session_token: Raw opaque session token.
        expires_at: Absolute session-expiry timestamp.
        auth_settings: Resolved auth settings.
    """
    response.set_cookie(
        key=auth_settings.cookie_name,
        value=session_token,
        httponly=True,
        secure=auth_settings.cookie_secure,
        samesite=auth_settings.cookie_same_site,
        max_age=int(auth_settings.session_ttl.total_seconds()),
        expires=format_datetime(expires_at),
        path="/",
    )


def _clear_session_cookie(*, response: Response, auth_settings: AuthSettings) -> None:
    """Clear the opaque session cookie from a response.

    Args:
        response: HTTP response to mutate.
        auth_settings: Resolved auth settings.
    """
    response.delete_cookie(
        key=auth_settings.cookie_name,
        httponly=True,
        secure=auth_settings.cookie_secure,
        samesite=auth_settings.cookie_same_site,
        path="/",
    )
