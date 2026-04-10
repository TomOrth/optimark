"""Repository protocol definitions for academic persistence."""

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from optimark_metis.academic import Course, CourseRole, Enrollment, User


class AcademicRepository(Protocol):
    """Protocol describing persistence operations for academic data."""

    def add_user(self, *, email: str, display_name: str) -> User:
        """Persist a new user."""

    def get_user_by_email(self, email: str) -> User | None:
        """Fetch a user by canonical email address."""

    def get_user(self, user_id: UUID) -> User | None:
        """Fetch a user by identifier."""

    def list_users(self) -> Sequence[User]:
        """List all users."""

    def add_course(self, *, course_code: str, title: str, term: str) -> Course:
        """Persist a new course."""

    def get_course(self, course_id: UUID) -> Course | None:
        """Fetch a course by identifier."""

    def list_courses(self) -> Sequence[Course]:
        """List all courses."""

    def add_enrollment(
        self,
        *,
        course_id: UUID,
        user_id: UUID,
        role: CourseRole,
    ) -> Enrollment:
        """Persist a new enrollment."""

    def list_course_enrollments(self, course_id: UUID) -> Sequence[Enrollment]:
        """List enrollments for a course."""

    def list_courses_for_user(
        self,
        user_id: UUID,
        *,
        role_filter: CourseRole | None = None,
    ) -> Sequence[Course]:
        """List courses for a user, optionally filtered by role."""

    def is_user_enrolled(
        self,
        *,
        course_id: UUID,
        user_id: UUID,
        role: CourseRole | None = None,
    ) -> bool:
        """Check whether a matching enrollment exists."""
