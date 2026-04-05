# ADR-0001: Core Product and Technology Stack

- Status: Accepted
- Date: 2026-04-05

## Context
Optimark is being built as a new instructor-first assessment platform, starting with coding assignments and autograding while preserving a path to broader assessment workflows. We need a clear default stack and product framing so early implementation work does not fragment across incompatible assumptions.

The project already has these directionally settled inputs:
- instructor-first product
- coding assignments first
- React/TanStack frontend using Bun
- Python backend using FastAPI and uv workspaces
- hosted SaaS initial deployment bias

## Decision
Optimark will be built as:
- a hosted SaaS assessment platform
- focused on course-based workflows for instructors, TAs, and students
- beginning with coding assignments as the first vertical slice

The initial technology stack is:
- Frontend: Bun, React, TanStack Router, TanStack Query
- Backend: Python, uv workspaces, FastAPI
- Primary database: Postgres
- Background work coordination: Redis
- Artifact storage: object storage abstraction with S3-compatible local development support

## Consequences
### Positive
- Establishes a coherent stack for immediate implementation work.
- Aligns frontend and backend choices with strong developer ergonomics.
- Supports the asynchronous grading model required for coding assignments.
- Keeps the platform oriented around structured web application workflows rather than generic document delivery.

### Negative
- Narrows early implementation toward a specific JS and Python ecosystem.
- Requires queue and object storage concerns earlier than a simpler synchronous product might.

### Follow-on implications
- API contracts should be generated or derived from FastAPI as the source of truth when practical.
- Local development must support Postgres, Redis, and object storage.
- The product model must not hard-code coding assignments as the only future assessment type.
