# Backend Workspace

This directory is the uv-managed Python workspace for Optimark.

## Structure
- `apps/api`: future FastAPI API application
- `apps/worker`: future background worker process
- `packages/domain`: shared business logic
- `packages/db`: persistence models and repositories
- `packages/contracts`: shared API and worker schemas

This issue creates the workspace boundaries only. Framework bootstrapping and application code are handled in later implementation issues.

