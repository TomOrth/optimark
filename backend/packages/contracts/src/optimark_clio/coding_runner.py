"""Shared contracts for the coding-submission runner boundary."""

import json
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


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
    RUN_CANCELLED = "run_cancelled"
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
    reference_uri: str
    display_name: str
    content_type: str | None = None
    size_bytes: int | None = Field(default=None, ge=0)
    sha256: str | None = None


class CodingRunnerExecutionLimits(BaseModel):
    """Execution ceilings passed to the runner as normalized policy input."""

    time_limit_seconds: int = Field(gt=0)
    memory_limit_mebibytes: int = Field(gt=0)
    max_output_bytes: int = Field(gt=0)


class CodingRunnerExecutionMetadata(BaseModel):
    """Core identifiers and audit metadata required by every run."""

    run_id: UUID
    submission_id: UUID
    assignment_id: UUID
    assignment_version_id: UUID
    student_user_id: UUID
    requested_at: datetime
    attempt_number: int = Field(default=1, ge=1)
    initiated_by_user_id: UUID | None = None


class CodingRunnerGradingConfig(BaseModel):
    """Normalized grading configuration consumed by the runner."""

    entrypoint: str
    invocation_args: list[str] = Field(default_factory=list)
    expected_result_format: str = "json"


class CodingRunnerRequest(BaseModel):
    """Stable request payload handed from the app/worker layer to a runner."""

    language: CodingRunnerLanguage
    runtime_version: str
    metadata: CodingRunnerExecutionMetadata
    submission_artifact: CodingRunnerArtifactRef
    assignment_artifacts: list[CodingRunnerArtifactRef] = Field(default_factory=list)
    grader_artifacts: list[CodingRunnerArtifactRef] = Field(default_factory=list)
    grading_config: CodingRunnerGradingConfig
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
    detail_payload: dict[str, object] = Field(default_factory=dict)

    @field_validator("detail_payload")
    @classmethod
    def validate_detail_payload(
        cls,
        value: dict[str, object],
    ) -> dict[str, object]:
        """Ensure failure detail payloads remain JSON-serializable."""
        _ensure_json_serializable(value, field_name="detail_payload")
        return value


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

    @model_validator(mode="after")
    def validate_failure_semantics(self) -> "CodingRunnerResult":
        """Ensure status/failure combinations are explicit and consistent."""
        if self.status is CodingRunnerOutcomeStatus.SUCCEEDED and self.failure is not None:
            raise ValueError("failure must be omitted when status is succeeded")
        if (
            self.status
            in {
                CodingRunnerOutcomeStatus.FAILED,
                CodingRunnerOutcomeStatus.INFRASTRUCTURE_ERROR,
                CodingRunnerOutcomeStatus.CANCELLED,
            }
            and self.failure is None
        ):
            raise ValueError(
                "failure is required for failed, infrastructure_error, and cancelled results",
            )
        return self


def _ensure_json_serializable(value: dict[str, object], *, field_name: str) -> None:
    """Validate that a mapping payload can be encoded as JSON."""
    try:
        json.dumps(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be JSON-serializable") from exc
