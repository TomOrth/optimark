"""Add generic assessment domain tables.

Revision ID: 20260424_0004
Revises: 20260410_0003
Create Date: 2026-04-24 00:04:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260424_0004"
down_revision: str | None = "20260410_0003"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


assignment_type = sa.Enum(
    "coding",
    "document",
    "quiz",
    name="assignment_type",
    native_enum=False,
)

assignment_publish_state = sa.Enum(
    "draft",
    "published",
    "archived",
    name="assignment_publish_state",
    native_enum=False,
)

submission_state = sa.Enum(
    "draft",
    "submitted",
    "withdrawn",
    name="submission_state",
    native_enum=False,
)

evaluation_kind = sa.Enum(
    "automated",
    "manual",
    name="evaluation_kind",
    native_enum=False,
)

evaluation_status = sa.Enum(
    "queued",
    "running",
    "succeeded",
    "failed",
    "cancelled",
    name="evaluation_status",
    native_enum=False,
)

grade_state = sa.Enum(
    "provisional",
    "released",
    "superseded",
    name="grade_state",
    native_enum=False,
)


def upgrade() -> None:
    """Create assessment tables, constraints, and indexes."""
    op.create_table(
        "assignments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("assignment_type", assignment_type, nullable=False),
        sa.Column("publish_state", assignment_publish_state, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
            name=op.f("fk_assignments_course_id_courses"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_assignments")),
    )
    op.create_index(
        op.f("ix_assignments_course_id"),
        "assignments",
        ["course_id"],
        unique=False,
    )

    op.create_table(
        "assignment_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("assignment_id", sa.Uuid(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("change_summary", sa.String(length=255), nullable=False),
        sa.Column("config_snapshot", sa.JSON(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["assignment_id"],
            ["assignments.id"],
            name=op.f("fk_assignment_versions_assignment_id_assignments"),
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name=op.f("fk_assignment_versions_created_by_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_assignment_versions")),
        sa.UniqueConstraint(
            "assignment_id",
            "version_number",
            name="uq_assignment_versions_assignment_number",
        ),
    )
    op.create_index(
        op.f("ix_assignment_versions_assignment_id"),
        "assignment_versions",
        ["assignment_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_assignment_versions_created_by_user_id"),
        "assignment_versions",
        ["created_by_user_id"],
        unique=False,
    )

    op.create_table(
        "submissions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("assignment_id", sa.Uuid(), nullable=False),
        sa.Column("assignment_version_id", sa.Uuid(), nullable=False),
        sa.Column("student_user_id", sa.Uuid(), nullable=False),
        sa.Column("state", submission_state, nullable=False),
        sa.Column("artifact_key", sa.String(length=512), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["assignment_id"],
            ["assignments.id"],
            name=op.f("fk_submissions_assignment_id_assignments"),
        ),
        sa.ForeignKeyConstraint(
            ["assignment_version_id"],
            ["assignment_versions.id"],
            name=op.f("fk_submissions_assignment_version_id_assignment_versions"),
        ),
        sa.ForeignKeyConstraint(
            ["student_user_id"],
            ["users.id"],
            name=op.f("fk_submissions_student_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_submissions")),
    )
    op.create_index(
        op.f("ix_submissions_assignment_id"),
        "submissions",
        ["assignment_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_submissions_assignment_version_id"),
        "submissions",
        ["assignment_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_submissions_student_user_id"),
        "submissions",
        ["student_user_id"],
        unique=False,
    )

    op.create_table(
        "evaluation_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("submission_id", sa.Uuid(), nullable=False),
        sa.Column("assignment_version_id", sa.Uuid(), nullable=False),
        sa.Column("evaluation_kind", evaluation_kind, nullable=False),
        sa.Column("status", evaluation_status, nullable=False),
        sa.Column("score", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("max_score", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("summary", sa.String(length=512), nullable=False),
        sa.Column("result_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["assignment_version_id"],
            ["assignment_versions.id"],
            name=op.f(
                "fk_evaluation_records_assignment_version_id_assignment_versions",
            ),
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["submissions.id"],
            name=op.f("fk_evaluation_records_submission_id_submissions"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_evaluation_records")),
    )
    op.create_index(
        op.f("ix_evaluation_records_assignment_version_id"),
        "evaluation_records",
        ["assignment_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_evaluation_records_submission_id"),
        "evaluation_records",
        ["submission_id"],
        unique=False,
    )

    op.create_table(
        "grade_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("submission_id", sa.Uuid(), nullable=False),
        sa.Column("student_user_id", sa.Uuid(), nullable=False),
        sa.Column("grader_user_id", sa.Uuid(), nullable=True),
        sa.Column("state", grade_state, nullable=False),
        sa.Column("score", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("max_score", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["grader_user_id"],
            ["users.id"],
            name=op.f("fk_grade_records_grader_user_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["student_user_id"],
            ["users.id"],
            name=op.f("fk_grade_records_student_user_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["submissions.id"],
            name=op.f("fk_grade_records_submission_id_submissions"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_grade_records")),
    )
    op.create_index(
        op.f("ix_grade_records_grader_user_id"),
        "grade_records",
        ["grader_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_grade_records_student_user_id"),
        "grade_records",
        ["student_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_grade_records_submission_id"),
        "grade_records",
        ["submission_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop assessment tables, constraints, and indexes."""
    op.drop_index(op.f("ix_grade_records_submission_id"), table_name="grade_records")
    op.drop_index(op.f("ix_grade_records_student_user_id"), table_name="grade_records")
    op.drop_index(op.f("ix_grade_records_grader_user_id"), table_name="grade_records")
    op.drop_table("grade_records")

    op.drop_index(
        op.f("ix_evaluation_records_submission_id"),
        table_name="evaluation_records",
    )
    op.drop_index(
        op.f("ix_evaluation_records_assignment_version_id"),
        table_name="evaluation_records",
    )
    op.drop_table("evaluation_records")

    op.drop_index(op.f("ix_submissions_student_user_id"), table_name="submissions")
    op.drop_index(
        op.f("ix_submissions_assignment_version_id"),
        table_name="submissions",
    )
    op.drop_index(op.f("ix_submissions_assignment_id"), table_name="submissions")
    op.drop_table("submissions")

    op.drop_index(
        op.f("ix_assignment_versions_created_by_user_id"),
        table_name="assignment_versions",
    )
    op.drop_index(
        op.f("ix_assignment_versions_assignment_id"),
        table_name="assignment_versions",
    )
    op.drop_table("assignment_versions")

    op.drop_index(op.f("ix_assignments_course_id"), table_name="assignments")
    op.drop_table("assignments")
