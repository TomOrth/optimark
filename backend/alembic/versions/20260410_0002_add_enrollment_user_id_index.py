"""Add an index for user-centric enrollment lookups.

Revision ID: 20260410_0002
Revises: 20260409_0001
Create Date: 2026-04-10 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op


revision: str = "20260410_0002"
down_revision: str | None = "20260409_0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Create the enrollment user lookup index."""
    op.create_index("ix_enrollments_user_id", "enrollments", ["user_id"], unique=False)


def downgrade() -> None:
    """Drop the enrollment user lookup index."""
    op.drop_index("ix_enrollments_user_id", table_name="enrollments")
