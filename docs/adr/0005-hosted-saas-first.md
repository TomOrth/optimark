# ADR-0005: Hosted SaaS First with Self-Hosting Seams

- Status: Accepted
- Date: 2026-04-05

## Context
The product should launch as a hosted SaaS platform because that is the fastest path to shipping and operating the initial MVP. At the same time, the broader vision includes a possible future need for self-hosting or enterprise-oriented deployment options.

We need to avoid over-investing in enterprise deployment complexity now while also avoiding needless lock-in to hosted-only assumptions.

## Decision
Optimark will optimize for hosted SaaS delivery first, while preserving clear seams that make future self-hosted deployment plausible.

These seams should exist around:
- authentication providers
- object storage
- queue and worker infrastructure
- environment configuration
- deployment-specific operational concerns

Self-hosting is not a v1 delivery target and should not drive the initial feature or infrastructure roadmap.

## Consequences
### Positive
- Keeps the MVP roadmap focused and pragmatic.
- Avoids premature enterprise complexity.
- Makes it easier to revisit self-hosting later without rewriting the whole system.

### Negative
- Some later deployment concerns will still require meaningful work when self-hosting becomes a real priority.
- The team must be intentional about abstraction boundaries rather than relying on future cleanup.

### Follow-on implications
- Local development and production configuration should use replaceable adapters where practical.
- Product decisions should not assume deep institution-specific administration in v1.
- Hosted SaaS remains the default assumption unless a later ADR supersedes this one.
