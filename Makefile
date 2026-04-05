.PHONY: help frontend-install frontend-dev backend-sync backend-lock

help:
	@printf "%s\n" \
	"Optimark workspace commands" \
	"" \
	"  make frontend-install  Install Bun dependencies for the frontend workspace" \
	"  make frontend-dev      Run the frontend workspace dev script" \
	"  make backend-sync      Sync the uv backend workspace" \
	"  make backend-lock      Refresh the backend uv lockfile"

frontend-install:
	cd frontend && bun install

frontend-dev:
	cd frontend && bun run dev

backend-sync:
	cd backend && uv sync --all-packages

backend-lock:
	cd backend && uv lock

