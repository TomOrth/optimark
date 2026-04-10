"""SQLAlchemy ORM models for the academic domain foundation."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, Uuid, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from optimark_metis.academic import CourseRole
from optimark_mnemosyne.base import Base


def utc_now() -> datetime:
    """Return the current UTC timestamp.

    Returns:
        datetime: Timezone-aware UTC timestamp.
    """
    return datetime.now(timezone.utc)


course_role_enum = Enum(
    CourseRole,
    values_callable=lambda roles: [role.value for role in roles],
    native_enum=False,
    name="course_role",
)


class UserModel(Base):
    """ORM model for persisted platform users."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    enrollments: Mapped[list["EnrollmentModel"]] = relationship(back_populates="user")


class CourseModel(Base):
    """ORM model for persisted courses."""

    __tablename__ = "courses"

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default=uuid4)
    course_code: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    term: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    enrollments: Mapped[list["EnrollmentModel"]] = relationship(back_populates="course")


class EnrollmentModel(Base):
    """ORM model linking a user to a course with a single role."""

    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("course_id", "user_id", name="uq_enrollments_course_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default=uuid4)
    course_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("courses.id"),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    role: Mapped[CourseRole] = mapped_column(course_role_enum, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    course: Mapped[CourseModel] = relationship(back_populates="enrollments")
    user: Mapped[UserModel] = relationship(back_populates="enrollments")
