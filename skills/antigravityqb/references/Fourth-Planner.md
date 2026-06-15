# Step 4 Implementation Handoff Prompt Template

This reference is not an auto-executed AntigravityQB planning step.

Use it only after Step 3 writes `Planner-docs/Sub-Planing-Audit.md` and the audit says Step 4 can begin. Print the copy block below for the user to paste into an Antigravity task.

If the audit status is `BLOCKED`, do not print this prompt. Print the minimal unblock prompt from the audit instead.

If the audit status is `PASS_WITH_WARNINGS` and any P0/P1 finding exists, do not print this prompt. Print a repair prompt targeting those P0/P1 findings first.

If the audit status is `PASS_WITH_WARNINGS` with only P2/P3 findings, this prompt may be printed, but state that the implementation run must keep those warnings visible.

## Copy Block

```text
Treat Planner-docs/Main-Planing.md, Planner-docs/Sub-Planing-Index.md, Planner-docs/Sub-Planing-Audit.md, and Planner-docs/Faz-*-Plans/*.md as source material. Build an ordered implementation queue from the audit's READY and READY_WITH_WARNINGS rows, preserving the index order. If the audit contains P0/P1 findings, stop before implementation and propose a repair prompt.

If installed/available in Antigravity, use relevant skills, project rules, and security review guidance by scope. If no supporting skill is installed, do not stop; continue using the audit, the active sub-plan, repo instructions, and existing validation commands with the same principles. Use GitHub publish/PR workflows only when explicitly requested.

Execute the queue continuously in this Antigravity task. For each implementation slice:
1. Name the active phase/sub-plan and the specific acceptance criterion being targeted.
2. Read AGENTS.md, README.md, Makefile, repo instructions, the audit, the index, and only the active sub-plan plus required repo files.
3. Run git status and stop if unrelated dirty changes or conflicts exist.
4. Inspect relevant files before editing.
5. Prefer adding or adjusting a focused failing test first when practical.
6. Implement the smallest change that can satisfy the selected acceptance criterion.
7. Run targeted validation first.
8. Run the repo-level gate when targeted validation passes.
9. Summarize:
   - files changed;
   - acceptance criterion addressed;
   - tests/commands run;
   - evidence produced;
   - remaining risks.
10. Continue to the next acceptance criterion or the next READY/READY_WITH_WARNINGS sub-plan instead of stopping.

Stop only when one of these stop gates is hit: P0/P1 or safety/security finding; failing test or unresolved regression; missing required source file; unclear contradiction between plan, audit, and repo reality; credential/live-environment/human-approval requirement; destructive external mutation requirement; unrelated dirty worktree or merge conflict; validation command unavailable with no equivalent fallback; scope would exceed the selected sub-plan; token/context budget too low to continue safely; or the user explicitly asks to stop. When stopping, write a concise handoff summary with completed slices, changed files, verification commands, blocker text, and the next queue item.

Do not write secrets, tokens, private keys, or local credentials. Watch token use: do not load every sub-plan into context; use the index/audit to navigate, read only the active sub-plan, and refresh queue status from the audit/index between slices. If context compaction or budget pressure is likely, summarize progress and continue only when the next slice can still be executed safely.
```

## Operator Notes

- Keep each implementation slice small and reversible, but continue through the ordered queue after each verified slice.
- Do not load every sub-plan into context unless the active slice requires cross-plan repair.
- Prefer existing repo validation commands over invented commands.
- Report exact blocker strings and separate code-delivery status from external config or credential blockers.
- Do not commit, push, open a PR, deploy, or mutate external systems unless the user explicitly asks in the Step 4 run.
