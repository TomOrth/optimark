# ADR-0003: Generic Assessment Domain with Coding as a Specialized Assignment Type

- Status: Accepted
- Date: 2026-04-05

## Context
Optimark starts with coding assignments, but the intended expansion path includes file/PDF submissions and later quizzes/exams. If the first schema and service model are built specifically for coding, the product will be harder to extend into broader assessment workflows.

We need a domain model that supports coding assignments now without forcing future non-coding assessment types into awkward retrofits.

## Decision
Optimark will use a generic assessment core domain centered on:
- `User`
- `Course`
- `Enrollment`
- `Assignment`
- `AssignmentVersion`
- `Submission`
- `SubmissionArtifact`
- `AutogradeRun`
- `Rubric` and `RubricItem`
- `GradeRecord`
- `FeedbackComment`

`Assignment` will be the generic assessment unit. Coding behavior will be expressed as a specialized assignment type and typed configuration attached to the generic assignment model, rather than through a separate parallel coding-only assignment system.

## Consequences
### Positive
- Preserves a clean path to non-coding assessment types.
- Keeps common workflow concepts reusable across assignment types.
- Makes gradebook and review experiences easier to generalize later.

### Negative
- Adds some abstraction overhead to the first coding-assignment implementation.
- Requires care to avoid over-generalizing features before they are needed.

### Follow-on implications
- `AssignmentVersion` should be used to snapshot published configuration.
- `AutogradeRun` should represent execution attempts, not the final authoritative grade.
- `GradeRecord` should remain the source of truth for released grading state.
- Coding-specific storage and business logic should extend the generic model rather than bypass it.
