"""Shared contracts for the coding-submission runner boundary."""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CodingRunnerLanguage(StrEnum):
    """Languages supported by the initial runner contract."""

    PYTHON = "python"


class CodingRunnerArtifactRole(StrEnum):
    """Roles an artifact can play in a runner request or result."""

    SUBMISSION = "submission"
    ASSIGNMENT_SUPPORT = "assignment_support"
    GRADER_SUPPORT = "grader_support"
    EXECUTION_LOG = "execution_log"
    RESULT_BUNDLE = "result_bundle"
    FEEDBACK_REPORT = "feedback_report"


class CodingRunnerOutcomeStatus(StrEnum):
    """Normalized terminal outcomes produced by a runner implementation."""

    SUCCEEDED = "succeeded"
    FAILED = "failed"
    INFRASTRUCTURE_ERROR = "infrastructure_error"
    CANCELLED = "cancelled"


class CodingRunnerFailureCode(StrEnum):
    """Failure categories stable enough for worker and API integration."""

    INVALID_REQUEST = "invalid_request"
    ARTIFACT_NOT_FOUND = "artifact_not_found"
    ASSIGNMENT_VERSION_NOT_FOUND = "assignment_version_not_found"
    UNSUPPORTED_LANGUAGE = "unsupported_language"
    EXECUTION_SETUP_FAILED = "execution_setup_failed"
    EXECUTION_TIMEOUT = "execution_timeout"
    EXECUTION_RUNTIME_ERROR = "execution_runtime_error"
    RUNNER_UNAVAILABLE = "runner_unavailable"
    INTERNAL_ERROR = "internal_error"


class CodingRunnerTestcaseStatus(StrEnum):
    """Normalized testcase outcomes emitted by the runner."""

    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class CodingRunnerArtifactRef(BaseModel):
    """Reference to an artifact consumed or produced by the runner."""

    role: CodingRunnerArtifactRole
    storage_provider: str = "s3"
    bucket: str
    key: str
    display_name: str
    content_type: str | None = None
    size_bytes: int | None = None
    sha256: str | None = None


class CodingRunnerExecutionLimits(BaseModel):
    """Execution ceilings passed to the runner as normalized policy input."""

    time_limit_seconds: int
    memory_limit_mebibytes: int
    max_output_bytes: int


class CodingRunnerExecutionMetadata(BaseModel):
    """Core identifiers and audit metadata required by every run."""

    run_id: UUID
    submission_id: UUID
    assignment_id: UUID
    assignment_version_id: UUID
    student_user_id: UUID
    requested_at: datetime
    attempt_number: int = 1
    initiated_by_user_id: UUID | None = None


class CodingRunnerRequest(BaseModel):
    """Stable request payload handed from the app/worker layer to a runner."""

    language: CodingRunnerLanguage
    metadata: CodingRunnerExecutionMetadata
    submission_artifact: CodingRunnerArtifactRef
    assignment_artifacts: list[CodingRunnerArtifactRef] = Field(default_factory=list)
    grader_artifacts: list[CodingRunnerArtifactRef] = Field(default_factory=list)
    grading_config: dict[str, Any] = Field(default_factory=dict)
    limits: CodingRunnerExecutionLimits
    execution_context: dict[str, str] = Field(default_factory=dict)


class CodingRunnerTestcaseResult(BaseModel):
    """Normalized testcase-level result emitted by the runner."""

    testcase_id: str
    status: CodingRunnerTestcaseStatus
    earned_score: float | None = None
    max_score: float | None = None
    message: str = ""


class CodingRunnerScoreSummary(BaseModel):
    """Normalized score summary emitted by the runner."""

    earned_score: float | None = None
    max_score: float | None = None
    score_components: dict[str, float] = Field(default_factory=dict)


class CodingRunnerFailureDetail(BaseModel):
    """Machine-readable failure payload for worker and API persistence."""

    code: CodingRunnerFailureCode
    message: str
    retryable: bool
    detail_payload: dict[str, Any] = Field(default_factory=dict)


class CodingRunnerResult(BaseModel):
    """Stable terminal response returned by a runner implementation."""

    run_id: UUID
    status: CodingRunnerOutcomeStatus
    started_at: datetime
    completed_at: datetime
    score_summary: CodingRunnerScoreSummary = Field(default_factory=CodingRunnerScoreSummary)
    testcase_results: list[CodingRunnerTestcaseResult] = Field(default_factory=list)
    output_artifacts: list[CodingRunnerArtifactRef] = Field(default_factory=list)
    logs: list[str] = Field(default_factory=list)
    failure: CodingRunnerFailureDetail | None = None
