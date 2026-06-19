# AntigravityQB Planning Ledger

AntigravityQB uses `Planner-docs/Planing-Ledger.md` as an optional durable memory artifact for planning and implementation history.

The spelling `Planing` is intentionally preserved to match the existing AntigravityQB artifact naming convention.

## Purpose

The ledger answers:

- What planning runs were completed?
- Which plans were implemented?
- What did each implementation run change?
- Which validation commands passed or failed?
- What is the latest known project state?
- What should future replanning read before creating new phases?

## Recommended File

```text
Planner-docs/Planing-Ledger.md
```

## Recommended Headings

Ledger v2 is the default structure for new files:

```markdown
# Planing Ledger

## 1. Purpose
## 2. Planning Runs
## 3. Plan Snapshot Registry
## 4. Sub-Plan Status Matrix
## 5. Implementation Runs
## 6. Current State Snapshot
## 7. Replanning Inputs
## 8. Open Decisions and Follow-Ups
```

Existing legacy v1 ledgers with the older six-section structure remain valid for compatibility. Non-strict validation accepts legacy v1 with a deprecation warning. Strict Step 4 execution requires migration to Ledger v2 before implementation starts.

## Update Rules

- Step 1 and Step 1.5 should read the ledger when it exists.
- Step 2 should read the ledger when it exists and carry relevant implementation history into sub-plans.
- Step 4 should append a concise implementation summary after each verified slice or stop event.
- Step 4 should record when a `Project-Comprehension.md` hypothesis is confirmed or contradicted, with concise evidence.
- Do not store secrets, tokens, credentials, private paths, or large logs.
- Store concise links or file paths to evidence instead of dumping full output.

## Plan Snapshot Registry

Use this section to map major planning artifacts to their current status and evidence.

```markdown
| Artifact | Status | Source evidence | Notes |
|---|---|---|---|
```

## Sub-Plan Status Matrix

Allowed status values are `planned`, `ready`, `ready_with_warnings`, `in_progress`, `implemented`, `verified`, `blocked`, and `superseded`.

Use the Ledger v2 table shape:

```markdown
| Sub-plan Path | Status | Snapshot ID | Run ID | Validation Evidence | Blocker | Next Action | Superseded By | Updated At |
|---|---|---|---|---|---|---|---|---|
```

Status semantics:

- `planned`: no execution run exists yet.
- `ready`: audit says the slice is executable.
- `ready_with_warnings`: only open/accepted P2/P3 or accepted risks remain.
- `in_progress`: Run ID is required. Next Action alone is not enough evidence.
- `implemented`: targeted validation evidence is required; final acceptance/repo gate may still be pending.
- `verified`: acceptance criteria and required repo gates passed; Validation Evidence is required.
- `blocked`: Blocker and Next Action are required.
- `superseded`: Superseded By is required.

Sub-plan Path must be repo-relative, must not contain `..`, must not be absolute, and should use this shape:

```text
Planner-docs/Faz-<n>-Plans/Faz<n>.<m>-<slug>.md
```

Do not keep two active rows for the same sub-plan with conflicting statuses.

## Step 4 Implementation Run Summary

Each Step 4 summary entry should include:

```markdown
### <date/time or run label> — <short run title>

- Source plan(s): <sub-plan paths>
- Slice(s) completed: <brief list>
- Files changed: <paths>
- Validation run: <commands and status>
- Evidence/artifacts: <paths or summaries>
- Remaining blockers: <none or concise blockers>
- Next recommended slice: <next queue item>
```

## Replanning Use

When a user reruns AntigravityQB for follow-up development, the agent should read the ledger before asking intake questions when possible. The agent should use the ledger as evidence, not as an unquestioned source of truth. Repository state, tests, and current user intent still win when they conflict with old ledger entries.
