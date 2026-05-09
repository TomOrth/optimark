# ADR-0009: Artifact Packaging and Execution Handoff for Coding Runs

- Status: Accepted
- Date: 2026-05-09

## Context
ADR-0008 defined the stable runner request and result contract, but it intentionally left one critical boundary open: how submission artifacts, assignment support assets, and grader inputs are prepared for execution.

The product now has:
- versioned assignments
- persisted submission artifacts
- a runner request that references artifacts by URI

The next implementation milestone is orchestration in issue `#10`. That worker-side flow needs more than a runner request. It also needs a stable handoff model that explains:
- which artifacts participate in a run
- how those artifacts are grouped for execution preparation
- whether execution consumes references directly or a prepared workspace bundle
- how the application records that handoff without choosing the final sandbox transport

Without that packaging model, `#10` would be forced to embed storage-specific staging assumptions or runner-specific workspace conventions into the worker logic.

## Decision
Optimark will define a stable execution handoff manifest that sits between orchestration and the runner-facing execution environment.

The shared packaging and handoff contracts are represented at:
- [coding_handoff.py](../../backend/packages/contracts/src/optimark_clio/coding_handoff.py)

### Artifact types in a coding run
The artifact set for an MVP coding run consists of:
- one required submission artifact:
  - the student-uploaded source artifact for a specific `submission_id`
- zero or more assignment support artifacts:
  - starter files
  - hidden tests
  - fixtures
  - instructor-authored data files tied to an `assignment_version_id`
- zero or more grader support artifacts:
  - grader entrypoints
  - harness code
  - reference assets required by the grading implementation
- optional execution output artifacts:
  - logs
  - result bundles
  - feedback reports

These artifact categories remain orthogonal to the final transport or staging strategy.

### Handoff modes
The contract supports two packaging modes:

1. `reference_manifest`
   - orchestration produces a manifest artifact plus an artifact-set record
   - the downstream execution layer resolves artifact URIs itself
   - this is the least opinionated mode and keeps storage references first-class

2. `prepared_bundle`
   - orchestration produces a prepared workspace bundle plus an explicit mapping of source artifacts to relative bundle paths
   - the downstream execution layer consumes one packaged workspace artifact instead of resolving each source reference independently

Both modes share the same top-level handoff envelope so the worker can evolve from reference-first staging to prepared bundles without changing the external orchestration contract.

### Stable handoff manifest
Every execution handoff must include:
- `handoff_id`
- `run_id`
- `assignment_id`
- `assignment_version_id`
- `submission_id`
- `created_at`
- `packaging_version`
- `mode`
- the normalized input artifact set
- a `staging_key_prefix`

Mode-specific fields:
- `reference_manifest` requires `manifest_artifact`
- `prepared_bundle` requires `prepared_bundle_artifact` and `bundle_entries`

### Bundle entry semantics
Prepared bundles must declare how source artifacts are materialized into the execution workspace. Each bundle entry records:
- the source artifact reference
- the normalized entry kind
- the relative workspace path
- whether the source is required
- the extraction/materialization mode

This keeps bundle layout decisions explicit and auditable instead of hidden inside a worker implementation.

### Versioning semantics
Assignment versioning and submission identity are part of the handoff contract, not incidental metadata:
- `assignment_version_id` identifies the exact versioned assignment context for hidden tests, starter assets, and grader inputs
- `submission_id` identifies the exact student artifact chosen for execution
- `run_id` identifies the execution attempt that consumed those inputs

This makes reruns and future review workflows easier to reason about because artifact provenance is carried directly by the handoff manifest.

## Consequences
### Positive
- Gives issue `#10` a stable staging contract for worker orchestration.
- Keeps artifact grouping and bundle layout explicit without choosing a final sandbox runtime.
- Preserves assignment-version and submission provenance through the handoff boundary.
- Supports a low-commitment reference-first implementation while leaving room for prepared bundle optimization later.

### Negative
- Adds one more contract layer between orchestration and execution.
- Some implementation details, like archive extraction policy and staging retention, remain intentionally unresolved.

### Follow-on implications
- Issue `#10` should persist an execution handoff record or equivalent manifest reference alongside autograde run state.
- Issue `#13` runner requests should consume artifact refs derived from this handoff contract rather than bypassing it.
- Issue `#16` can choose the eventual isolation/scaling strategy without redefining the packaging envelope.

## Explicit Non-Decisions
This ADR does not decide:
- whether prepared bundles are tarballs, zip archives, mounted directories, or another format
- whether references are resolved from object storage, local disk mirrors, or another backing store
- the final sandbox transport between worker and execution runtime
- the long-term retention policy for staged workspaces or intermediate artifacts
