# Backend Workspace

This directory is the uv-managed Python workspace for Optimark.

## Structure
- `apps/api`: FastAPI API application bootstrap
- `apps/worker`: background worker bootstrap
- `packages/domain`: shared business logic
- `packages/db`: persistence models and repositories
- `packages/contracts`: shared API and worker schemas

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
- `make backend-api-dev`
- `make backend-worker-run`
