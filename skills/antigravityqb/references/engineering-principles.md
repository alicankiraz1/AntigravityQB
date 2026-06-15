# AntigravityQB Engineering Principles

AntigravityQB should adapt established software engineering and computer science principles to the project context without cargo-culting them.

## Architecture and Design

Use when relevant:

- separation of concerns;
- information hiding and clear interfaces;
- cohesion and low coupling;
- domain-driven design language and bounded contexts;
- ports/adapters or hexagonal boundaries for external systems;
- dependency inversion where it reduces coupling;
- simple data lifecycle and state machine modeling;
- idempotency and retry safety for distributed or agentic workflows;
- explicit invariants and failure modes.

## Delivery and Validation

Use when relevant:

- test-driven or test-first slices;
- characterization tests for legacy code;
- property-based tests for invariants;
- contract tests for adapters and APIs;
- smoke tests for runtime boundaries;
- regression gates before refactors;
- observability and evidence artifacts.

## Secure Engineering

Plans should include secure-by-design expectations where relevant:

- least privilege;
- input validation and output encoding;
- safe command execution;
- path traversal protection;
- dependency and supply-chain awareness;
- secret redaction and secret-free artifacts;
- approval gates for destructive or external mutations;
- threat modeling for high-risk surfaces;
- audit logging and rollback paths.

## Planning Rule

Apply these principles selectively. The plan should explain why a principle matters for the project instead of listing generic best practices.
