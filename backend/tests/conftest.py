"""Shared pytest fixtures for backend database and service tests."""

from collections.abc import Iterator
from datetime import timedelta
from itertools import count
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from optimark_athena.app import app
from optimark_athena.config import AuthSettings
from optimark_athena.dependencies import get_auth_settings, get_db_session
from optimark_metis.auth_service import AuthService
from optimark_metis.service import AcademicService
from optimark_mnemosyne.config import create_session_factory
from optimark_mnemosyne.auth_repository import SqlAlchemyAuthRepository
from optimark_mnemosyne.repository import SqlAlchemyAcademicRepository


BACKEND_DIR = Path(__file__).resolve().parents[1]


def make_alembic_config(database_url: str) -> Config:
    """Build an Alembic config targeting a specific database URL.

    Args:
        database_url: Database URL to inject into the Alembic config.

    Returns:
        Config: Configured Alembic configuration object.
    """
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


@pytest.fixture
def sqlite_database_url(tmp_path: Path) -> str:
    """Return a temporary SQLite database URL for tests.

    Args:
        tmp_path: Pytest-provided temporary directory.

    Returns:
        str: SQLite database URL.
    """
    return f"sqlite+pysqlite:///{tmp_path / 'academic.db'}"


@pytest.fixture
def migrated_database(sqlite_database_url: str) -> str:
    """Apply migrations to the temporary test database.

    Args:
        sqlite_database_url: Temporary SQLite database URL.

    Returns:
        str: Migrated database URL.
    """
    command.upgrade(make_alembic_config(sqlite_database_url), "head")
    return sqlite_database_url


@pytest.fixture
def db_session(migrated_database: str) -> Session:
    """Yield a SQLAlchemy session bound to a migrated test database.

    Args:
        migrated_database: Temporary migrated database URL.

    Yields:
        Session: Active SQLAlchemy ORM session.
    """
    session_factory = create_session_factory(migrated_database)
    with session_factory() as session:
        yield session
        session.rollback()


@pytest.fixture
def academic_service(db_session: Session) -> AcademicService:
    """Build an academic service backed by the test session.

    Args:
        db_session: Active SQLAlchemy ORM session.

    Returns:
        AcademicService: Service bound to the repository under test.
    """
    return AcademicService(SqlAlchemyAcademicRepository(db_session))


@pytest.fixture
def auth_service(db_session: Session) -> AuthService:
    """Build an auth service backed by the test session.

    Args:
        db_session: Active SQLAlchemy ORM session.

    Returns:
        AuthService: Auth service bound to the repositories under test.
    """
    token_counter = count()
    return AuthService(
        academic_repository=SqlAlchemyAcademicRepository(db_session),
        auth_repository=SqlAlchemyAuthRepository(db_session),
        password_hasher=PasswordHash.recommended(),
        session_ttl=timedelta(days=14),
        token_generator=lambda: f"test-session-token-{next(token_counter)}",
    )


@pytest.fixture
def migrated_engine(migrated_database: str):
    """Yield a SQLAlchemy engine bound to a migrated test database.

    Args:
        migrated_database: Temporary migrated database URL.

    Yields:
        Engine: SQLAlchemy engine for schema inspection.
    """
    engine = create_engine(migrated_database)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def api_client(db_session: Session) -> Iterator[TestClient]:
    """Yield a test client with database and auth settings overrides.

    Args:
        db_session: Active SQLAlchemy ORM session.

    Yields:
        TestClient: FastAPI test client bound to the shared test session.
    """

    def override_get_db_session() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_auth_settings] = lambda: AuthSettings(
        cookie_name="optimark_session",
        session_ttl=timedelta(days=14),
        cookie_secure=False,
        cookie_same_site="lax",
    )
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
