"""SQLAlchemy ORM models for academic, assessment, and auth persistence."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    Uuid,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from optimark_metis.academic import CourseRole
from optimark_metis.assessment import (
    AssignmentPublishState,
    AssignmentType,
    EvaluationKind,
    EvaluationStatus,
    GradeState,
    SubmissionState,
)
from optimark_metis.auth import AuthProvider
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

assignment_type_enum = Enum(
    AssignmentType,
    values_callable=lambda values: [value.value for value in values],
    native_enum=False,
    name="assignment_type",
)

assignment_publish_state_enum = Enum(
    AssignmentPublishState,
    values_callable=lambda values: [value.value for value in values],
    native_enum=False,
    name="assignment_publish_state",
)

submission_state_enum = Enum(
    SubmissionState,
    values_callable=lambda values: [value.value for value in values],
    native_enum=False,
    name="submission_state",
)

evaluation_kind_enum = Enum(
    EvaluationKind,
    values_callable=lambda values: [value.value for value in values],
    native_enum=False,
    name="evaluation_kind",
)

evaluation_status_enum = Enum(
    EvaluationStatus,
    values_callable=lambda values: [value.value for value in values],
    native_enum=False,
    name="evaluation_status",
)

grade_state_enum = Enum(
    GradeState,
    values_callable=lambda values: [value.value for value in values],
    native_enum=False,
    name="grade_state",
)

auth_provider_enum = Enum(
    AuthProvider,
    values_callable=lambda providers: [provider.value for provider in providers],
    native_enum=False,
    name="auth_provider",
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
    assignment_versions: Mapped[list["AssignmentVersionModel"]] = relationship(
        back_populates="created_by_user",
    )
    submissions: Mapped[list["SubmissionModel"]] = relationship(
        back_populates="student_user",
    )
    recorded_grades: Mapped[list["GradeRecordModel"]] = relationship(
        back_populates="grader_user",
        foreign_keys="GradeRecordModel.grader_user_id",
    )
    earned_grades: Mapped[list["GradeRecordModel"]] = relationship(
        back_populates="student_user",
        foreign_keys="GradeRecordModel.student_user_id",
    )
    auth_identities: Mapped[list["AuthIdentityModel"]] = relationship(
        back_populates="user",
    )
    password_credential: Mapped["PasswordCredentialModel | None"] = relationship(
        back_populates="user",
        uselist=False,
    )
    auth_sessions: Mapped[list["AuthSessionModel"]] = relationship(
        back_populates="user",
    )


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
    assignments: Mapped[list["AssignmentModel"]] = relationship(
        back_populates="course",
    )


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


class AssignmentModel(Base):
    """ORM model for persisted assignments."""

    __tablename__ = "assignments"

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default=uuid4)
    course_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("courses.id"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text(), nullable=False)
    assignment_type: Mapped[AssignmentType] = mapped_column(
        assignment_type_enum,
        nullable=False,
    )
    publish_state: Mapped[AssignmentPublishState] = mapped_column(
        assignment_publish_state_enum,
        nullable=False,
    )
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

    course: Mapped[CourseModel] = relationship(back_populates="assignments")
    versions: Mapped[list["AssignmentVersionModel"]] = relationship(
        back_populates="assignment",
    )
    submissions: Mapped[list["SubmissionModel"]] = relationship(
        back_populates="assignment",
    )


class AssignmentVersionModel(Base):
    """ORM model for versioned assignment configuration snapshots."""

    __tablename__ = "assignment_versions"
    __table_args__ = (
        UniqueConstraint(
            "assignment_id",
            "version_number",
            name="uq_assignment_versions_assignment_number",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default=uuid4)
    assignment_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("assignments.id"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(nullable=False)
    change_summary: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    config_snapshot: Mapped[dict[str, object]] = mapped_column(JSON(), nullable=False)
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        Uuid(),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    assignment: Mapped[AssignmentModel] = relationship(back_populates="versions")
    created_by_user: Mapped[UserModel | None] = relationship(
        back_populates="assignment_versions",
    )
    submissions: Mapped[list["SubmissionModel"]] = relationship(
        back_populates="assignment_version",
    )
    evaluations: Mapped[list["EvaluationRecordModel"]] = relationship(
        back_populates="assignment_version",
    )


class SubmissionModel(Base):
    """ORM model for learner submissions."""

    __tablename__ = "submissions"

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default=uuid4)
    assignment_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("assignments.id"),
        nullable=False,
        index=True,
    )
    assignment_version_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("assignment_versions.id"),
        nullable=False,
        index=True,
    )
    student_user_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    state: Mapped[SubmissionState] = mapped_column(
        submission_state_enum,
        nullable=False,
    )
    artifact_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
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

    assignment: Mapped[AssignmentModel] = relationship(back_populates="submissions")
    assignment_version: Mapped[AssignmentVersionModel] = relationship(
        back_populates="submissions",
    )
    student_user: Mapped[UserModel] = relationship(back_populates="submissions")
    evaluations: Mapped[list["EvaluationRecordModel"]] = relationship(
        back_populates="submission",
    )
    grade_records: Mapped[list["GradeRecordModel"]] = relationship(
        back_populates="submission",
    )


class EvaluationRecordModel(Base):
    """ORM model for automated or manual evaluation results."""

    __tablename__ = "evaluation_records"

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default=uuid4)
    submission_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("submissions.id"),
        nullable=False,
        index=True,
    )
    assignment_version_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("assignment_versions.id"),
        nullable=False,
        index=True,
    )
    evaluation_kind: Mapped[EvaluationKind] = mapped_column(
        evaluation_kind_enum,
        nullable=False,
    )
    status: Mapped[EvaluationStatus] = mapped_column(
        evaluation_status_enum,
        nullable=False,
    )
    score: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    max_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    summary: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    result_payload: Mapped[dict[str, object]] = mapped_column(
        JSON(),
        nullable=False,
        default=dict,
    )
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

    submission: Mapped[SubmissionModel] = relationship(back_populates="evaluations")
    assignment_version: Mapped[AssignmentVersionModel] = relationship(
        back_populates="evaluations",
    )


class GradeRecordModel(Base):
    """ORM model for grade decisions associated with submissions."""

    __tablename__ = "grade_records"

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default=uuid4)
    submission_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("submissions.id"),
        nullable=False,
        index=True,
    )
    student_user_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    grader_user_id: Mapped[UUID | None] = mapped_column(
        Uuid(),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    state: Mapped[GradeState] = mapped_column(grade_state_enum, nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    max_score: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    feedback: Mapped[str] = mapped_column(Text(), nullable=False, default="")
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

    submission: Mapped[SubmissionModel] = relationship(back_populates="grade_records")
    student_user: Mapped[UserModel] = relationship(
        back_populates="earned_grades",
        foreign_keys=[student_user_id],
    )
    grader_user: Mapped[UserModel | None] = relationship(
        back_populates="recorded_grades",
        foreign_keys=[grader_user_id],
    )


class AuthIdentityModel(Base):
    """ORM model linking a user to an auth provider subject."""

    __tablename__ = "auth_identities"
    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_subject",
            name="uq_auth_identities_provider_subject",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    provider: Mapped[AuthProvider] = mapped_column(auth_provider_enum, nullable=False)
    provider_subject: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    user: Mapped[UserModel] = relationship(back_populates="auth_identities")


class PasswordCredentialModel(Base):
    """ORM model storing password credentials for users."""

    __tablename__ = "password_credentials"

    user_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("users.id"),
        primary_key=True,
    )
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
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

    user: Mapped[UserModel] = relationship(back_populates="password_credential")


class AuthSessionModel(Base):
    """ORM model storing opaque authenticated sessions."""

    __tablename__ = "auth_sessions"

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped[UserModel] = relationship(back_populates="auth_sessions")
