"""Service tests for the generic assessment domain foundation."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from optimark_clio.assessment import CreateAssignmentVersionInput, RecordEvaluationInput
from optimark_metis.assessment import (
    AssignmentPublishState,
    AssignmentType,
    EvaluationKind,
    EvaluationStatus,
    GradeState,
    SubmissionState,
)
from optimark_metis.assessment_service import AssessmentService
from optimark_metis.errors import (
    DuplicateAssignmentVersionError,
    EntityNotFoundError,
    InvalidAssessmentDataError,
)


def test_assessment_service_creates_and_lists_assignment_entities(
    assessment_service: AssessmentService,
    academic_service,
) -> None:
    """Create and query assignments, versions, submissions, evaluations, and grades."""
    instructor = academic_service.create_user(
        email="instructor@example.com",
        display_name="Instructor",
    )
    student = academic_service.create_user(
        email="student@example.com",
        display_name="Student",
    )
    course = academic_service.create_course(
        course_code="CS101",
        title="Intro to CS",
        term="Fall 2026",
    )

    assignment = assessment_service.create_assignment(
        course_id=course.id,
        title="Project 1",
        description="Build a parser",
        assignment_type=AssignmentType.CODING,
        publish_state=AssignmentPublishState.PUBLISHED,
    )
    assignment_version = assessment_service.create_assignment_version(
        assignment_id=assignment.id,
        version_number=1,
        change_summary="Initial release",
        config_snapshot={"runner": "pytest", "time_limit_seconds": 30},
        created_by_user_id=instructor.id,
    )
    submission = assessment_service.create_submission(
        assignment_id=assignment.id,
        assignment_version_id=assignment_version.id,
        student_user_id=student.id,
        state=SubmissionState.SUBMITTED,
        artifact_key="submissions/project-1/student.zip",
    )
    evaluation = assessment_service.record_evaluation(
        submission_id=submission.id,
        assignment_version_id=assignment_version.id,
        evaluation_kind=EvaluationKind.AUTOMATED,
        status=EvaluationStatus.SUCCEEDED,
        score=Decimal("8.50"),
        max_score=Decimal("10.00"),
        summary="Autograde passed with minor deductions.",
        result_payload={"tests_passed": 17, "tests_failed": 1},
    )
    grade_record = assessment_service.record_grade(
        submission_id=submission.id,
        student_user_id=student.id,
        grader_user_id=instructor.id,
        state=GradeState.PROVISIONAL,
        score=Decimal("8.50"),
        max_score=Decimal("10.00"),
        feedback="Looks good overall.",
    )

    assert assessment_service.list_course_assignments(course.id) == [assignment]
    assert assessment_service.list_assignment_versions(assignment.id) == [
        assignment_version,
    ]
    assert assessment_service.list_assignment_submissions(assignment.id) == [submission]
    assert assessment_service.list_submission_evaluations(submission.id) == [evaluation]
    assert assessment_service.list_submission_grade_records(submission.id) == [
        grade_record,
    ]
    assert submission.submitted_at is not None
    assert evaluation.result_payload["tests_passed"] == 17
    assert grade_record.state is GradeState.PROVISIONAL


def test_assessment_service_rejects_duplicate_assignment_version_numbers(
    assessment_service: AssessmentService,
    academic_service,
) -> None:
    """Reject duplicate assignment version numbers for the same assignment."""
    instructor = academic_service.create_user(
        email="owner@example.com",
        display_name="Owner",
    )
    course = academic_service.create_course(
        course_code="CS102",
        title="Data Structures",
        term="Spring 2027",
    )
    assignment = assessment_service.create_assignment(
        course_id=course.id,
        title="Lab 1",
        description="Implement a queue",
        assignment_type=AssignmentType.CODING,
    )

    assessment_service.create_assignment_version(
        assignment_id=assignment.id,
        version_number=1,
        config_snapshot={"runner": "pytest"},
        created_by_user_id=instructor.id,
    )

    with pytest.raises(DuplicateAssignmentVersionError):
        assessment_service.create_assignment_version(
            assignment_id=assignment.id,
            version_number=1,
            config_snapshot={"runner": "pytest", "seed": 2},
            created_by_user_id=instructor.id,
        )


def test_assessment_service_updates_assignments(
    assessment_service: AssessmentService,
    academic_service,
) -> None:
    """Update editable assignment fields for a managed assignment."""
    course = academic_service.create_course(
        course_code="CS150",
        title="Programming Languages",
        term="Spring 2027",
    )
    assignment = assessment_service.create_assignment(
        course_id=course.id,
        title="Interpreter Lab",
        description="Build the first evaluator pass.",
        assignment_type=AssignmentType.CODING,
    )

    updated_assignment = assessment_service.update_assignment(
        assignment_id=assignment.id,
        title="Interpreter Project",
        description="Build the evaluator and parser passes.",
        publish_state=AssignmentPublishState.PUBLISHED,
    )

    assert updated_assignment.id == assignment.id
    assert updated_assignment.title == "Interpreter Project"
    assert updated_assignment.description == "Build the evaluator and parser passes."
    assert updated_assignment.publish_state is AssignmentPublishState.PUBLISHED


def test_assessment_service_allows_idempotent_assignment_updates(
    assessment_service: AssessmentService,
    academic_service,
) -> None:
    """Return the existing assignment when an update repeats current values."""
    course = academic_service.create_course(
        course_code="CS151",
        title="Compilers",
        term="Fall 2027",
    )
    assignment = assessment_service.create_assignment(
        course_id=course.id,
        title="CFG Lab",
        description="Build a control-flow graph.",
        assignment_type=AssignmentType.CODING,
        publish_state=AssignmentPublishState.DRAFT,
    )

    updated_assignment = assessment_service.update_assignment(
        assignment_id=assignment.id,
        title=assignment.title,
        description=assignment.description,
        assignment_type=assignment.assignment_type,
        publish_state=assignment.publish_state,
    )

    assert updated_assignment == assignment


def test_assessment_service_rejects_mismatched_submission_and_scores(
    assessment_service: AssessmentService,
    academic_service,
) -> None:
    """Reject mismatched assignment versions and invalid score combinations."""
    course = academic_service.create_course(
        course_code="CS103",
        title="Systems",
        term="Summer 2027",
    )
    student = academic_service.create_user(
        email="learner@example.com",
        display_name="Learner",
    )
    other_student = academic_service.create_user(
        email="other@example.com",
        display_name="Other",
    )
    assignment = assessment_service.create_assignment(
        course_id=course.id,
        title="HW 1",
        description="Concurrency warm-up",
        assignment_type=AssignmentType.CODING,
    )
    other_assignment = assessment_service.create_assignment(
        course_id=course.id,
        title="HW 2",
        description="Sockets warm-up",
        assignment_type=AssignmentType.CODING,
    )
    version = assessment_service.create_assignment_version(
        assignment_id=assignment.id,
        version_number=1,
        config_snapshot={"runner": "pytest"},
    )
    other_version = assessment_service.create_assignment_version(
        assignment_id=other_assignment.id,
        version_number=1,
        config_snapshot={"runner": "pytest"},
    )

    with pytest.raises(InvalidAssessmentDataError):
        assessment_service.create_submission(
            assignment_id=assignment.id,
            assignment_version_id=other_version.id,
            student_user_id=student.id,
        )

    submission = assessment_service.create_submission(
        assignment_id=assignment.id,
        assignment_version_id=version.id,
        student_user_id=student.id,
        state=SubmissionState.DRAFT,
    )

    assert submission.submitted_at is None

    with pytest.raises(InvalidAssessmentDataError):
        assessment_service.record_evaluation(
            submission_id=submission.id,
            assignment_version_id=version.id,
            evaluation_kind=EvaluationKind.AUTOMATED,
            status=EvaluationStatus.FAILED,
            score=Decimal("1.00"),
            max_score=None,
        )

    with pytest.raises(InvalidAssessmentDataError):
        assessment_service.record_grade(
            submission_id=submission.id,
            student_user_id=other_student.id,
            score=Decimal("5.00"),
            max_score=Decimal("10.00"),
        )


def test_assessment_service_validates_related_entities(
    assessment_service: AssessmentService,
) -> None:
    """Surface not-found errors when related academic entities are missing."""
    with pytest.raises(EntityNotFoundError):
        assessment_service.list_course_assignments(uuid4())


def test_assessment_service_rejects_non_json_serializable_payloads(
    assessment_service: AssessmentService,
    academic_service,
) -> None:
    """Reject payloads that cannot be serialized into JSON columns."""
    course = academic_service.create_course(
        course_code="CS104",
        title="Databases",
        term="Fall 2027",
    )
    student = academic_service.create_user(
        email="json-student@example.com",
        display_name="JSON Student",
    )
    assignment = assessment_service.create_assignment(
        course_id=course.id,
        title="HW JSON",
        description="Serialize all the things",
        assignment_type=AssignmentType.CODING,
    )

    with pytest.raises(InvalidAssessmentDataError, match="config_snapshot"):
        assessment_service.create_assignment_version(
            assignment_id=assignment.id,
            version_number=1,
            config_snapshot={"released_at": datetime.now(timezone.utc)},
        )

    assignment_version = assessment_service.create_assignment_version(
        assignment_id=assignment.id,
        version_number=1,
        config_snapshot={"runner": "pytest"},
    )
    submission = assessment_service.create_submission(
        assignment_id=assignment.id,
        assignment_version_id=assignment_version.id,
        student_user_id=student.id,
    )

    with pytest.raises(InvalidAssessmentDataError, match="result_payload"):
        assessment_service.record_evaluation(
            submission_id=submission.id,
            assignment_version_id=assignment_version.id,
            evaluation_kind=EvaluationKind.AUTOMATED,
            status=EvaluationStatus.FAILED,
            result_payload={"finished_at": datetime.now(timezone.utc)},
        )


def test_assessment_contracts_reject_non_json_serializable_payloads() -> None:
    """Reject non-JSON-serializable payloads at the contract boundary."""
    with pytest.raises(ValidationError, match="config_snapshot must be JSON-serializable"):
        CreateAssignmentVersionInput(
            assignment_id=uuid4(),
            version_number=1,
            config_snapshot={"created_at": datetime.now(timezone.utc)},
        )

    with pytest.raises(ValidationError, match="result_payload must be JSON-serializable"):
        RecordEvaluationInput(
            submission_id=uuid4(),
            assignment_version_id=uuid4(),
            evaluation_kind=EvaluationKind.AUTOMATED,
            status=EvaluationStatus.QUEUED,
            result_payload={"started_at": datetime.now(timezone.utc)},
        )
