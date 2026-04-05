# Optimark

Optimark is an instructor-first assessment platform starting with coding assignments, asynchronous autograding, and manual review workflows. This repository is currently in the foundation phase and is organized as a monorepo so the frontend and backend can evolve independently while staying in one codebase.

## Current status
This issue scaffolds the workspace layout only. It creates:
- a Bun-ready frontend workspace
- a uv-managed Python backend workspace
- a shared root entrypoint via `Makefile`
- documentation describing how the repository is organized

It does not yet implement product UI, API routes, or grading logic.

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
- `apps/api`: future FastAPI HTTP API
- `apps/worker`: future background worker
- `packages/domain`: shared business logic and domain types
- `packages/db`: persistence-layer models and repositories
- `packages/contracts`: API and worker contract schemas

### `docs/`
- product and architecture spec
- ADRs
- UI-generation brief for design exploration

## Getting started
### Prerequisites
- `bun`
- `python3`
- `uv`

### Common commands
```sh
make help
make frontend-install
make frontend-dev
make backend-sync
```

At this stage, the frontend and backend commands are scaffold entrypoints rather than full application bootstraps.

## Related planning docs
- [AI spec](docs/optimark-ai-spec.md)
- [UI generation brief](docs/optimark-ui-brief.md)
- [ADR index](docs/adr/README.md)

