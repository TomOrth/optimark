# Frontend Workspace

This workspace contains the Bun frontend monorepo for Optimark.

## Stack
- Bun
- React
- TanStack Router
- TanStack Query
- Vite

## Commands
- `bun install`
- `bun run dev`
- `bun run build`
- `bun run check`
- `bun run preview`

The Apollo Vite dev server proxies `/api` requests to `http://127.0.0.1:8000` so the cookie-backed auth flow works locally without adding broad frontend CORS logic.

## Workspace Layout
- `apps/apollo`: main React SPA
- `packages/calliope`: shared frontend design-system package for tokens, shell primitives, and reusable surface patterns

## Package Roadmap
- `apps/apollo`: implemented
  Primary web application for instructors, TAs, and students.
- `packages/calliope`: implemented
  Shared brand tokens, shell primitives, layout scaffolds, and reusable surface patterns derived from the design mockups in `docs/mockups/`.
- `packages/iris`: planned
  Notifications, toasts, inbox-style messaging, and other user-facing system signals.
- `packages/hephaestus`: planned
  Shared frontend tooling and config such as lint/build presets, environment helpers, and code generation glue.
- `apps/museion`: planned
  Internal pattern library or Storybook-style workspace for documenting components, flows, and visual decisions.

The current implementation provides a mockup-aligned design system in `calliope` plus a routed Apollo app that now includes login, signup, session restoration, protected route gating, logout behavior, and showcase surfaces for future instructor and student flows.
