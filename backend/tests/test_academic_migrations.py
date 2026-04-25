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
    """Verify the migration creates the expected tables, constraints, and indexes."""
    inspector = inspect(migrated_engine)

    assert set(inspector.get_table_names()) >= {
        "users",
        "courses",
        "enrollments",
        "assignments",
        "assignment_versions",
        "submissions",
        "evaluation_records",
        "grade_records",
        "auth_identities",
        "password_credentials",
        "auth_sessions",
    }

    user_unique_constraints = inspector.get_unique_constraints("users")
    assert {
        tuple(constraint["column_names"])
        for constraint in user_unique_constraints
    } >= {("email",)}

    unique_constraints = inspector.get_unique_constraints("enrollments")
    assert {
        tuple(sorted(constraint["column_names"]))
        for constraint in unique_constraints
    } >= {("course_id", "user_id")}

    indexes = inspector.get_indexes("enrollments")
    assert {
        (index["name"], tuple(index["column_names"]))
        for index in indexes
    } >= {("ix_enrollments_user_id", ("user_id",))}

    assignment_indexes = inspector.get_indexes("assignments")
    assert {
        (index["name"], tuple(index["column_names"]))
        for index in assignment_indexes
    } >= {("ix_assignments_course_id", ("course_id",))}

    assignment_version_unique_constraints = inspector.get_unique_constraints(
        "assignment_versions",
    )
    assert {
        tuple(constraint["column_names"])
        for constraint in assignment_version_unique_constraints
    } >= {("assignment_id", "version_number")}

    submission_indexes = inspector.get_indexes("submissions")
    assert {
        (index["name"], tuple(index["column_names"]))
        for index in submission_indexes
    } >= {
        ("ix_submissions_assignment_id", ("assignment_id",)),
        ("ix_submissions_assignment_version_id", ("assignment_version_id",)),
        ("ix_submissions_student_user_id", ("student_user_id",)),
    }

    evaluation_indexes = inspector.get_indexes("evaluation_records")
    assert {
        (index["name"], tuple(index["column_names"]))
        for index in evaluation_indexes
    } >= {
        ("ix_evaluation_records_assignment_version_id", ("assignment_version_id",)),
        ("ix_evaluation_records_submission_id", ("submission_id",)),
    }

    grade_indexes = inspector.get_indexes("grade_records")
    assert {
        (index["name"], tuple(index["column_names"]))
        for index in grade_indexes
    } >= {
        ("ix_grade_records_submission_id", ("submission_id",)),
        ("ix_grade_records_student_user_id", ("student_user_id",)),
        ("ix_grade_records_grader_user_id", ("grader_user_id",)),
    }

    identity_unique_constraints = inspector.get_unique_constraints("auth_identities")
    assert {
        tuple(constraint["column_names"])
        for constraint in identity_unique_constraints
    } >= {("provider", "provider_subject")}

    identity_indexes = inspector.get_indexes("auth_identities")
    assert {
        (index["name"], tuple(index["column_names"]))
        for index in identity_indexes
    } >= {("ix_auth_identities_user_id", ("user_id",))}

    session_indexes = inspector.get_indexes("auth_sessions")
    assert {
        (index["name"], tuple(index["column_names"]), index["unique"])
        for index in session_indexes
    } >= {
        ("ix_auth_sessions_token_hash", ("token_hash",), True),
        ("ix_auth_sessions_user_id", ("user_id",), False),
    }


def test_alembic_upgrade_to_head_succeeds(sqlite_database_url: str) -> None:
    """Verify a fresh database can be migrated to the latest revision."""
    config = make_alembic_config(sqlite_database_url)

    command.upgrade(config, "head")
