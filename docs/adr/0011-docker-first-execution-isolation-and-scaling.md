# ADR-0010: Docker-First Execution Isolation and Scaling Strategy

- Status: Accepted
- Date: 2026-05-09

## Context

ADR-0004, ADR-0008, and ADR-0009 intentionally kept the execution runtime open while Optimark defined the runner contract and artifact handoff semantics first.

That sequencing was correct, but the next implementation phase now needs an actual operating assumption for issue `#10` and the first real execution worker. Without a concrete decision, the team still cannot answer several practical questions:
- where artifact preparation happens relative to execution
- how a single autograde run maps to host resources
- what concurrency controls and failure isolation should look like
- which observability and security controls are required in the first production-ready worker path

Issue `#16` originally framed this as a decision framework rather than a final platform choice. We are intentionally going one step further here because the product now has enough context to choose the initial route without blocking future evolution.

The key product and operational constraints are:
- student code is untrusted and must be treated as hostile
- the MVP is Python-first, not broad multi-language from day one
- the product is hosted-SaaS-first, with self-hosting seams preserved where practical
- the team needs a path that is realistic for a small engineering organization to implement and operate soon
- the contract and handoff layers should remain stable even if the underlying isolation mechanism changes later

## Decision

Optimark will use hardened ephemeral Docker containers as the initial execution isolation boundary for coding runs.

This is the selected MVP route, not a permanent claim that Docker is the final best answer for all future scale and threat models.

### Why Docker first

Docker is the best current fit for the first execution system because it offers the strongest balance of:
- implementation speed
- operational familiarity
- acceptable isolation for an MVP when combined with strict hardening
- low-friction local development parity
- a clean migration path behind the already-defined runner and handoff contracts

Compared with the alternatives:
- Firecracker provides stronger isolation characteristics, but it adds meaningful complexity in image management, VM boot orchestration, filesystem staging, networking, and host operations before the product has validated its workload shape.
- Full VM-based execution provides strong isolation but is the least efficient option for cold start time, density, and cost in the MVP stage.
- Docker lets the team deliver real isolated execution now while preserving a future path to Firecracker or another stronger boundary if the product or threat model demands it.

### Execution model

The initial worker architecture will use:
- one background orchestration worker tier that owns run state, artifact handoff resolution, retries, and queue coordination
- one execution-host tier that launches one ephemeral container per autograde run
- one run per container, with no container reuse across student submissions

Artifact flow:
- the worker reads the execution handoff contract from ADR-0009
- the worker materializes a prepared execution workspace outside the container
- the worker launches the container against that prepared workspace
- the runner inside the container produces normalized result artifacts and terminal output for the worker to persist

This keeps artifact staging and runner contract handling outside the container while making the execution environment itself disposable.

### Required hardening baseline

Docker is acceptable only with a strict hardening baseline. The initial execution system must enforce:
- non-root execution inside the container
- a read-only container root filesystem wherever practical
- a dedicated writable scratch/output mount per run
- no mounted Docker socket or equivalent host-control channel
- no cloud-provider instance credentials inside the execution container
- network egress disabled by default for student code
- CPU, memory, process-count, and wall-clock limits per run
- per-run filesystem size limits and cleanup guarantees
- isolated temp directories and artifact paths per run
- explicit allowlisting for any grader-controlled network requirement rather than open outbound access

### Scaling model

The initial scaling strategy will be queue-driven horizontal scaling over a pool of execution hosts.

Concurrency should be managed by explicit host budgets rather than by “as many containers as possible” behavior. Each host should advertise or be configured with a safe concurrency limit derived from:
- CPU cores
- memory capacity
- expected Python-run workload shape
- staging disk availability
- acceptable noisy-neighbor risk

The worker system should scale by:
- increasing or decreasing the number of execution hosts
- tuning per-host concurrency ceilings
- separating orchestration workers from execution hosts if queue pressure and runtime pressure diverge

This gives the MVP a simple and predictable capacity model:
- queue depth measures backlog
- host count measures parallel capacity
- per-host concurrency caps constrain failure blast radius

### Failure isolation expectations

The chosen route must assume:
- a failed student run can consume its own container budget but should not crash unrelated runs
- host-level failures may lose in-flight runs on that host, so run state and retry policy must live outside the container
- the worker must treat container startup failures, timeout failures, and host-capacity failures as explicit infrastructure events that map back into the normalized failure taxonomy from ADR-0008

### Observability requirements

The execution system must expose enough telemetry to support both debugging and capacity planning. At minimum, track:
- queue wait time
- workspace preparation time
- container start latency
- run duration
- timeout rate
- infrastructure-error rate
- per-host concurrent run count
- per-run resource usage where available
- artifact staging failures
- retry volume and retry outcome

### Why not Firecracker now

Firecracker remains the most likely future upgrade path if Optimark needs materially stronger multi-tenant isolation. We are not choosing it first because:
- it would slow the path to the first production-capable autograde engine
- it introduces more host-operations surface area before the workload is proven
- the current contracts already let us defer that complexity without blocking product progress

### Upgrade triggers

This ADR should be revisited if one or more of these become true:
- the product serves a larger multi-tenant hosted customer base with higher isolation expectations
- security review concludes container hardening is insufficient for the threat model
- compliance, enterprise procurement, or institutional review requires VM-class isolation
- noisy-neighbor or kernel-shared runtime risk becomes a material operational issue
- container escape risk is judged too high relative to company risk tolerance

If those triggers occur, the preferred next evaluation path is Firecracker-style microVM execution behind the same runner and handoff contracts.

## Consequences

### Positive

- Unblocks issue `#10` with a concrete execution target.
- Keeps the execution path realistic for a small team to build and operate.
- Preserves local-development and production-parity advantages.
- Uses the existing contract and handoff layers as intended instead of bypassing them.
- Creates a clear migration story instead of a vague “we will decide later” position.

### Negative

- Docker is a weaker isolation boundary than microVMs against kernel-level threats.
- Hardening discipline becomes part of the product’s security posture rather than an optional extra.
- A later migration to Firecracker or another stronger boundary may still be necessary.

### Follow-on implications

- Issue `#10` should build a Docker-backed executor path first.
- Issue `#14` prepared-workspace flow is now the default operational path for execution staging.
- Local development should support the same basic container-launch flow used in production workers.
- Future security work should codify container hardening and host isolation assumptions in operational runbooks.

## Explicit Non-Decisions

This ADR does not decide:
- the final container image layout for every assignment type
- the exact orchestrator or autoscaling control plane
- whether execution hosts run on Kubernetes, Nomad, plain VMs, or another host scheduler
- when multi-language execution will be added beyond preserving the seam
