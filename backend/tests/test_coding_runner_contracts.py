"""Tests for the coding runner contract schemas."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from optimark_clio import (
    CodingRunnerArtifactRef,
    CodingRunnerArtifactRole,
    CodingRunnerExecutionLimits,
    CodingRunnerExecutionMetadata,
    CodingRunnerFailureCode,
    CodingRunnerFailureDetail,
    CodingRunnerGradingConfig,
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
        runtime_version="3.13",
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
            reference_uri="s3://optimark-dev/submissions/course/assignment/submission.zip",
            display_name="submission.zip",
            size_bytes=2048,
        ),
        assignment_artifacts=[
            CodingRunnerArtifactRef(
                role=CodingRunnerArtifactRole.ASSIGNMENT_SUPPORT,
                reference_uri="s3://optimark-dev/assignments/v1/tests.tar.gz",
                display_name="tests.tar.gz",
            ),
        ],
        grading_config=CodingRunnerGradingConfig(
            entrypoint="grader.py",
        ),
        limits=CodingRunnerExecutionLimits(
            time_limit_seconds=30,
            memory_limit_mebibytes=512,
            max_output_bytes=1_000_000,
        ),
    )

    assert request.metadata.run_id == run_id
    assert request.metadata.submission_id == submission_id
    assert request.assignment_artifacts[0].role is CodingRunnerArtifactRole.ASSIGNMENT_SUPPORT
    assert request.runtime_version == "3.13"
    assert request.grading_config.entrypoint == "grader.py"
    assert request.submission_artifact.reference_uri.startswith("s3://")


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


def test_coding_runner_contract_rejects_invalid_bounds_and_json_payloads() -> None:
    """Verify bounds and JSON-safe payload validation remain explicit."""
    with pytest.raises(ValueError, match="greater than 0"):
        CodingRunnerExecutionLimits(
            time_limit_seconds=0,
            memory_limit_mebibytes=512,
            max_output_bytes=1_000,
        )

    with pytest.raises(ValueError, match="greater than or equal to 1"):
        CodingRunnerExecutionMetadata(
            run_id=uuid4(),
            submission_id=uuid4(),
            assignment_id=uuid4(),
            assignment_version_id=uuid4(),
            student_user_id=uuid4(),
            requested_at=datetime(2026, 5, 9, 12, 0, tzinfo=UTC),
            attempt_number=0,
        )

    with pytest.raises(ValueError, match="detail_payload must be JSON-serializable"):
        CodingRunnerFailureDetail(
            code=CodingRunnerFailureCode.INTERNAL_ERROR,
            message="Bad payload",
            retryable=False,
            detail_payload={"bad": object()},
        )


def test_coding_runner_result_enforces_status_failure_semantics() -> None:
    """Verify terminal status and failure payload combinations are unambiguous."""
    base_kwargs = {
        "run_id": uuid4(),
        "started_at": datetime(2026, 5, 9, 12, 0, tzinfo=UTC),
        "completed_at": datetime(2026, 5, 9, 12, 1, tzinfo=UTC),
    }

    with pytest.raises(ValueError, match="failure must be omitted"):
        CodingRunnerResult(
            status=CodingRunnerOutcomeStatus.SUCCEEDED,
            failure=CodingRunnerFailureDetail(
                code=CodingRunnerFailureCode.INTERNAL_ERROR,
                message="should not be present",
                retryable=False,
            ),
            **base_kwargs,
        )

    with pytest.raises(ValueError, match="failure is required"):
        CodingRunnerResult(
            status=CodingRunnerOutcomeStatus.FAILED,
            failure=None,
            **base_kwargs,
        )

    cancelled = CodingRunnerResult(
        status=CodingRunnerOutcomeStatus.CANCELLED,
        failure=CodingRunnerFailureDetail(
            code=CodingRunnerFailureCode.RUN_CANCELLED,
            message="Cancelled by operator.",
            retryable=False,
        ),
        **base_kwargs,
    )
    assert cancelled.failure is not None
