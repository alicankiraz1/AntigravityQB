# AntigravityQB Probe Policy

Use probes to resolve evidence gaps without turning planning into uncontrolled experimentation.

## Tier 0: Static Local Probe

Read-only file inspection, manifest parsing, git history inspection, and local documentation review.

- Approval: not required.
- Timeout: keep commands short and bounded.
- Cleanup: none expected.
- Evidence artifact: concise path, line, or command summary.

## Tier 1: Bounded Local Probe

Local tests, linters, type checks, dry-run commands, or small scripts that do not mutate durable project state.

- Approval: not required when the repository already defines the command.
- Timeout: use a clear timeout when the command could hang.
- Cleanup: remove temporary files in `/tmp` or the repo's existing temp area.
- Evidence artifact: command, exit status, and concise relevant output.

## Tier 2: Stateful Local Probe

Commands that create local databases, containers, generated artifacts, caches, migrations, or other durable state.

- Approval: get explicit user approval when state creation is non-trivial or cleanup is uncertain.
- Timeout: define the timeout before starting.
- Cleanup: document cleanup commands and remove generated temporary state when practical.
- Evidence artifact: artifact path, command, exit status, cleanup status, and remaining local state.

## Tier 3: External / Live Probe

Network calls, live services, cloud resources, paid APIs, production-like infrastructure, deployments, or external mutations.

- Approval: explicit user approval is required.
- Timeout: define a bounded timeout and stop condition.
- Cleanup: document rollback or cleanup steps before mutation.
- Evidence artifact: never include secrets; record endpoint class, command summary, status, and redacted evidence only.

## General Rules

- Prefer the lowest tier that can answer the question.
- Do not print secrets, tokens, credentials, private keys, or local environment values.
- Use bundled validators and file-name-only discovery for sensitive scans.
- If a probe contradicts the plan, record the contradiction and next probe instead of silently promoting a claim.
