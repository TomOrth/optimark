# Optimark AI-Optimized Product and Architecture Spec

## Document Status
- Status: Draft
- Scope: Overall product direction and system architecture
- Audience: Founders, engineers, and coding agents contributing to Optimark
- Canonical for: v1 product framing, repo structure, domain boundaries, and coding-assignment architecture constraints

## Related ADRs
- [ADR-0001: Core Product and Technology Stack](./adr/0001-core-product-and-technology-stack.md)
- [ADR-0002: Modular Monolith Backend with Separate Worker](./adr/0002-modular-monolith-backend-with-worker.md)
- [ADR-0003: Generic Assessment Domain with Coding as a Specialized Assignment Type](./adr/0003-generic-assessment-domain.md)
- [ADR-0004: Contract-Driven Coding Submission Engine](./adr/0004-contract-driven-coding-engine.md)
- [ADR-0005: Hosted SaaS First with Self-Hosting Seams](./adr/0005-hosted-saas-first.md)
- [ADR-0007: Backend uv Workspace Package Topology](./adr/0007-backend-uv-workspace-package-topology.md)

## 1. Product Summary
Optimark is an instructor-first assessment platform that begins with coding assignments and autograding, while intentionally preserving a path to broader assessment workflows similar to Gradescope. The first release should serve CS instructors, TAs, and students, but the core domain model must remain generic enough to support non-coding assignments later.

The first flagship feature is coding assignments where:
- instructors create and publish assignments
- students submit code artifacts
- the system runs asynchronous grading workflows
- instructors and TAs can review, override, and release grades

The near-term platform expansion path is:
1. Coding assignments
2. File/PDF submissions
3. Quizzes and exams

## 2. Product Principles
Use these as hard constraints for design and implementation.

1. Instructor-first, not student-consumer-first.
2. Hosted SaaS first, but avoid architectural dead ends that block future self-hosting.
3. Generic assessment model first, coding specialization second.
4. Async grading lifecycle is a core platform capability, not a side feature.
5. Manual review and rubric feedback are first-class, even for autograded work.
6. The coding execution engine must be designed behind a stable contract and must not be prematurely locked to one sandbox/runtime architecture.

## 3. v1 Goals
- Support course-based assessment workflows for instructors, TAs, and students.
- Allow instructors to create coding assignments for Python-first submissions.
- Support student submission upload and resubmission flows.
- Support background autograding with persistent run status and results.
- Support manual review, rubric feedback, score overrides, and grade release.
- Provide instructor and student read surfaces for submissions and grades.

## 4. Explicit Non-Goals for v1
- Full LMS feature parity
- Institution-wide compliance or procurement-focused administration
- Full multi-language execution support
- Final decision on sandbox/runtime execution technology
- Rich inline code annotation tooling
- Production self-hosted packaging

## 5. Primary Users
### Instructor
- Creates courses and assignments
- Publishes assessment configuration
- Monitors submissions and grading progress
- Reviews and overrides grades

### TA
- Assists with submission review and grading
- Leaves rubric and feedback comments
- Operates within instructor-defined permissions

### Student
- Enrolls in courses
- Views assigned work
- Uploads submissions
- Monitors grading state
- Views released scores and feedback

## 6. Product Surface Area
The v1 application should include these areas:

### Course management
- courses
- enrollments
- instructor/TA/student roles

### Assignment management
- draft and published assignments
- due date metadata
- assignment versions
- coding-assignment configuration

### Submission workflow
- file or archive upload
- submission history
- submission status tracking
- resubmission support

### Evaluation workflow
- autograde run creation
- autograde lifecycle tracking
- normalized result persistence
- review and override path

### Grade presentation
- submission detail views
- gradebook summary views
- student-visible released results

## 7. Canonical Technical Decisions
These decisions are considered settled unless explicitly revised.

### Frontend
- Runtime/package manager: Bun
- Framework: React
- Routing: TanStack Router
- Data fetching/cache: TanStack Query
- App type: SPA

### Backend
- Language/runtime: Python
- Workspace manager: uv workspaces
- Web framework: FastAPI
- Architecture shape: modular monolith with a separate worker process

### Data and infrastructure
- Primary database: Postgres
- Queue/background coordination: Redis
- Artifact storage: object storage abstraction with local S3-compatible development support

### Deployment bias
- Hosted SaaS first
- Preserve abstraction seams for future self-hosted deployment

