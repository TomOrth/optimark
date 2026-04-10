"""Core academic domain entities for users, courses, and enrollments."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class CourseRole(StrEnum):
    """Role values used for course membership."""

    INSTRUCTOR = "instructor"
    TA = "ta"
    STUDENT = "student"


@dataclass(frozen=True)
class User:
    """Immutable domain representation of a user.

    Attributes:
        id: Stable user identifier.
        email: Normalized user email address.
        display_name: User-facing display name.
        created_at: Time when the user record was created.
        updated_at: Time when the user record was last updated.
    """

    id: UUID
    email: str
    display_name: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class Course:
    """Immutable domain representation of a course.

    Attributes:
        id: Stable course identifier.
        course_code: Human-readable course code.
        title: Course title.
        term: Academic term label.
        created_at: Time when the course record was created.
        updated_at: Time when the course record was last updated.
    """

    id: UUID
    course_code: str
    title: str
    term: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class Enrollment:
    """Immutable domain representation of a course enrollment.

    Attributes:
        id: Stable enrollment identifier.
        course_id: Related course identifier.
        user_id: Related user identifier.
        role: Membership role for the enrollment.
        created_at: Time when the enrollment record was created.
        updated_at: Time when the enrollment record was last updated.
    """

    id: UUID
    course_id: UUID
    user_id: UUID
    role: CourseRole
    created_at: datetime
    updated_at: datetime
