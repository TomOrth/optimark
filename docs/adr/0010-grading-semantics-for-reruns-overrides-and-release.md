# ADR-0010: Grading Semantics for Reruns, Overrides, and Grade Release

- Status: Accepted
- Date: 2026-05-09

## Context

Optimark's coding-assignment workflow now has a clear submission contract and runner boundary, but the product still needs explicit grading semantics for one of the most failure-prone areas: how autograde results, manual review, reruns, overrides, and grade release interact.

Without a stable semantic model, issue `#10` could persist rerun results in a way that silently changes a grade after manual review, and issue `#11` could implement review and override UX on top of ambiguous authority rules.

The key unresolved questions are:
- which record is authoritative before and after review
- what a rerun is allowed to replace automatically
- when a released grade can change student-visible state
- how overrides relate to future autograde reruns

## Decision

Optimark will separate three related but distinct concepts:
- the latest autograde candidate result
- the current authoritative grade decision
- the current student-visible released grade

The shared grading-semantics contracts are represented at:
- [coding_grading.py](../../backend/packages/contracts/src/optimark_clio/coding_grading.py)

### Authoritative source of truth

`GradeRecord` remains the authoritative grading object for anything student-visible or operationally final.

The authoritative grade may originate from:
- `autograde`
- `review_adjustment`
- `manual_override`

Autograde output alone is not the final truth. It is a candidate input to a grade decision unless staff policy and workflow allow it to stand unchanged.

### Review and override semantics

The coding review state is explicitly modeled as:
- `pending_autograde`
- `ready_for_review`
- `reviewed`
- `overridden`

Override semantics are stricter than ordinary review adjustment:
- `reviewed` means staff accepted or adjusted the grading outcome in a normal review path
- `overridden` means staff intentionally replaced the grading outcome with a manual decision that should not be interpreted as an ordinary autograde-derived result

When the review state is `overridden`, the authoritative source must be `manual_override`.

### Release semantics

Release is separate from review completion.

The release-state model is:
- `unreleased`
- `released`

When a grade is released:
- there must already be an authoritative `GradeRecord`
- the student-visible grade must point to that same authoritative record
- students continue to see the last released record until staff explicitly replace it through a new release decision

This means a newly completed rerun does not automatically alter student-visible state just because fresher autograde data exists.

### Rerun semantics

Reruns must not silently destroy review history or mutate released grades in place.

The design defines three core rerun scenarios:

1. `pre_release_unreviewed`
   - outcome: `replace_candidate_only`
   - semantics:
     - the latest autograde candidate may be replaced automatically
     - no student-visible state changes
     - no prior authoritative reviewed decision is being overwritten

2. `pre_release_reviewed`
   - outcome: `require_review_reconciliation`
   - semantics:
     - the new autograde result becomes a fresh candidate
     - the prior authoritative grade stays authoritative until staff reconcile the rerun
     - reviewer action is required before the authoritative grade changes

3. `post_release`
   - outcome: `preserve_released_grade`
   - semantics:
     - the newly completed rerun does not automatically replace the released grade
     - the current released grade remains student-visible
     - staff must explicitly reconcile and re-release if they want the rerun to supersede the published decision

### Operational interpretation

These semantics imply:
- the system may track fresher autograde candidates than the current authoritative grade
- reruns can create "pending reconciliation" state without changing what students see
- review and release actions are explicit transitions, not side effects of autograde completion
- a superseded grade should be recorded through a new authoritative decision, not by mutating historical review intent out of existence

## Consequences

### Positive

- Gives issue `#10` a safe rerun model that avoids destructive grade mutations.
- Gives issue `#11` a clear contract for review, override, and release UX.
- Preserves auditability by separating candidate autograde results from authoritative and student-visible grade state.
- Keeps post-release reruns non-destructive unless staff explicitly adopt them.

### Negative

- Introduces extra semantic state compared with a naive "latest run wins" model.
- Requires reconciliation flows in later product work instead of allowing silent autograde replacement.

### Follow-on implications

- Issue `#10` should persist the latest autograde candidate separately from the authoritative released grade decision.
- Issue `#11` should expose reviewer actions that deliberately reconcile reruns rather than auto-applying them.
- Gradebook and student-facing surfaces should distinguish unreleased candidate changes from released results.

## Explicit Non-Decisions

This ADR does not decide:
- institution-specific late-policy workflows
- whether releases happen per submission, per assignment, or in bulk from the final gradebook UX
- rubric structure or comment-thread UI details
