# ADR-0008: Runner Contract for Coding Submissions

- Status: Accepted
- Date: 2026-05-09

## Context
ADR-0004 established that the coding submission engine must be contract-driven before Optimark commits to a final execution architecture. Since then, the MVP has gained:
- assignment versioning
- student submission upload and artifact persistence
- submission lifecycle states visible to the UI

The next backend milestone is autograde orchestration. That work needs a concrete contract between the application or worker layer and any future runner implementation. Without that contract, issue `#10` would be forced to guess:
- which identifiers are required to launch a run
- how submission and assignment artifacts are referenced
- which output fields are normalized and persisted
- how retry and failure behavior should be interpreted

The contract must be explicit enough for worker integration and API-visible status handling, while still avoiding premature commitment to Docker, Firecracker, VMs, or a particular packaging transport.

## Decision
Optimark will define the coding runner boundary around a typed request/terminal-result contract that is shared across the app and worker layers.

The contract is represented in the shared contracts package at:
- [coding_runner.py](../../backend/packages/contracts/src/optimark_clio/coding_runner.py)

### Request shape
Every runner invocation must include:
- stable run metadata:
  - `run_id`
  - `submission_id`
  - `assignment_id`
  - `assignment_version_id`
  - `student_user_id`
  - `requested_at`
  - `attempt_number`
- optional `initiated_by_user_id`
- `language`
- `runtime_version`
- one required `submission_artifact` reference
- zero or more `assignment_artifacts`
- zero or more `grader_artifacts`
- normalized `grading_config`
- normalized execution `limits`
- optional `execution_context` metadata

### Artifact reference semantics
Artifact references are URI-oriented and intentionally runtime-agnostic. Each artifact reference includes:
- a normalized `reference_uri`
- display name
- optional content metadata such as `content_type`, `size_bytes`, and `sha256`
- an explicit artifact role

The contract deliberately references artifacts by location rather than embedding file payloads in the runner request.

### Output shape
The runner returns one terminal result payload containing:
- `run_id`
- terminal `status`
- `started_at`
- `completed_at`
- normalized `score_summary`
- per-testcase result records
- output artifact references
- logs
- optional machine-readable failure detail

### Status semantics
Queueing and in-progress state are orchestration concerns, not terminal runner outcomes.

The runner contract therefore defines terminal outcome states only:
- `succeeded`
- `failed`
- `infrastructure_error`
- `cancelled`

The worker or orchestration layer remains responsible for broader run lifecycle states such as:
- `queued`
- `running`
- `completed`
- `failed`

This keeps the contract compatible with multiple orchestration strategies while still giving the application a normalized terminal payload.

### Failure semantics
Failures must be normalized into stable categories instead of runner-specific exception text alone.

The initial failure-code set is:
- `invalid_request`
- `artifact_not_found`
- `assignment_version_not_found`
- `unsupported_language`
- `execution_setup_failed`
- `execution_timeout`
- `execution_runtime_error`
- `runner_unavailable`
- `internal_error`

Each failure detail also includes:
- a human-readable message
- a `retryable` flag
- optional structured detail payload

The shared schema also enforces the relationship between terminal outcome and failure payload:
- `succeeded` results must not include `failure`
- `failed`, `infrastructure_error`, and `cancelled` results must include `failure`

### Python-first, future-extensible
The initial language enum includes only `python`, which matches the MVP. This is an intentional product constraint rather than a hard architectural ceiling. The request now carries `runtime_version` explicitly so Python-first execution can remain normalized without burying version choice inside ad hoc config blobs, and additional language values can be added later without redefining the overall contract shape.

## Consequences
### Positive
- Gives issue `#10` a concrete boundary for autograde run orchestration and persistence.
- Prevents the API and worker layers from baking in a runner-specific payload shape.
- Separates orchestration lifecycle from terminal execution outcome semantics.
- Keeps artifact addressing generic enough for object-storage-backed and future non-object-storage execution strategies.
- Makes artifact references, failure codes, and result payloads explicit enough for later review and grade workflows.

### Negative
- Some details still remain intentionally open, especially artifact packaging conventions and the final transport from object storage into execution.
- A future runner implementation may still require adapters if its native request/response format differs from the shared contract.

### Follow-on implications
- Issue `#10` should persist run lifecycle state separately from the terminal runner result payload.
- Issue `#14` should define how assignment and grader support artifacts are bundled or referenced before execution without changing the request envelope.
- Issue `#15` should build on the normalized score and failure fields rather than inventing alternate grading semantics in the worker layer.
- Future execution implementations must map their native failures into the shared failure-code taxonomy.

## Explicit Non-Decisions
This ADR does not decide:
- the final isolation technology
- the final artifact packaging format
- whether orchestration uses Redis queues, Postgres polling, or another transport
- how multi-language support is scheduled beyond preserving the extensibility seam
