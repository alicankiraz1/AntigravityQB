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

```markdown
# Planing Ledger

## 1. Purpose
## 2. Planning Runs
## 3. Implementation Runs
## 4. Current State Snapshot
## 5. Replanning Inputs
## 6. Open Decisions and Follow-Ups
```

## Update Rules

- Step 1 and Step 1.5 should read the ledger when it exists.
- Step 2 should read the ledger when it exists and carry relevant implementation history into sub-plans.
- Step 4 should append a concise implementation summary after each verified slice or stop event.
- Do not store secrets, tokens, credentials, private paths, or large logs.
- Store concise links or file paths to evidence instead of dumping full output.

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