## 8. Recommended Repository Layout
```text
optimark/
  frontend/
  backend/
    apps/
      api/
      worker/
    packages/
      domain/
      db/
      contracts/
  docs/
```

### Layout intent
- `frontend/`: web app for instructors, TAs, and students
- `backend/apps/api`: FastAPI HTTP API
- `backend/apps/worker`: background worker for submission processing and grading orchestration
- `backend/packages/domain`: business rules, domain types, state transitions
- `backend/packages/db`: persistence models, repositories, migrations
- `backend/packages/contracts`: API payloads and worker contract schemas

## 9. System Architecture
Optimark should be implemented as a modular monolith with explicit domain and infrastructure boundaries.

### Core runtime pieces
- React SPA frontend
- FastAPI API service
- Background worker service
- Postgres database
- Redis queue
- Object storage

### High-level request flow
1. Instructor or student interacts with the SPA.
2. SPA calls FastAPI endpoints.
3. API persists domain state in Postgres.
4. API stores or references uploaded artifacts in object storage.
5. API enqueues grading-related background work in Redis.
6. Worker processes submission jobs and updates autograde state.
7. API exposes updated status and final results back to the SPA.

## 10. Core Domain Model
These entities should anchor the platform. Avoid designing coding-specific tables that bypass them.

### User
- platform identity
- authentication linkage

### Course
- instructional container for assignments and enrollments

### Enrollment
- links user to course
- role enum: `instructor | ta | student`

### Assignment
- generic assessment unit
- `assignment_type` enum initially supports `coding`
- reserve future support for `document` and `quiz`

### AssignmentVersion
- immutable configuration snapshot used for evaluation consistency

### Submission
- student submission record tied to an assignment version
- source of truth for submission status

### SubmissionArtifact
- uploaded code archive/files
- generated outputs/log attachments

### AutogradeRun
- one asynchronous grading attempt
- stores lifecycle state and normalized result payload

### Rubric / RubricItem
- structured review and manual scoring framework

### GradeRecord
- authoritative grade state
- tracks autograde-derived values, manual override or adjustment, and released grade state

### FeedbackComment
- reviewer-authored feedback attached to a submission or rubric item

## 11. Domain Modeling Rules
1. Common assessment workflow belongs in generic entities, not coding-specific tables.
2. Coding-specific settings should extend `Assignment` through typed configuration, not replace the model.
3. `AssignmentVersion` is required to evaluate against stable published config.
4. `AutogradeRun` is not the same thing as the final grade.
5. `GradeRecord` is the authoritative student-facing grading object.

## 12. Core State Models
These state models should guide implementation and tests.

### Assignment status
- `draft`
- `published`
- `archived`

### Submission status
- `draft`
- `submitted`
- `queued`
- `running`
- `completed`
- `failed`

### Autograde run status
- `queued`
- `running`
- `completed`
- `failed`

### Grade release status
- `unreleased`
- `released`

## 13. Coding Assignment v1 Scope
The first coding-assignment implementation should support:
- Python-first execution
- starter materials
- submission artifacts
- asynchronous autograde processing
- result storage
- instructor and TA review
- rubric feedback
- manual score overrides

### Coding assignment fields to plan for
- title
- description
- due date
- submission limit
- starter artifact references
- language = `python`
- scoring configuration placeholder

## 14. Coding Engine Boundary
This is intentionally constrained. The product must define the contract and lifecycle, but not finalize the sandbox/runtime architecture yet.

### Must define now
- runner input shape
- runner output shape
- error semantics
- lifecycle integration points
- persistence model for run status and results

### Must not define yet
- Docker vs Firecracker vs VM vs other isolation choice
- final transport/packaging strategy for all artifact types
- final horizontal scaling strategy
- broad multi-language implementation details

## 15. Runner Contract Requirements
The future coding runner interface must support:

### Inputs
- submission artifact references
- assignment version reference
- execution metadata
- grading configuration reference

### Outputs
- normalized status
- numeric score or score components
- testcase summary
- logs or artifact references
- machine-readable failure information

### Contract properties
- Python-first, future language-extensible
- stable enough for API and worker integration
- independent of the final sandbox/runtime implementation

## 16. Grade Semantics
These rules should guide future implementation and design work.

