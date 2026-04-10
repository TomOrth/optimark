"""SQLAlchemy-backed repository implementations for academic data."""

from datetime import UTC, datetime
from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from optimark_metis.academic import Course, CourseRole, Enrollment, User
from optimark_metis.errors import DuplicateEmailError
from optimark_mnemosyne.models import CourseModel, EnrollmentModel, UserModel


class SqlAlchemyAcademicRepository:
    """Persist and query academic entities through SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with an active SQLAlchemy session.

        Args:
            session: Active ORM session used for persistence operations.
        """
        self._session = session

    def add_user(self, *, email: str, display_name: str) -> User:
        """Insert a new user record.

        Args:
            email: Normalized user email address.
            display_name: User-facing display name.

        Returns:
            User: The persisted domain user.

        Raises:
            DuplicateEmailError: If the canonical email already exists.
        """
        model = UserModel(email=email, display_name=display_name)
        self._session.add(model)
        try:
            self._session.flush()
        except IntegrityError as exc:
            if _is_duplicate_email_integrity_error(exc):
                raise DuplicateEmailError(f"user email {email} already exists") from exc
            raise
        return _user_from_model(model)

    def get_user_by_email(self, email: str) -> User | None:
        """Fetch a user by canonical email address.

        Args:
            email: Canonical email address to look up.

        Returns:
            User | None: The matching user when present.
        """
        statement = select(UserModel).where(UserModel.email == email)
        model = self._session.scalar(statement)
        if model is None:
            return None
        return _user_from_model(model)

    def get_user(self, user_id: UUID) -> User | None:
        """Fetch a user by identifier.

        Args:
            user_id: User identifier to look up.

        Returns:
            User | None: The matching user when present.
        """
        model = self._session.get(UserModel, user_id)
        if model is None:
            return None
        return _user_from_model(model)

    def list_users(self) -> Sequence[User]:
        """List all persisted users in creation order.

        Returns:
            Sequence[User]: Ordered collection of users.
        """
        statement = select(UserModel).order_by(UserModel.created_at, UserModel.id)
        return [_user_from_model(model) for model in self._session.scalars(statement)]

    def add_course(self, *, course_code: str, title: str, term: str) -> Course:
        """Insert a new course record.

        Args:
            course_code: Human-readable course code.
            title: Course title.
            term: Academic term label.

        Returns:
            Course: The persisted domain course.
        """
        model = CourseModel(course_code=course_code, title=title, term=term)
        self._session.add(model)
        self._session.flush()
        return _course_from_model(model)

    def get_course(self, course_id: UUID) -> Course | None:
        """Fetch a course by identifier.

        Args:
            course_id: Course identifier to look up.

        Returns:
            Course | None: The matching course when present.
        """
        model = self._session.get(CourseModel, course_id)
        if model is None:
            return None
        return _course_from_model(model)

    def list_courses(self) -> Sequence[Course]:
        """List all persisted courses in creation order.

        Returns:
            Sequence[Course]: Ordered collection of courses.
        """
        statement = select(CourseModel).order_by(CourseModel.created_at, CourseModel.id)
        return [_course_from_model(model) for model in self._session.scalars(statement)]

    def add_enrollment(
        self,
        *,
        course_id: UUID,
        user_id: UUID,
        role: CourseRole,
    ) -> Enrollment:
        """Insert a new enrollment record.

        Args:
            course_id: Related course identifier.
            user_id: Related user identifier.
            role: Membership role for the enrollment.

        Returns:
            Enrollment: The persisted enrollment entity.
        """
        model = EnrollmentModel(course_id=course_id, user_id=user_id, role=role)
        self._session.add(model)
        self._session.flush()
        return _enrollment_from_model(model)

    def list_course_enrollments(self, course_id: UUID) -> Sequence[Enrollment]:
        """List enrollments for a course.

        Args:
            course_id: Course identifier to filter by.

        Returns:
            Sequence[Enrollment]: Ordered enrollments for the course.
        """
        statement = (
            select(EnrollmentModel)
            .where(EnrollmentModel.course_id == course_id)
            .order_by(EnrollmentModel.created_at, EnrollmentModel.id)
        )
        return [
            _enrollment_from_model(model) for model in self._session.scalars(statement)
        ]

    def list_courses_for_user(
        self,
        user_id: UUID,
        *,
        role_filter: CourseRole | None = None,
    ) -> Sequence[Course]:
        """List courses for a user, optionally filtered by role.

        Args:
            user_id: User identifier to filter by.
            role_filter: Optional enrollment role filter.

        Returns:
            Sequence[Course]: Ordered courses for the user.
        """
        statement: Select[tuple[CourseModel]] = (
            select(CourseModel)
            .join(EnrollmentModel, EnrollmentModel.course_id == CourseModel.id)
            .where(EnrollmentModel.user_id == user_id)
            .order_by(CourseModel.created_at, CourseModel.id)
        )
        if role_filter is not None:
            statement = statement.where(EnrollmentModel.role == role_filter)

        return [_course_from_model(model) for model in self._session.scalars(statement)]

    def is_user_enrolled(
        self,
        *,
        course_id: UUID,
        user_id: UUID,
        role: CourseRole | None = None,
    ) -> bool:
        """Check whether a user is enrolled in a course.

        Args:
            course_id: Course identifier to check.
            user_id: User identifier to check.
            role: Optional role that must match the enrollment.

        Returns:
            bool: True when a matching enrollment exists.
        """
        statement = select(EnrollmentModel.id).where(
            EnrollmentModel.course_id == course_id,
            EnrollmentModel.user_id == user_id,
        )
        if role is not None:
            statement = statement.where(EnrollmentModel.role == role)

        return self._session.scalar(statement) is not None


def _user_from_model(model: UserModel) -> User:
    """Convert a user ORM model into a domain user.

    Args:
        model: ORM user model instance.

    Returns:
        User: Domain user entity.
    """
    return User(
        id=model.id,
        email=model.email,
        display_name=model.display_name,
        created_at=_coerce_utc(model.created_at),
        updated_at=_coerce_utc(model.updated_at),
    )


def _course_from_model(model: CourseModel) -> Course:
    """Convert a course ORM model into a domain course.

    Args:
        model: ORM course model instance.

    Returns:
        Course: Domain course entity.
    """
    return Course(
        id=model.id,
        course_code=model.course_code,
        title=model.title,
        term=model.term,
        created_at=_coerce_utc(model.created_at),
        updated_at=_coerce_utc(model.updated_at),
    )


def _enrollment_from_model(model: EnrollmentModel) -> Enrollment:
    """Convert an enrollment ORM model into a domain enrollment.

    Args:
        model: ORM enrollment model instance.

    Returns:
        Enrollment: Domain enrollment entity.
    """
    return Enrollment(
        id=model.id,
        course_id=model.course_id,
        user_id=model.user_id,
        role=model.role,
        created_at=_coerce_utc(model.created_at),
        updated_at=_coerce_utc(model.updated_at),
    )


def _coerce_utc(value: datetime) -> datetime:
    """Normalize timestamps to timezone-aware UTC values.

    Args:
        value: Timestamp returned by the ORM or database driver.

    Returns:
        datetime: Timezone-aware UTC timestamp.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _is_duplicate_email_integrity_error(error: IntegrityError) -> bool:
    """Return whether an integrity error represents a duplicate user email.

    Args:
        error: Integrity error raised by SQLAlchemy during flush.

    Returns:
        bool: True when the error matches the user-email uniqueness constraint.
    """
    message = str(error.orig)
    return (
        "uq_users_email" in message
        or "users.email" in message
        or "UNIQUE constraint failed: users.email" in message
    )
