# Optimark

Optimark is an instructor-first assessment platform starting with coding assignments, asynchronous autograding, and manual review workflows. This repository is currently in the foundation phase and is organized as a monorepo so the frontend and backend can evolve independently while staying in one codebase.

## Current status

The repository currently includes:

- a Bun-managed React SPA with TanStack Router, TanStack Query, and a shared app shell
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
    apps/
      apollo/
    packages/
      calliope/
    package.json
  Makefile
```

## Workspace responsibilities

### `frontend/`

- Bun-managed frontend workspace
- `apps/apollo`: routed React SPA for instructors, TAs, and students
- `packages/calliope`: shared frontend theme and shell copy package
- Planned next frontend packages:
  `packages/iris` for notifications and messaging,
  `packages/hephaestus` for shared tooling/config,
  and `apps/museion` for a pattern-library workspace
- Includes the initial routed SPA, shared shell, and mockup-inspired scaffold screens

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
make ci
make tooling-install
make frontend-install
make frontend-dev
make backend-sync
make backend-db-upgrade
make backend-api-dev
make backend-worker-run
```

The frontend now boots a real routed SPA with a shared workspace shell, while the backend includes a minimal FastAPI and worker bootstrap for upcoming product work.

The backend academic foundation now includes persisted `User`, `Course`, and `Enrollment` models plus Alembic migrations for bootstrapping the schema.

## Quality checks

The baseline CI workflow runs on pull requests, pushes to `main`, and tag pushes. It validates the current monorepo quality gate:

- frontend dependency install, typecheck, and build
- backend uv sync, Ruff linting, and pytest smoke tests

On push events, CI also builds and publishes the frontend and backend container images.

Run the same setup and checks locally with one command:

```sh
make ci
```

`make ci` installs frontend dependencies with `--frozen-lockfile`, syncs the backend workspace with `--frozen`, and then runs the same frontend and backend quality gates as GitHub Actions.

## Containers

Optimark publishes two application images to GitHub Container Registry:

- `ghcr.io/tomorth/optimark-frontend`
- `ghcr.io/tomorth/optimark-backend`

Pushes to `main` publish images tagged `latest`; tag pushes publish images with the Git tag. The publish job uses Docker Hardened Images base images from `dhi.io`, so the repository must define `DHI_USERNAME` and `DHI_TOKEN` secrets that can pull those base images. Published images are scanned with Trivy, and SARIF vulnerability reports are uploaded to GitHub code scanning for review.

Build the images locally from the repository root:

```sh
docker build -f frontend/Dockerfile -t optimark-frontend .
docker build -f backend/Dockerfile -t optimark-backend .
```

Run the containers locally:

```sh
docker run --rm -p 4173:4173 optimark-frontend
docker run --rm -p 8000:8000 optimark-backend
```

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

## Commit convention

This repository uses Conventional Commits for both commit messages and PR titles so history stays clean and changelog-friendly.

Examples:
- `feat(frontend): add protected app shell`
- `fix(api): handle missing submission id`
- `docs(adr): document backend uv workspace topology`

See [CONTRIBUTING.md](CONTRIBUTING.md) for the supported types and workflow details.
Run `make tooling-install` or `bun install` at the repository root at least once so Husky hooks are installed locally.
