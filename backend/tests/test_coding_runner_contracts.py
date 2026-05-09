"""Tests for the coding runner contract schemas."""

from datetime import UTC, datetime
from uuid import uuid4

from optimark_clio import (
    CodingRunnerArtifactRef,
    CodingRunnerArtifactRole,
    CodingRunnerExecutionLimits,
    CodingRunnerExecutionMetadata,
    CodingRunnerFailureCode,
    CodingRunnerFailureDetail,
    CodingRunnerLanguage,
    CodingRunnerOutcomeStatus,
    CodingRunnerRequest,
    CodingRunnerResult,
    CodingRunnerScoreSummary,
    CodingRunnerTestcaseResult,
    CodingRunnerTestcaseStatus,
)


def test_coding_runner_request_captures_required_handoff_fields() -> None:
    """Verify the request schema covers the MVP runner handoff boundary."""
    run_id = uuid4()
    submission_id = uuid4()
    assignment_id = uuid4()
    assignment_version_id = uuid4()
    student_user_id = uuid4()

    request = CodingRunnerRequest(
        language=CodingRunnerLanguage.PYTHON,
        metadata=CodingRunnerExecutionMetadata(
            run_id=run_id,
            submission_id=submission_id,
            assignment_id=assignment_id,
            assignment_version_id=assignment_version_id,
            student_user_id=student_user_id,
            requested_at=datetime(2026, 5, 9, 12, 0, tzinfo=UTC),
            initiated_by_user_id=uuid4(),
        ),
        submission_artifact=CodingRunnerArtifactRef(
            role=CodingRunnerArtifactRole.SUBMISSION,
            bucket="optimark-dev",
            key="submissions/course/assignment/submission.zip",
            display_name="submission.zip",
            size_bytes=2048,
        ),
        assignment_artifacts=[
            CodingRunnerArtifactRef(
                role=CodingRunnerArtifactRole.ASSIGNMENT_SUPPORT,
                bucket="optimark-dev",
                key="assignments/v1/tests.tar.gz",
                display_name="tests.tar.gz",
            ),
        ],
        grading_config={"entrypoint": "grader.py", "python_version": "3.13"},
        limits=CodingRunnerExecutionLimits(
            time_limit_seconds=30,
            memory_limit_mebibytes=512,
            max_output_bytes=1_000_000,
        ),
    )

    assert request.metadata.run_id == run_id
    assert request.metadata.submission_id == submission_id
    assert request.assignment_artifacts[0].role is CodingRunnerArtifactRole.ASSIGNMENT_SUPPORT
    assert request.grading_config["entrypoint"] == "grader.py"


def test_coding_runner_result_normalizes_terminal_outcomes() -> None:
    """Verify the result schema supports scores, testcase detail, and failures."""
    run_id = uuid4()
    result = CodingRunnerResult(
        run_id=run_id,
        status=CodingRunnerOutcomeStatus.FAILED,
        started_at=datetime(2026, 5, 9, 12, 0, tzinfo=UTC),
        completed_at=datetime(2026, 5, 9, 12, 1, tzinfo=UTC),
        score_summary=CodingRunnerScoreSummary(
            earned_score=3.0,
            max_score=10.0,
            score_components={"tests": 3.0},
        ),
        testcase_results=[
            CodingRunnerTestcaseResult(
                testcase_id="test_reverse_list",
                status=CodingRunnerTestcaseStatus.FAILED,
                earned_score=0.0,
                max_score=2.0,
                message="Expected reversed ordering.",
            ),
        ],
        failure=CodingRunnerFailureDetail(
            code=CodingRunnerFailureCode.EXECUTION_RUNTIME_ERROR,
            message="Process exited with code 1.",
            retryable=False,
            detail_payload={"exit_code": 1},
        ),
        logs=["Traceback ..."],
    )

    assert result.run_id == run_id
    assert result.status is CodingRunnerOutcomeStatus.FAILED
    assert result.failure is not None
    assert result.failure.code is CodingRunnerFailureCode.EXECUTION_RUNTIME_ERROR
    assert result.testcase_results[0].status is CodingRunnerTestcaseStatus.FAILED
