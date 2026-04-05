# ADR-0007: Backend uv Workspace Package Topology

- Status: Accepted
- Date: 2026-04-05

## Context
Optimark's backend is already committed to Python, FastAPI, and `uv` workspaces, but the workspace shape itself is also an architectural decision. The project needs:
- one API runtime for HTTP product workflows
- one worker runtime for asynchronous grading and submission processing
- shared packages for domain logic, persistence, and contracts
- local iteration speed without prematurely splitting into separately versioned repositories or deployable services

Without an explicit workspace topology, backend code would tend to collect inside one app package, making boundaries between API, worker, domain, persistence, and contracts harder to preserve over time.

The backend also uses themed package names:
- `athena`: API application
- `hermes`: worker application
- `metis`: domain package
- `mnemosyne`: persistence package
- `clio`: contracts package

Those names are already present in the current `uv` workspace and should be explained so they remain intentional rather than becoming opaque trivia.

## Decision
The backend will use a single `uv` workspace rooted at `backend/` with these members:
- `apps/api`
- `apps/worker`
- `packages/domain`
- `packages/db`
- `packages/contracts`

The workspace root will:
- define the shared `uv` workspace membership
- own shared development dependencies used across backend packages
- map themed package names through `tool.uv.sources` so workspace members resolve locally during development

### Package intent
#### `apps/api` -> `athena`
`athena` is the FastAPI runtime package. It owns HTTP request handling, application startup, and API-oriented integration wiring. It should depend on shared packages rather than becoming the home for business logic.

#### `apps/worker` -> `hermes`
`hermes` is the background worker runtime package. It owns async job execution and orchestration concerns that should not run inside the request path. It should share the same domain, persistence, and contract concepts as the API.

#### `packages/domain` -> `metis`
`metis` is the domain package. It exists so business rules, enums, workflow concepts, and model-adjacent logic can be shared without depending on HTTP or persistence concerns.

#### `packages/db` -> `mnemosyne`
`mnemosyne` is the persistence package. It exists to hold database-facing models, repositories, and persistence bootstrap concerns without forcing those details into contracts or domain logic.

#### `packages/contracts` -> `clio`
`clio` is the contracts package. It exists to define API and worker-facing schemas that can be shared across the backend without taking on persistence-specific dependencies.

## Consequences
### Positive
- Creates a backend structure that is modular from the start without requiring microservices.
- Keeps API runtime code and worker runtime code separate while still sharing a single repository and toolchain.
- Gives domain, persistence, and contract code explicit homes instead of allowing them to drift into app packages.
- Makes local development straightforward because `uv sync --all-packages` can prepare the whole backend workspace consistently.
- Preserves the themed package naming while keeping the on-disk directory names descriptive.

### Negative
- Adds one more layer of indirection because package names and directory names are not the same.
- Requires discipline to keep the workspace boundaries meaningful instead of letting one package reach across layers casually.

### Follow-on implications
- New backend packages should only be added when they represent a meaningful architectural boundary, not just a temporary implementation preference.
- Shared backend development tooling should continue to live at the workspace root when it applies to multiple packages.
- Contracts should not depend on persistence-layer types, and app packages should prefer shared packages over duplicating core logic.
