---
contract_version: 1
---

# Step 3 Antigravity Task Handoff

Use the antigravityqb skill. Run Step 3 according to `references/Third-Planner.md`.

Antigravity Task Contract:
- Outcome: audit every generated sub-plan and decide whether Step 4 can begin.
- Inputs: `Main-Planing`, `Sub-Planing-Index`, `Faz` plans, optional `Autopsy`, `Project-Ontology`, `Project-Comprehension`, and `Planing-Ledger` files.
- Boundaries: modify only `Planner-docs/Sub-Planing-Audit.md`.
- Source precedence: `Main-Planing` and validator findings first; support artifacts as evidence, with tentative comprehension claims audited before use.
- Validation gates: run the bundled Step 3 preflight and post-audit validators or equivalent all-file validation.
- Stop gates: missing `Main-Planing`, missing `Sub-Planing-Index`, or no sub-plan files.
- Context budget: inspect all plan files structurally, then quote only concise evidence.
- Helper agent policy: use helper agents only for broad coverage/readiness/security review; parent writes the audit.

Resume / Recovery Protocol:
1. Re-read this canonical Antigravity Task Contract.
2. Read current git status and branch.
3. Re-read the active audit if present, ledger, plan snapshot, index, and all selected sub-plans.
4. Reconcile ledger state with repository evidence before deciding readiness.
5. Do not repeat a verified slice or mark completed work READY again.
6. If the active plan snapshot changed, stop and request or perform replanning.

Audit `Planner-docs/Main-Planing.md`, `Planner-docs/Sub-Planing-Index.md`, `Planner-docs/Faz-*-Plans/*.md`, and any supporting `Planner-docs/Autopsy.md`, `Planner-docs/Project-Ontology.md`, `Planner-docs/Project-Comprehension.md`, or `Planner-docs/Planing-Ledger.md`. Analyze main-phase coverage, file naming, sequencing, required section structure, index consistency, content quality, scope drift, readiness realism, evidence quality, confidence calibration, trace coverage, architecture drift coverage, competency-question coverage, open-hypothesis probes, ontology consistency, planning-history continuity, security/governance, vibecoding slice quality, and Step 4 readiness. Do not fix any plan files; produce only `Planner-docs/Sub-Planing-Audit.md`. Do not stop until all phases and sub-plans have been reviewed.
