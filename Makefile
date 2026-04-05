.PHONY: help tooling-install frontend-install frontend-dev backend-sync backend-lock backend-api-dev backend-worker-run dev-services-up dev-services-down dev-services-reset dev-services-logs

help:
	@printf "%s\n" \
	"Optimark workspace commands" \
	"" \
	"  make dev-services-up   Start Postgres, Redis, and SeaweedFS for local development" \
	"  make dev-services-down Stop the local development services" \
	"  make dev-services-reset Stop and remove local development service volumes" \
	"  make dev-services-logs Tail logs for the local development services" \
	"  make tooling-install   Install repo-level tooling such as Husky and commitlint" \
	"  make frontend-install  Install repo tooling and Bun dependencies for the frontend workspace" \
	"  make frontend-dev      Run the frontend workspace dev script" \
	"  make backend-sync      Sync the uv backend workspace" \
	"  make backend-lock      Refresh the backend uv lockfile" \
	"  make backend-api-dev   Run the FastAPI backend app with reload" \
	"  make backend-worker-run Run the worker bootstrap command"

dev-services-up:
	docker compose up -d

dev-services-down:
	docker compose down

dev-services-reset:
	docker compose down --volumes --remove-orphans

dev-services-logs:
	docker compose logs -f

tooling-install:
	bun install

frontend-install: tooling-install
	cd frontend && bun install

frontend-dev:
	cd frontend && bun run dev

backend-sync:
	cd backend && uv sync --all-packages

backend-lock:
	cd backend && uv lock

backend-api-dev:
	cd backend && uv run --package athena uvicorn optimark_athena.app:app --reload

backend-worker-run:
	cd backend && uv run --package hermes hermes-worker
