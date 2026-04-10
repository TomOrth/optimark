"""Migration tests for the academic domain foundation."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect


def make_alembic_config(database_url: str) -> Config:
    """Build an Alembic config targeting a specific database URL.

    Args:
        database_url: Database URL to inject into the Alembic config.

    Returns:
        Config: Configured Alembic configuration object.
    """
    backend_dir = Path(__file__).resolve().parents[1]
    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("script_location", str(backend_dir / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def test_migrations_create_academic_tables_and_constraints(migrated_engine) -> None:
    """Verify the migration creates the expected tables and uniqueness rules."""
    inspector = inspect(migrated_engine)

    assert set(inspector.get_table_names()) >= {"users", "courses", "enrollments"}

    unique_constraints = inspector.get_unique_constraints("enrollments")
    assert {
        tuple(sorted(constraint["column_names"]))
        for constraint in unique_constraints
    } >= {("course_id", "user_id")}


def test_alembic_upgrade_to_head_succeeds(sqlite_database_url: str) -> None:
    """Verify a fresh database can be migrated to the latest revision."""
    config = make_alembic_config(sqlite_database_url)

    command.upgrade(config, "head")
