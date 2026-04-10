"""Service and repository tests for the academic domain foundation."""

from sqlalchemy.exc import IntegrityError

from optimark_metis.academic import CourseRole
from optimark_metis.errors import DuplicateEnrollmentError
from optimark_metis.service import AcademicService
from optimark_mnemosyne.repository import SqlAlchemyAcademicRepository


def test_academic_service_creates_and_fetches_users_and_courses(
    academic_service: AcademicService,
) -> None:
    """Verify the service creates and retrieves users and courses."""
    user = academic_service.create_user(
        email="  instructor@example.edu ",
        display_name="  Dr. Ada Lovelace ",
    )
    course = academic_service.create_course(
        course_code="CS 1332",
        title="Data Structures and Algorithms",
        term="Fall 2026",
    )

    assert academic_service.get_user(user.id).email == "instructor@example.edu"
    assert academic_service.get_user(user.id).display_name == "Dr. Ada Lovelace"
    assert academic_service.list_users() == [user]

    assert academic_service.get_course(course.id).course_code == "CS 1332"
    assert academic_service.list_courses() == [course]


def test_academic_service_enrolls_users_and_filters_courses(
    academic_service: AcademicService,
) -> None:
    """Verify enrollments drive course and membership queries."""
    instructor = academic_service.create_user(
        email="instructor@example.edu",
        display_name="Instructor",
    )
    student = academic_service.create_user(
        email="student@example.edu",
        display_name="Student",
    )
    algorithms = academic_service.create_course(
        course_code="CS 3510",
        title="Algorithms",
        term="Spring 2027",
    )
    systems = academic_service.create_course(
        course_code="CS 3210",
        title="Design of Operating Systems",
        term="Spring 2027",
    )

    instructor_enrollment = academic_service.enroll_user(
        course_id=algorithms.id,
        user_id=instructor.id,
        role=CourseRole.INSTRUCTOR,
    )
    student_enrollment = academic_service.enroll_user(
        course_id=algorithms.id,
        user_id=student.id,
        role=CourseRole.STUDENT,
    )
    academic_service.enroll_user(
        course_id=systems.id,
        user_id=student.id,
        role=CourseRole.STUDENT,
    )

    assert academic_service.list_course_enrollments(algorithms.id) == [
        instructor_enrollment,
        student_enrollment,
    ]
    assert academic_service.list_courses_for_user(student.id) == [algorithms, systems]
    assert academic_service.list_courses_for_user(
        student.id,
        role_filter=CourseRole.STUDENT,
    ) == [algorithms, systems]
    assert academic_service.list_courses_for_user(
        instructor.id,
        role_filter=CourseRole.INSTRUCTOR,
    ) == [algorithms]
    assert academic_service.is_user_enrolled(
        course_id=algorithms.id,
        user_id=student.id,
        role=CourseRole.STUDENT,
    )
    assert not academic_service.is_user_enrolled(
        course_id=algorithms.id,
        user_id=student.id,
        role=CourseRole.TA,
    )


def test_academic_service_rejects_duplicate_enrollment(
    academic_service: AcademicService,
    db_session,
) -> None:
    """Verify duplicate enrollments are blocked in service and database layers."""
    user = academic_service.create_user(
        email="ta@example.edu",
        display_name="Teaching Assistant",
    )
    course = academic_service.create_course(
        course_code="CS 4400",
        title="Intro to Databases",
        term="Summer 2027",
    )

    academic_service.enroll_user(
        course_id=course.id,
        user_id=user.id,
        role=CourseRole.TA,
    )

    try:
        academic_service.enroll_user(
            course_id=course.id,
            user_id=user.id,
            role=CourseRole.TA,
        )
    except DuplicateEnrollmentError:
        pass
    else:
        raise AssertionError("expected duplicate enrollment to be rejected")

    repository = SqlAlchemyAcademicRepository(db_session)
    try:
        repository.add_enrollment(
            course_id=course.id,
            user_id=user.id,
            role=CourseRole.TA,
        )
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
    else:
        raise AssertionError("expected the database unique constraint to reject duplicates")
