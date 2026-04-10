"""Application service layer for the academic domain foundation."""

from collections.abc import Sequence
from uuid import UUID

from optimark_metis.academic import Course, CourseRole, Enrollment, User
from optimark_metis.errors import (
    DuplicateEmailError,
    DuplicateEnrollmentError,
    EntityNotFoundError,
    InvalidAcademicDataError,
)
from optimark_metis.repository import AcademicRepository


class AcademicService:
    """Coordinate academic domain operations and validation."""

    def __init__(self, repository: AcademicRepository) -> None:
        """Initialize the service with a persistence repository.

        Args:
            repository: Repository implementation used for persistence and queries.
        """
        self._repository = repository

    def create_user(self, *, email: str, display_name: str) -> User:
        """Create a normalized user record.

        Args:
            email: User email address.
            display_name: User-facing display name.

        Returns:
            User: The persisted user entity.

        Raises:
            DuplicateEmailError: If the canonicalized email already exists.
            InvalidAcademicDataError: If any required field is blank.
        """
        normalized_email = self._normalize_required(
            value=email,
            field_name="email",
        ).lower()
        normalized_display_name = self._normalize_required(
            value=display_name,
            field_name="display_name",
        )

        if self._repository.get_user_by_email(normalized_email) is not None:
            raise DuplicateEmailError(f"user email {normalized_email} already exists")

        return self._repository.add_user(
            email=normalized_email,
            display_name=normalized_display_name,
        )

    def get_user(self, user_id: UUID) -> User:
        """Fetch a user by identifier.

        Args:
            user_id: User identifier to look up.

        Returns:
            User: The matching user entity.

        Raises:
            EntityNotFoundError: If no user exists for the identifier.
        """
        user = self._repository.get_user(user_id)
        if user is None:
            raise EntityNotFoundError(f"user {user_id} was not found")
        return user

    def list_users(self) -> Sequence[User]:
        """List all users.

        Returns:
            Sequence[User]: Ordered users from the repository.
        """
        return self._repository.list_users()

    def create_course(self, *, course_code: str, title: str, term: str) -> Course:
        """Create a normalized course record.

        Args:
            course_code: Human-readable course code.
            title: Course title.
            term: Academic term label.

        Returns:
            Course: The persisted course entity.

        Raises:
            InvalidAcademicDataError: If any required field is blank.
        """
        normalized_course_code = self._normalize_required(
            value=course_code,
            field_name="course_code",
        )
        normalized_title = self._normalize_required(value=title, field_name="title")
        normalized_term = self._normalize_required(value=term, field_name="term")
        return self._repository.add_course(
            course_code=normalized_course_code,
            title=normalized_title,
            term=normalized_term,
        )

    def get_course(self, course_id: UUID) -> Course:
        """Fetch a course by identifier.

        Args:
            course_id: Course identifier to look up.

        Returns:
            Course: The matching course entity.

        Raises:
            EntityNotFoundError: If no course exists for the identifier.
        """
        course = self._repository.get_course(course_id)
        if course is None:
            raise EntityNotFoundError(f"course {course_id} was not found")
        return course

    def list_courses(self) -> Sequence[Course]:
        """List all courses.

        Returns:
            Sequence[Course]: Ordered courses from the repository.
        """
        return self._repository.list_courses()

    def enroll_user(
        self,
        *,
        course_id: UUID,
        user_id: UUID,
        role: CourseRole,
    ) -> Enrollment:
        """Enroll a user into a course.

        Args:
            course_id: Course identifier to enroll into.
            user_id: User identifier to enroll.
            role: Membership role to assign.

        Returns:
            Enrollment: The persisted enrollment entity.

        Raises:
            EntityNotFoundError: If the course or user does not exist.
            DuplicateEnrollmentError: If the user is already enrolled in the course.
        """
        self.get_course(course_id)
        self.get_user(user_id)

        if self._repository.is_user_enrolled(course_id=course_id, user_id=user_id):
            raise DuplicateEnrollmentError(
                f"user {user_id} is already enrolled in course {course_id}",
            )

        return self._repository.add_enrollment(
            course_id=course_id,
            user_id=user_id,
            role=role,
        )

    def list_course_enrollments(self, course_id: UUID) -> Sequence[Enrollment]:
        """List enrollments for a course.

        Args:
            course_id: Course identifier to query.

        Returns:
            Sequence[Enrollment]: Ordered course enrollments.

        Raises:
            EntityNotFoundError: If the course does not exist.
        """
        self.get_course(course_id)
        return self._repository.list_course_enrollments(course_id)

    def list_courses_for_user(
        self,
        user_id: UUID,
        *,
        role_filter: CourseRole | None = None,
    ) -> Sequence[Course]:
        """List courses for a user, optionally filtered by role.

        Args:
            user_id: User identifier to query for.
            role_filter: Optional role that the enrollment must match.

        Returns:
            Sequence[Course]: Ordered courses for the user.

        Raises:
            EntityNotFoundError: If the user does not exist.
        """
        self.get_user(user_id)
        return self._repository.list_courses_for_user(user_id, role_filter=role_filter)

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

        Raises:
            EntityNotFoundError: If the course or user does not exist.
        """
        self.get_course(course_id)
        self.get_user(user_id)
        return self._repository.is_user_enrolled(
            course_id=course_id,
            user_id=user_id,
            role=role,
        )

    @staticmethod
    def _normalize_required(*, value: str, field_name: str) -> str:
        """Trim and validate a required string field.

        Args:
            value: Raw string value to normalize.
            field_name: Field name used in validation errors.

        Returns:
            str: Trimmed non-empty value.

        Raises:
            InvalidAcademicDataError: If the value is blank after trimming.
        """
        normalized_value = value.strip()
        if normalized_value == "":
            raise InvalidAcademicDataError(f"{field_name} is required")
        return normalized_value
