# Changelog

## 0.2.1

- Added Step 3 preflight validation and made Step 3 require `Planner-docs/Sub-Planing-Audit.md`.
- Added semantic Step 4 readiness parsing, NO_ACTION_REQUIRED support, finding status semantics, unsafe path rejection, and Ledger v2 strict execution checks.
- Added schema/version contracts: `artifact_schema_version: 2` and `handoff_contract_version: 1`.
- Moved Antigravity task handoff text into canonical `references/handoffs/run-step2.md`, `run-step3.md`, and `run-step4.md` files.
- Strengthened optional `Project-Comprehension.md` validation with minimum content checks, explicit markers, claim classes, and evidence requirements.
- Added deterministic fixture corpus checks for future skill-eval inputs.
- Added `references/probe-policy.md` for static, local, stateful, and external/live probe boundaries.
- Documented 0.2.0 artifact compatibility and Ledger v1 migration behavior.

## 0.2.0

- Added evidence-backed project comprehension, optional ontology, planning ledger guidance, and fixture corpus inputs.
- Hardened repo validation, package hygiene, secret scanning, and installed skill parity workflows.

## 0.1.0

- Initial Antigravity-native planning workflow with repo-aware intake, Step 1.5 Autopsy, ontology support, validator, installer, and gated Step 4 handoff.
