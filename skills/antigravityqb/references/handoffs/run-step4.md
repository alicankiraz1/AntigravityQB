---
contract_version: 1
---

# Step 4 Antigravity Task Handoff

Use this only after Step 3 writes `Planner-docs/Sub-Planing-Audit.md` and validation says implementation can begin.

Antigravity Task Contract:
- Outcome: implement the ordered READY/READY_WITH_WARNINGS queue in small verified slices, or report NO_ACTION_REQUIRED without starting implementation.
- Inputs: `Main-Planing`, `Sub-Planing-Index`, `Sub-Planing-Audit`, active `Faz` sub-plan, optional `Autopsy`, `Project-Ontology`, `Project-Comprehension`, and `Planing-Ledger` evidence.
- Boundaries: change only files required by the active slice; do not batch unrelated sub-plans.
- Source precedence: repo instructions and current source first; audit/sub-plan second; comprehension and ontology as evidence. Tentative claims must be verified before code changes.
- Validation gates: targeted validation first, then repo-level gate.
- Stop gates: P0/P1 or safety finding, unclear contradiction, failing regression, missing source, credential/live approval, destructive mutation, unrelated dirty worktree, unavailable validation without fallback, scope overflow, token/context budget pressure, or user stop.
- Context budget: read only the active slice and the `Project-Comprehension.md` CQ/TRACE/ARC/HYP rows relevant to that slice.
- Helper agent policy: use helper agents only for non-trivial exploration, test-path discovery, implementation/review separation, or security review; max 3 helper agents per comprehension pass by default; no recursive spawning; read-only by default; parent writes artifacts; only one writer modifies files per slice.

Resume / Recovery Protocol:
1. Re-read this canonical Antigravity Task Contract.
2. Read current git status and branch.
3. Re-read the active audit, ledger, plan snapshot, and selected sub-plan.
4. Reconcile ledger state with repository evidence.
5. Do not repeat a verified slice.
6. If the active snapshot changed, stop and request or perform replanning.

Treat `Planner-docs/Main-Planing.md`, `Planner-docs/Sub-Planing-Index.md`, `Planner-docs/Sub-Planing-Audit.md`, `Planner-docs/Faz-*-Plans/*.md`, and any `Planner-docs/Autopsy.md`, `Planner-docs/Project-Ontology.md`, `Planner-docs/Project-Comprehension.md`, or `Planner-docs/Planing-Ledger.md` as source material. Build an ordered implementation queue from the audit's READY and READY_WITH_WARNINGS rows, preserving index order. If the audit says NO_ACTION_REQUIRED, do not start implementation; summarize why there is no queue. If the audit contains P0/P1 findings, stop before implementation and propose a repair prompt.

If installed/available in Antigravity, use relevant implementation, test-driven-development, verification, security, policy, secret-handling, or command-execution support by scope. If no supporting skill or helper agent is available, do not stop; continue using the audit, the active sub-plan, repo instructions, and existing validation commands with the same principles. Use GitHub publish/PR workflows only when explicitly requested. Use helper agents when they reduce context pollution or separate evidence gathering from implementation/review; do not use them for trivial single-file changes.

Default Antigravity task batch:
- one major phase;
- or at most 4 selected implementation slices;
- or a smaller explicit token/context budget.

The user may explicitly raise or lower the limit. Checkpoint after every completed slice instead of stopping after the first successful slice.

For each implementation slice:
1. Name the active phase/sub-plan and the specific acceptance criterion being targeted.
2. Read AGENTS.md, README.md, Makefile, repo instructions, the audit, the index, optional ontology/ledger files as needed, only the active sub-plan, and only the `Project-Comprehension.md` CQ/TRACE/ARC/HYP rows relevant to the active slice.
3. Run git status and stop if unrelated dirty changes or conflicts exist.
4. Inspect relevant files before editing.
5. Prefer adding or adjusting a focused failing test first when practical.
6. Verify tentative comprehension assumptions before code changes; then implement the smallest change that can satisfy the selected acceptance criterion.
7. Run targeted validation first.
8. If targeted validation fails and the source is unclear, stop and summarize the exact failure before editing more files.
9. Run the repo-level gate when targeted validation passes.
10. Do not batch unrelated sub-plans in one diff; continue to the next queue item only after the active slice is verified or blocked.
11. Append or update `Planner-docs/Planing-Ledger.md` with a concise implementation summary for the verified slice or stop event. If a `Project-Comprehension.md` hypothesis is confirmed or contradicted, record the hypothesis ID and evidence in the ledger. If the ledger does not exist, create it using the structure from AntigravityQB planning-ledger guidance.
12. Summarize:
   - files changed;
   - acceptance criterion addressed;
   - tests/commands run;
   - evidence produced;
   - remaining risks;
   - ledger entry added or updated.
13. Continue to the next acceptance criterion or the next READY/READY_WITH_WARNINGS sub-plan instead of stopping.

Stop only when one of these stop gates is hit: P0/P1 or safety/security finding; failing test or unresolved regression; missing required source file; unclear contradiction between plan, audit, and repo reality; credential/live-environment/human-approval requirement; destructive external mutation requirement; unrelated dirty worktree or merge conflict; validation command unavailable with no equivalent fallback; current plan snapshot no longer matches; next slice depends on a blocked slice; scope would exceed the selected sub-plan; token/context budget too low to continue safely; or the user explicitly asks to stop. When stopping, write a concise handoff summary with completed slices, changed files, verification commands, blocker text, and the next queue item.

Do not write secrets, tokens, private keys, or local credentials. Do not paste full logs into the ledger; store concise evidence paths or summaries. Watch token use: do not load every sub-plan into context; use the index/audit to navigate, read only the active sub-plan, and refresh queue status from the audit/index between slices. If context compaction or budget pressure is likely, summarize progress and continue only when the next slice can still be executed safely.