1. Autograde output informs grading but is not always the final grade.
2. Manual review can adjust or override the result.
3. Released grades are a distinct state from computed grades.
4. Reruns must not silently destroy review history.
5. Student-visible data must be separated from staff-only grading state.

## 17. API Design Direction
Use FastAPI OpenAPI as the source of truth and generate a typed frontend client from it.

### Initial route groups
- `/api/v1/auth/*`
- `/api/v1/courses`
- `/api/v1/courses/{course_id}/enrollments`
- `/api/v1/courses/{course_id}/assignments`
- `/api/v1/assignments/{assignment_id}`
- `/api/v1/assignments/{assignment_id}/submissions`
- `/api/v1/submissions/{submission_id}`
- `/api/v1/submissions/{submission_id}/artifacts`
- `/api/v1/submissions/{submission_id}/autograde-runs`
- `/api/v1/submissions/{submission_id}/grade`
- `/api/v1/assignments/{assignment_id}/gradebook`

### API principles
- role-aware access control
- predictable status enums
- no frontend-only data contracts
- generic assessment model exposed cleanly

## 18. Frontend Architecture Direction
The frontend should be organized around route groups and shared data access, not page-local one-off logic.

### Route groups
- auth
- instructor course dashboard
- assignment management
- student assignment detail and submission
- submission detail
- grading and review
- gradebook

### Frontend architectural rules
1. TanStack Router owns navigation and route composition.
2. TanStack Query owns server-state fetching and mutation coordination.
3. API contracts should be typed from backend schemas when possible.
4. Instructor, TA, and student views may share layouts but must not share permission assumptions.

## 19. Backend Architecture Direction
The backend should start as a modular monolith.

### Why modular monolith first
- fastest path to product delivery
- lower coordination overhead than microservices
- easier domain consistency
- clean enough to split later if justified

### Internal backend boundaries
- HTTP layer
- domain/application services
- persistence/repositories
- contracts/schemas
- background job handlers

## 20. Security and Isolation Baselines
These are guiding constraints even before the final execution engine is chosen.

### Product security baseline
- strict role-based access control
- audit-friendly grade overrides
- separation of staff-only and student-visible state
- artifact access controlled through application permissions

### Execution security baseline
- untrusted student code is treated as hostile
- grading execution must occur behind an isolation boundary
- execution artifacts and logs must be scoped to authorized access

## 21. Local Development Requirements
The development environment should support:
- local Postgres
- local Redis
- local S3-compatible object storage
- one-command or one-workflow startup for core services

## 22. Testing Strategy
### Domain tests
- role permissions
- assignment lifecycle rules
- submission state transitions
- grade resolution logic

### API tests
- instructor assignment creation
- student submission creation
- reviewer grading and override flows
- gradebook retrieval

### Worker tests
- queue pickup and state changes
- run persistence
- failure handling

### Frontend integration tests
- instructor creates a coding assignment
- student submits code
- staff reviews and adjusts grade
- student sees released result

## 23. Delivery Sequence
This is the recommended implementation order.

1. Monorepo scaffolding
2. Local dev stack
3. FastAPI backend bootstrap
4. React SPA bootstrap
5. Auth and role model
6. Core academic domain
7. Generic assessment domain
8. Instructor assignment management
9. Student submission flow
10. Autograde lifecycle orchestration
11. Review and override workflow
12. Gradebook and submission detail views

## 24. Open Design Threads
These remain intentionally open and should be explored through dedicated design work:
- runner contract finalization details
- artifact packaging and handoff model
- grading semantics for reruns and release policy
- isolation and scaling strategy for execution workers

## 25. Known Expansion Path
After the first coding vertical slice:
1. Add file/PDF submission assessment type
2. Add quizzes and exams
3. Revisit self-hosted and enterprise-oriented architecture needs

## 26. Build Guidance for Future Agents
When implementing against this spec:
- preserve the generic assessment core
- do not bake the coding engine into the core domain without a contract boundary
- prefer explicit enums and typed schemas over ad hoc strings
- keep staff and student authorization paths separate
- avoid introducing microservices unless the modular monolith becomes a clear bottleneck
- do not finalize execution sandbox technology without revisiting the open design issues

## 27. One-Sentence Canonical Summary
Optimark is a hosted, instructor-first assessment platform built as a React/TanStack SPA plus FastAPI modular monolith, with a generic assessment domain and a contract-driven coding submission engine that starts with Python autograding and manual review without prematurely locking the final execution architecture.
