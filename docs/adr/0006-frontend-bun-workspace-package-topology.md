# ADR-0006: Frontend Bun Workspace Package Topology

- Status: Accepted
- Date: 2026-04-05

## Context
Optimark's frontend started as a single Bun-managed React SPA. As soon as the routed shell, mockup-inspired surfaces, and shared shell language landed, it became clear that the frontend would benefit from the same explicit workspace boundaries already used in the backend.

The product direction implies several distinct kinds of frontend concerns:
- one primary web application for instructors, TAs, and students
- shared brand, shell, and UI primitives that should not live inside a single app
- user-facing system messaging and notification behaviors that will span multiple screens
- shared tooling and code generation glue that should not be coupled to app runtime code
- a future environment for documenting components and flows without mixing that work into the production app

Without package boundaries, these concerns would accumulate inside one app package and make later extraction more expensive.

## Decision
The frontend will use a Bun workspace rooted at `frontend/` with `apps/*` and `packages/*` package groups.

The current and planned package topology is:
- `apps/apollo`: the primary React SPA
- `packages/calliope`: shared brand tokens, shell copy, theme constants, and future reusable UI primitives
- `packages/iris`: planned package for notifications, inbox-style messaging, and other user-facing system signals
- `packages/hephaestus`: planned package for shared frontend tooling and config, including environment helpers, lint/build presets, and code generation glue
- `apps/museion`: planned internal pattern-library or Storybook-style workspace for documenting components, states, and flows

### Package intent
#### `apps/apollo`
`apollo` is needed as the production application boundary. It owns routing, page composition, app runtime wiring, and product workflows for instructors, TAs, and students. Keeping it as an app package makes it easier to grow the product without mixing application runtime concerns into shared packages.

#### `packages/calliope`
`calliope` is needed to hold presentation-layer primitives that should remain reusable across the frontend. This starts with brand and shell constants, but should grow into shared UI primitives, layout conventions, and design-language helpers. Pulling these out early prevents the main app from becoming the only place where visual consistency is defined.

#### `packages/iris`
`iris` is needed because notifications, toasts, inbox items, activity signaling, and cross-surface user messaging are product concerns that cut across many pages. Keeping them in a dedicated package avoids duplicating event-display patterns across feature areas and creates a clear home for delivery semantics that are broader than any single route.

#### `packages/hephaestus`
`hephaestus` is needed to keep tooling concerns separate from runtime code. Frontend code generation, shared Vite or TypeScript presets, environment helpers, and other build-time utilities are important, but they should not be imported from the product app or UI package by accident. A dedicated tooling package keeps those concerns explicit and easier to evolve.

#### `apps/museion`
`museion` is needed as the eventual documentation and design-validation surface for the frontend system. As Optimark's UI grows, engineers and designers will benefit from a dedicated place to review components, route fragments, loading states, and edge cases outside the production app. Keeping that workspace separate prevents internal documentation tooling from leaking into the shipping application.

## Consequences
### Positive
- Creates a frontend structure that mirrors the backend's workspace-oriented architecture.
- Establishes clear seams between runtime app code, shared UI concerns, system messaging, tooling, and documentation.
- Makes it cheaper to introduce code generation, shared components, or future frontend surfaces without large refactors.
- Gives the repository a clearer place for frontend architectural ownership instead of letting the main app absorb every concern.

### Negative
- Adds workspace complexity earlier than a single-app frontend strictly requires.
- Introduces planned packages before their implementation is complete, which requires discipline to keep the package map intentional rather than ornamental.

### Follow-on implications
- New shared UI or shell primitives should default to `calliope` unless they are clearly app-local.
- Notification and inbox workflows should prefer `iris` once implemented instead of being recreated inside `apollo`.
- Frontend build/config helpers should prefer `hephaestus` once implemented instead of accumulating in app-level scripts.
- Component documentation and UI validation work should prefer `museion` once implemented instead of adding internal-only surfaces to the production app.
