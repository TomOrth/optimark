"""Authorization policy helpers for course-scoped capabilities."""

from optimark_metis.academic import CourseRole
from optimark_metis.auth import CourseCapability
from optimark_metis.service import AcademicService


_CAPABILITY_ROLES: dict[CourseCapability, tuple[CourseRole, ...]] = {
    CourseCapability.MANAGE_COURSE: (CourseRole.INSTRUCTOR,),
    CourseCapability.GRADE_SUBMISSIONS: (
        CourseRole.INSTRUCTOR,
        CourseRole.TA,
    ),
    CourseCapability.SUBMIT_WORK: (CourseRole.STUDENT,),
}


def roles_for_capability(capability: CourseCapability) -> tuple[CourseRole, ...]:
    """Return the course roles that satisfy a capability.

    Args:
        capability: Capability to resolve.

    Returns:
        tuple[CourseRole, ...]: Roles that grant the capability.
    """
    return _CAPABILITY_ROLES[capability]


def capabilities_for_role(role: CourseRole) -> frozenset[CourseCapability]:
    """Return the capabilities granted by a role.

    Args:
        role: Course role to resolve.

    Returns:
        frozenset[CourseCapability]: Capabilities granted to the role.
    """
    return frozenset(
        capability
        for capability, roles in _CAPABILITY_ROLES.items()
        if role in roles
    )


class AuthorizationService:
    """Resolve whether users have course-scoped capabilities."""

    def __init__(self, academic_service: AcademicService) -> None:
        """Initialize the authorization service.

        Args:
            academic_service: Academic service used to resolve enrollments.
        """
        self._academic_service = academic_service

    def user_has_course_capability(
        self,
        *,
        course_id,
        user_id,
        capability: CourseCapability,
    ) -> bool:
        """Return whether a user has a capability in a course.

        Args:
            course_id: Course identifier to evaluate.
            user_id: User identifier to evaluate.
            capability: Capability to check.

        Returns:
            bool: True when the user has a qualifying course role.
        """
        return any(
            self._academic_service.is_user_enrolled(
                course_id=course_id,
                user_id=user_id,
                role=role,
            )
            for role in roles_for_capability(capability)
        )
