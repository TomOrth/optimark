"""Pydantic contracts for the academic domain foundation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from optimark_metis.academic import Course, CourseRole, Enrollment, User


class CreateUserInput(BaseModel):
    """Input payload for creating a user."""

    email: str
    display_name: str


class UserSummary(BaseModel):
    """Summary representation of a user.

    Attributes:
        id: Stable user identifier.
        email: Normalized user email address.
        display_name: User-facing display name.
    """

    id: UUID
    email: str
    display_name: str

    @classmethod
    def from_domain(cls, user: User) -> "UserSummary":
        """Build a summary contract from a domain user.

        Args:
            user: Domain user entity to serialize.

        Returns:
            UserSummary: The serialized user summary.
        """
        return cls(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
        )


class UserDetail(UserSummary):
    """Detailed representation of a user including timestamps.

    Attributes:
        created_at: Time when the user record was created.
        updated_at: Time when the user record was last updated.
    """

    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> "UserDetail":
        """Build a detail contract from a domain user.

        Args:
            user: Domain user entity to serialize.

        Returns:
            UserDetail: The serialized user detail payload.
        """
        return cls(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class CreateCourseInput(BaseModel):
    """Input payload for creating a course."""

    course_code: str
    title: str
    term: str


class CourseSummary(BaseModel):
    """Summary representation of a course.

    Attributes:
        id: Stable course identifier.
        course_code: Human-readable course code.
        title: Course title.
        term: Academic term label.
    """

    id: UUID
    course_code: str
    title: str
    term: str

    @classmethod
    def from_domain(cls, course: Course) -> "CourseSummary":
        """Build a summary contract from a domain course.

        Args:
            course: Domain course entity to serialize.

        Returns:
            CourseSummary: The serialized course summary.
        """
        return cls(
            id=course.id,
            course_code=course.course_code,
            title=course.title,
            term=course.term,
        )


class CourseDetail(CourseSummary):
    """Detailed representation of a course including timestamps.

    Attributes:
        created_at: Time when the course record was created.
        updated_at: Time when the course record was last updated.
    """

    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, course: Course) -> "CourseDetail":
        """Build a detail contract from a domain course.

        Args:
            course: Domain course entity to serialize.

        Returns:
            CourseDetail: The serialized course detail payload.
        """
        return cls(
            id=course.id,
            course_code=course.course_code,
            title=course.title,
            term=course.term,
            created_at=course.created_at,
            updated_at=course.updated_at,
        )


class EnrollUserInput(BaseModel):
    """Input payload for enrolling a user into a course."""

    course_id: UUID
    user_id: UUID
    role: CourseRole


class EnrollmentRecord(BaseModel):
    """Serialized enrollment record.

    Attributes:
        id: Stable enrollment identifier.
        course_id: Related course identifier.
        user_id: Related user identifier.
        role: Course membership role.
        created_at: Time when the enrollment record was created.
        updated_at: Time when the enrollment record was last updated.
    """

    id: UUID
    course_id: UUID
    user_id: UUID
    role: CourseRole
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, enrollment: Enrollment) -> "EnrollmentRecord":
        """Build an enrollment contract from a domain enrollment.

        Args:
            enrollment: Domain enrollment entity to serialize.

        Returns:
            EnrollmentRecord: The serialized enrollment payload.
        """
        return cls(
            id=enrollment.id,
            course_id=enrollment.course_id,
            user_id=enrollment.user_id,
            role=enrollment.role,
            created_at=enrollment.created_at,
            updated_at=enrollment.updated_at,
        )
