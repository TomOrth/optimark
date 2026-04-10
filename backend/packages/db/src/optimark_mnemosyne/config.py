"""Database configuration helpers for the Mnemosyne package."""

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker


DEFAULT_DATABASE_URL = "postgresql+psycopg://optimark:optimark@localhost:5432/optimark"


def get_database_url() -> str:
    """Resolve the configured backend database URL.

    Returns:
        str: The configured database URL, falling back to the local development
            default when the environment variable is unset.
    """
    return os.environ.get("BACKEND_DATABASE_URL", DEFAULT_DATABASE_URL)


def create_db_engine(database_url: str | None = None) -> Engine:
    """Create a SQLAlchemy engine for the configured database.

    Args:
        database_url: Optional database URL override.

    Returns:
        Engine: A SQLAlchemy engine configured for the target dialect.
    """
    resolved_database_url = database_url or get_database_url()
    connect_args: dict[str, object] = {}
    if resolved_database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(
        resolved_database_url,
        future=True,
        pool_pre_ping=not resolved_database_url.startswith("sqlite"),
        connect_args=connect_args,
    )


def create_session_factory(
    database_url: str | None = None,
) -> sessionmaker:
    """Create a session factory bound to the configured engine.

    Args:
        database_url: Optional database URL override.

    Returns:
        sessionmaker: Session factory for ORM work.
    """
    return sessionmaker(
        bind=create_db_engine(database_url),
        autoflush=False,
        expire_on_commit=False,
    )
