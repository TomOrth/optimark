# Optimark

Optimark is an instructor-first assessment platform starting with coding assignments, asynchronous autograding, and manual review workflows. This repository is currently in the foundation phase and is organized as a monorepo so the frontend and backend can evolve independently while staying in one codebase.

## Current status

The repository currently includes:

- a Bun-ready frontend workspace
- a uv-managed Python backend workspace
- a shared root `Makefile`
- a Docker Compose local development stack for Postgres, Redis, and SeaweedFS
- product and architecture documentation

It still does not implement product UI, API routes, or grading logic.

## Repository layout

```text
optimark/
  backend/
    apps/
      api/
      worker/
    packages/
      contracts/
      db/
      domain/
    pyproject.toml
  docs/
    adr/
    optimark-ai-spec.md
    optimark-ui-brief.md
  frontend/
    package.json
    tsconfig.json
  Makefile
```

## Workspace responsibilities

### `frontend/`

- Bun-managed React application workspace
- Will hold the instructor, TA, and student web application
- App bootstrap and product UI land in later issues

### `backend/`

- uv workspace for Python services and shared packages
- `apps/api`: FastAPI HTTP API bootstrap
- `apps/worker`: worker bootstrap
- `packages/domain`: shared business logic and domain types
- `packages/db`: persistence-layer models and repositories
- `packages/contracts`: API and worker contract schemas

The backend workspace keeps readable directory names while using themed uv package names:

- `athena`: API app
- `hermes`: worker app
- `metis`: domain package
- `mnemosyne`: persistence package
- `clio`: contracts package

### `docs/`

- product and architecture spec
- ADRs
- UI-generation brief for design exploration
- UI mockups

## Getting started

### Prerequisites

- `bun`
- `python3`
- `uv`
- `docker`
- `docker compose`

### Common commands

```sh
make help
cp .env.example .env
make dev-services-up
make frontend-install
make frontend-dev
make backend-sync
make backend-api-dev
make backend-worker-run
```

The frontend commands are still scaffold entrypoints, but the backend workspace now includes a minimal FastAPI and worker bootstrap for upcoming product work.

## Local development services

Optimark uses a local Docker Compose stack for core infrastructure:

- Postgres
- Redis
- SeaweedFS for S3-compatible object storage

Useful commands:

```sh
make dev-services-up
make dev-services-down
make dev-services-reset
make dev-services-logs
```

See [local development stack docs](docs/local-development-stack.md) for connection defaults and service details.

## Related planning docs

- [AI spec](docs/optimark-ai-spec.md)
- [UI generation brief](docs/optimark-ui-brief.md)
- [ADR index](docs/adr/README.md)
- [Local development stack](docs/local-development-stack.md)
- [UI Mockups](docs/mockups)
