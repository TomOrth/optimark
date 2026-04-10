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

The backend also now includes the first auth and authorization slice for:
- email/password identities
- opaque server-backed sessions
- course capability checks derived from enrollment roles

This foundation is still intentionally backend-led. It establishes persistence, domain services, shared contracts, and hosted-app auth/session routes for later frontend auth, assessment, and course-management issues.

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

## Auth routes and settings
The API now exposes these hosted-auth routes:
- `POST /api/v1/auth/signup`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/session`

The root `.env.example` also includes session-cookie configuration for local and deployed environments:
- `BACKEND_AUTH_SESSION_COOKIE_NAME`
- `BACKEND_AUTH_SESSION_TTL_DAYS`
- `BACKEND_AUTH_SESSION_COOKIE_SECURE`
- `BACKEND_AUTH_SESSION_COOKIE_SAME_SITE`
