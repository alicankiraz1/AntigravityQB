---
contract_version: 1
---

# Step 2 Antigravity Task Handoff

Use the antigravityqb skill. Run Step 2 according to `references/Second-Planner.md`.

Antigravity Task Contract:
- Outcome: decompose every main phase into implementation-ready sub-plans.
- Inputs: `Planner-docs/Main-Planing.md` plus optional `Autopsy.md`, `Project-Ontology.md`, `Project-Comprehension.md`, and `Planing-Ledger.md`.
- Boundaries: modify only `Planner-docs/`; do not implement product code or edit `Planner-docs/Main-Planing.md`.
- Source precedence: user-confirmed intent and `Main-Planing.md` first; current repository evidence second; optional continuity artifacts third. Tentative comprehension claims require validation work before becoming implementation facts.
- Validation gates: run the bundled Step 2 validator or equivalent all-file validation.
- Stop gates: missing, inconsistent, incomplete, or undecomposable `Main-Planing.md`; unrelated dirty worktree only if it blocks safe planning.
- Context budget: read support artifacts fully once, then navigate by CQ, TRACE, ARC, ledger, and index references.
- Helper agent policy: use helper agents only for large repo exploration or phase drafting; parent writes final artifacts.

Resume / Recovery Protocol:
1. Re-read this canonical Antigravity Task Contract.
2. Read current git status and branch.
3. Re-read `Main-Planing.md`, optional autopsy, ontology, comprehension, ledger, and any existing index/sub-plans.
4. Reconcile ledger state with repository evidence before writing.
5. Do not repeat a verified slice or duplicate an existing sub-plan.
6. If the active plan snapshot changed, stop and request or perform replanning.

Read all main phases in `Planner-docs/Main-Planing.md`. If `Planner-docs/Autopsy.md`, `Planner-docs/Project-Ontology.md`, `Planner-docs/Project-Comprehension.md`, or `Planner-docs/Planing-Ledger.md` exists, read it fully as supporting evidence and account for it in the sub-phase plans. Plan in a vibecoding-first style: small reversible slices, fast validation signals, explicit deferrals, security boundaries, evidence confidence, CQ/TRACE/ARC references, and Antigravity task readiness. For each phase, create `Faz-<n>-Plans` folders and detailed `Faz<n>.<m>-*.md` sub-plan files under `Planner-docs`. Do not stop until all phases are covered. Modify only `Planner-docs`.
