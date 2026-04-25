"""Tests for Athena auth configuration defaults."""

import pytest

from optimark_athena.config import load_auth_settings


def test_load_auth_settings_defaults_to_secure_cookie(monkeypatch) -> None:
    """Verify session cookies are secure by default when env overrides are absent.

    Args:
        monkeypatch: Pytest fixture used to control environment variables.
    """
    monkeypatch.delenv("BACKEND_AUTH_SESSION_COOKIE_NAME", raising=False)
    monkeypatch.delenv("BACKEND_AUTH_SESSION_TTL_DAYS", raising=False)
    monkeypatch.delenv("BACKEND_AUTH_SESSION_COOKIE_SECURE", raising=False)
    monkeypatch.delenv("BACKEND_AUTH_SESSION_COOKIE_SAME_SITE", raising=False)

    settings = load_auth_settings()

    assert settings.cookie_secure is True


def test_load_auth_settings_honors_explicit_insecure_local_override(
    monkeypatch,
) -> None:
    """Verify operators can explicitly disable secure cookies for local HTTP dev.

    Args:
        monkeypatch: Pytest fixture used to control environment variables.
    """
    monkeypatch.setenv("BACKEND_AUTH_SESSION_COOKIE_SECURE", "false")

    settings = load_auth_settings()

    assert settings.cookie_secure is False


def test_load_auth_settings_rejects_non_integer_ttl(monkeypatch) -> None:
    """Verify non-integer TTL values raise a clear validation error.

    Args:
        monkeypatch: Pytest fixture used to control environment variables.
    """
    monkeypatch.setenv("BACKEND_AUTH_SESSION_TTL_DAYS", "abc")

    with pytest.raises(
        ValueError,
        match="BACKEND_AUTH_SESSION_TTL_DAYS must be an integer, got 'abc'",
    ):
        load_auth_settings()
