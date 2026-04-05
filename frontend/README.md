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

## Workspace Layout
- `apps/apollo`: main React SPA
- `packages/calliope`: shared frontend theme and UI copy package

## Package Roadmap
- `apps/apollo`: implemented
  Primary web application for instructors, TAs, and students.
- `packages/calliope`: implemented
  Shared brand tokens, shell copy, and the first seam for reusable UI primitives.
- `packages/iris`: planned
  Notifications, toasts, inbox-style messaging, and other user-facing system signals.
- `packages/hephaestus`: planned
  Shared frontend tooling and config such as lint/build presets, environment helpers, and code generation glue.
- `apps/museion`: planned
  Internal pattern library or Storybook-style workspace for documenting components, flows, and visual decisions.

The current implementation provides the initial app shell and mockup-inspired route scaffolding for future instructor and student flows. The dashboard and assignment editor screens are intentionally scaffold-grade, while the rest of the route tree is ready for issue-focused product work.
