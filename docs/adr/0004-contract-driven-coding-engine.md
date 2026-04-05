# ADR-0004: Contract-Driven Coding Submission Engine

- Status: Accepted
- Date: 2026-04-05

## Context
The coding submission engine is central to Optimark, but its final execution architecture is still intentionally open. We know the product requires:
- student code submission
- asynchronous grading
- persistent run state
- normalized result storage
- instructor and TA review flows

We do not yet want to finalize:
- sandbox technology
- runtime isolation mechanism
- artifact packaging transport details
- long-term scaling design

Without a stable boundary, the application layer could become tightly coupled to a premature runner implementation.

## Decision
Optimark will define the coding submission engine around a stable runner contract and lifecycle boundary before choosing the final sandbox/runtime implementation.

The application and worker layers must integrate through:
- explicit runner inputs
- explicit runner outputs
- explicit status and failure semantics
- persistent `AutogradeRun` lifecycle state

The initial implementation will be Python-first, but the contract must preserve future language expansion.

## Consequences
### Positive
- Allows product development to proceed without locking the final execution stack.
- Makes grading orchestration, persistence, and review workflows implementable now.
- Reduces the risk of a runner-specific architecture leaking into the entire system.

### Negative
- Some execution details remain unresolved longer.
- Early implementations may need adapters or placeholders before the final engine architecture is chosen.

### Follow-on implications
- `AutogradeRun` must store normalized outputs rather than opaque runner-only state.
- Design work is still required for artifact handoff, rerun semantics, and worker isolation strategy.
- Issues and implementation work should not assume Docker, Firecracker, VMs, or any specific sandbox as a settled choice.
