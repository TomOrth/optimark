# Architecture Decision Records

This directory contains the formal Architecture Decision Records (ADRs) for Optimark.

## Status conventions
- `Proposed`: discussed and preferred, but still open to revision
- `Accepted`: approved as the current default
- `Superseded`: replaced by a newer ADR

## Current ADRs
- [ADR-0001: Core Product and Technology Stack](./0001-core-product-and-technology-stack.md)
- [ADR-0002: Modular Monolith Backend with Separate Worker](./0002-modular-monolith-backend-with-worker.md)
- [ADR-0003: Generic Assessment Domain with Coding as a Specialized Assignment Type](./0003-generic-assessment-domain.md)
- [ADR-0004: Contract-Driven Coding Submission Engine](./0004-contract-driven-coding-engine.md)
- [ADR-0005: Hosted SaaS First with Self-Hosting Seams](./0005-hosted-saas-first.md)
- [ADR-0006: Frontend Bun Workspace Package Topology](./0006-frontend-bun-workspace-package-topology.md)
- [ADR-0007: Backend uv Workspace Package Topology](./0007-backend-uv-workspace-package-topology.md)
- [ADR-0008: Runner Contract for Coding Submissions](./0008-runner-contract-for-coding-submissions.md)
- [ADR-0009: Artifact Packaging and Execution Handoff for Coding Runs](./0009-artifact-packaging-and-execution-handoff.md)
<<<<<<< HEAD
- [ADR-0010: Docker-First Execution Isolation and Scaling Strategy](./0010-docker-first-execution-isolation-and-scaling.md)
=======
- [ADR-0010: Grading Semantics for Reruns, Overrides, and Grade Release](./0010-grading-semantics-for-reruns-overrides-and-release.md)
>>>>>>> main

## Usage
- Create a new ADR when making a meaningful architectural or product-platform decision.
- Do not silently rewrite prior decisions; supersede them with a new ADR if needed.
- Keep implementation details in issue specs and design docs unless they materially affect architecture.
