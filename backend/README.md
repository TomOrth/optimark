# Backend Workspace

This directory is the uv-managed Python workspace for Optimark.

## Structure
- `apps/api`: FastAPI API application bootstrap
- `apps/worker`: background worker bootstrap
- `packages/domain`: shared business logic
- `packages/db`: persistence models and repositories
- `packages/contracts`: shared API and worker schemas

## Current backend foundation
The backend now includes the first academic domain slice for:
- `User`
- `Course`
- `Enrollment`

This foundation is intentionally backend-only. It establishes persistence, domain services, and shared contracts for later auth, assessment, and course-management issues without exposing feature routes yet.

## Themed package map
The workspace directories stay descriptive, while the Python packages use an academic assessment theme:
- `athena`: API app
- `hermes`: worker app
- `metis`: shared domain package
- `mnemosyne`: persistence package
- `clio`: shared contracts package

## Local development
Useful commands from the repository root:
- `make backend-sync`
- `make backend-db-upgrade`
- `make backend-db-revision message="describe change"`
- `make backend-api-dev`
- `make backend-worker-run`

The backend uses SQLAlchemy for ORM mappings and Alembic for schema migrations. `make backend-db-upgrade` applies the current schema to `BACKEND_DATABASE_URL`, which defaults to the local Postgres service defined in `.env.example`.
