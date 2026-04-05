# ADR-0002: Modular Monolith Backend with Separate Worker

- Status: Accepted
- Date: 2026-04-05

## Context
Optimark needs:
- a web API for authenticated product workflows
- asynchronous processing for grading-related work
- clean domain boundaries for future growth

The product is still early, so splitting into many services would introduce operational overhead before the domain is stable. At the same time, grading and submission processing cannot be purely synchronous inside the HTTP request path.

## Decision
The backend will start as a modular monolith with:
- one FastAPI API application
- one separate worker process for background jobs
- shared backend packages for domain logic, persistence, and contracts

Recommended structure:
- `backend/apps/api`
- `backend/apps/worker`
- `backend/packages/domain`
- `backend/packages/db`
- `backend/packages/contracts`

## Consequences
### Positive
- Keeps the initial architecture simple and fast to iterate on.
- Supports asynchronous grading and submission processing without committing to microservices.
- Encourages domain-level reuse between API and worker paths.
- Reduces consistency problems compared with early service decomposition.

### Negative
- Requires discipline to preserve clean module boundaries inside one codebase.
- May eventually need decomposition if product scale or operational complexity grows substantially.

### Follow-on implications
- Domain rules should live in shared packages, not inside HTTP handlers.
- Worker flows should use the same contracts and persistence layer concepts as the API.
- Background lifecycle state must be represented explicitly in the database rather than inferred from worker memory.
