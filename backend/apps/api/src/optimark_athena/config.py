"""Configuration helpers for Athena auth and session behavior."""

from dataclasses import dataclass
from datetime import timedelta
import os
from typing import Literal


DEFAULT_AUTH_SESSION_COOKIE_NAME = "optimark_session"
DEFAULT_AUTH_SESSION_TTL_DAYS = 14
DEFAULT_AUTH_SESSION_COOKIE_SECURE = True
DEFAULT_AUTH_SESSION_COOKIE_SAME_SITE = "lax"

_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


@dataclass(frozen=True)
class AuthSettings:
    """Resolved Athena auth settings.

    Attributes:
        cookie_name: Name of the opaque session cookie.
        session_ttl: Lifetime for newly issued sessions.
        cookie_secure: Whether the session cookie should require HTTPS.
        cookie_same_site: SameSite policy for the session cookie.
    """

    cookie_name: str
    session_ttl: timedelta
    cookie_secure: bool
    cookie_same_site: Literal["lax", "strict", "none"]


def load_auth_settings() -> AuthSettings:
    """Resolve auth settings from environment variables.

    Returns:
        AuthSettings: Resolved auth settings for the API application.
    """
    return AuthSettings(
        cookie_name=os.environ.get(
            "BACKEND_AUTH_SESSION_COOKIE_NAME",
            DEFAULT_AUTH_SESSION_COOKIE_NAME,
        ),
        session_ttl=timedelta(
            days=_get_positive_int_env(
                "BACKEND_AUTH_SESSION_TTL_DAYS",
                DEFAULT_AUTH_SESSION_TTL_DAYS,
            ),
        ),
        cookie_secure=_get_bool_env(
            "BACKEND_AUTH_SESSION_COOKIE_SECURE",
            DEFAULT_AUTH_SESSION_COOKIE_SECURE,
        ),
        cookie_same_site=_get_same_site_env(
            "BACKEND_AUTH_SESSION_COOKIE_SAME_SITE",
            DEFAULT_AUTH_SESSION_COOKIE_SAME_SITE,
        ),
    )


def _get_positive_int_env(name: str, default: int) -> int:
    """Return a positive integer environment variable.

    Args:
        name: Environment-variable name.
        default: Default value when unset.

    Returns:
        int: Positive integer value.

    Raises:
        ValueError: If the configured value is not a positive integer.
    """
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default

    value = int(raw_value)
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def _get_bool_env(name: str, default: bool) -> bool:
    """Return a boolean environment variable.

    Args:
        name: Environment-variable name.
        default: Default value when unset.

    Returns:
        bool: Parsed boolean value.

    Raises:
        ValueError: If the configured value is not a recognized boolean.
    """
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default

    normalized = raw_value.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    raise ValueError(f"{name} must be a boolean value")


def _get_same_site_env(
    name: str,
    default: Literal["lax", "strict", "none"],
) -> Literal["lax", "strict", "none"]:
    """Return a SameSite environment variable.

    Args:
        name: Environment-variable name.
        default: Default value when unset.

    Returns:
        Literal["lax", "strict", "none"]: Parsed SameSite value.

    Raises:
        ValueError: If the configured value is not supported.
    """
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default

    normalized = raw_value.strip().lower()
    if normalized not in {"lax", "strict", "none"}:
        raise ValueError(f"{name} must be one of: lax, strict, none")
    return normalized
